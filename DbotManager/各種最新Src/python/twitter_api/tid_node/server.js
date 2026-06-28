const http = require('http');
const url = require('url');
const { ClientTransaction } = require('@lami/x-client-transaction-id');
const { parseHTML } = require('linkedom');

const PORT = 3000;
const generators = new Map();
const initializationPromises = new Map();
const MAX_GENERATORS = 50;

function makeGeneratorKey(userAgent, secChUa, secChUaMobile, secChUaPlatform, cookieHeader, twid) {
    const authState = cookieHeader ? 'auth' : 'guest';
    const accountKey = twid || authState;
    return `${accountKey}|${userAgent || ''}|${secChUa || ''}|${secChUaMobile || ''}|${secChUaPlatform || ''}`;
}

async function fetchXDocument(userAgent, secChUa, secChUaMobile, secChUaPlatform, cookieHeader) {
    const ua = userAgent || "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/145.0.0.0 Safari/537.36";
    const uaLower = ua.toLowerCase();
    const isChrome = uaLower.includes("chrome");
    const isAndroid = uaLower.includes("android");
    const isMac = uaLower.includes("macintosh");
    const headers = {
        accept: "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "accept-language": "ja-JP,ja;q=0.9",
        "cache-control": "no-cache",
        pragma: "no-cache",
        priority: "u=0, i",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "none",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1",
        "user-agent": ua
    };
    if (isChrome) {
        headers["sec-ch-ua"] = secChUa || '"Not:A-Brand";v="99", "Google Chrome";v="145", "Chromium";v="145"';
        headers["sec-ch-ua-mobile"] = secChUaMobile || (isAndroid || uaLower.includes("mobile") ? "?1" : "?0");
        headers["sec-ch-ua-platform"] = secChUaPlatform || (isAndroid ? '"Android"' : (isMac ? '"macOS"' : '"Windows"'));
    }
    if (cookieHeader) {
        headers.cookie = cookieHeader;
    }
    const response = await fetch(cookieHeader ? "https://x.com/home" : "https://x.com", { headers });
    if (!response.ok) {
        throw new Error(`X homepage fetch failed: ${response.status} ${response.statusText}`);
    }
    const htmlText = await response.text();
    return parseHTML(htmlText).window.document;
}

// 初期化関数
async function initializeGenerator(userAgent, secChUa, secChUaMobile, secChUaPlatform, cookieHeader) {
    console.log('Fetching X migration data...');
    const migrationData = await fetchXDocument(userAgent, secChUa, secChUaMobile, secChUaPlatform, cookieHeader);
    const generator = new ClientTransaction(migrationData);
    await generator.initialize();
    console.log('TID Generator initialized successfully.');
    return generator;
}

async function getGenerator(userAgent, secChUa, secChUaMobile, secChUaPlatform, cookieHeader, twid) {
    const key = makeGeneratorKey(userAgent, secChUa, secChUaMobile, secChUaPlatform, cookieHeader, twid);
    if (generators.has(key)) {
        return generators.get(key);
    }

    if (!initializationPromises.has(key)) {
        const promise = initializeGenerator(userAgent, secChUa, secChUaMobile, secChUaPlatform, cookieHeader)
            .then((generator) => {
                generators.set(key, generator);
                if (generators.size > MAX_GENERATORS) {
                    const oldestKey = generators.keys().next().value;
                    generators.delete(oldestKey);
                }
                return generator;
            })
            .finally(() => {
                initializationPromises.delete(key);
            });
        initializationPromises.set(key, promise);
    }

    return initializationPromises.get(key);
}

// サーバー起動
const server = http.createServer(async (req, res) => {
    const parsedUrl = url.parse(req.url, true);

    if (req.method === 'GET' && parsedUrl.pathname === '/tid') {
        const path = parsedUrl.query.path;
        const method = parsedUrl.query.method || 'POST';
        const userAgent = parsedUrl.query.ua || '';
        const secChUa = parsedUrl.query.ch || '';
        const secChUaMobile = parsedUrl.query.mobile || '';
        const secChUaPlatform = parsedUrl.query.platform || '';
        const cookieHeader = req.headers["x-x-cookie"] || "";
        const twid = parsedUrl.query.twid || "";

        if (!path) {
            res.writeHead(400, { 'Content-Type': 'text/plain' });
            res.end('Missing path parameter');
            return;
        }

        try {
            const generator = await getGenerator(userAgent, secChUa, secChUaMobile, secChUaPlatform, cookieHeader, twid);
            const tid = await generator.generateTransactionId(method, path);
            res.writeHead(200, { 'Content-Type': 'text/plain' });
            res.end(tid);
        } catch (error) {
            console.error('TID Generation Error:', error && error.stack ? error.stack : error);
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
    getGenerator('', '', '', '').catch((error) => {
        console.error('Initial TID Generator warm-up failed:', error && error.stack ? error.stack : error);
    });
});




