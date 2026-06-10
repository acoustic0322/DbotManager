const http = require('http');
const url = require('url');
const { ClientTransaction, handleXMigration } = require('@lami/x-client-transaction-id');

const PORT = 3000;
let transactionGenerator = null;

// 初期化関数
async function initializeGenerator() {
    try {
        console.log('Fetching X migration data...');
        // DOM情報を取得 (これに時間がかかるため、サーバー起動時に行う)
        const migrationData = await handleXMigration('https://x.com/home');
        transactionGenerator = new ClientTransaction(migrationData);
        await transactionGenerator.initialize();
        console.log('TID Generator initialized successfully.');
    } catch (error) {
        console.error('Failed to initialize TID Generator:', error);
        // 再試行ロジックなどが本来は必要
    }
}

// サーバー起動
const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);

    if (req.method === 'GET' && parsedUrl.pathname === '/tid') {
        const path = parsedUrl.query.path;
        const method = parsedUrl.query.method || 'POST';

        if (!path) {
            res.writeHead(400, { 'Content-Type': 'text/plain' });
            res.end('Missing path parameter');
            return;
        }

        if (!transactionGenerator) {
            // まだ初期化されていない、または失敗していた場合、再試行
            try {
                await initializeGenerator();
            } catch (e) {
                res.writeHead(503, { 'Content-Type': 'text/plain' });
                res.end('Generator not initialized');
                return;
            }
        }

        try {
            const tid = await transactionGenerator.generateTransactionId(method, path);
            res.writeHead(200, { 'Content-Type': 'text/plain' });
            res.end(tid);
        } catch (error) {
            console.error('TID Generation Error:', error);
            // 初期化切れの可能性もあるため、エラー時は再初期化を検討してもよい
            res.writeHead(500, { 'Content-Type': 'text/plain' });
            res.end('Error generating TID');
        }
    } else if (req.method === 'GET' && parsedUrl.pathname === '/status') {
        res.writeHead(200, { 'Content-Type': 'text/plain' });
        res.end('OK');
    } else {
        res.writeHead(404, { 'Content-Type': 'text/plain' });
        res.end('Not Found');
    }
});

// 起動と同時に初期化
server.listen(PORT, () => {
    console.log(`TID Server running at http://localhost:${PORT}`);
    initializeGenerator();
});
