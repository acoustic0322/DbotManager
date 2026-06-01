const { ClientTransaction, handleXMigration } = require('@lami/x-client-transaction-id');

// 引数からパスとメソッドを取得（デフォルトはいいね用）
const path = process.argv[2] || '/i/api/graphql/lI07N6Otwv1PhnEgXILM7A/FavoriteTweet';
const method = process.argv[3] || 'POST';

async function generate() {
    try {
        // Twitterのホームページから必要なDOM情報を取得
        // ※ 初回のみネットワーク通信が発生するが、ライブラリ側でキャッシュなどの仕組みがあるかは不明
        // 実運用ではこのDOMを定期取得して渡すのが高速だが、まずはシンプルに実装
        const migrationData = await handleXMigration('https://x.com/home');

        const transaction = new ClientTransaction(migrationData);
        await transaction.initialize(); // 追加: 初期化呼び出し
        const tid = await transaction.generateTransactionId(method, path);

        console.log(tid);
    } catch (error) {
        console.error('Error generating TID:', error);
        process.exit(1);
    }
}

generate();
