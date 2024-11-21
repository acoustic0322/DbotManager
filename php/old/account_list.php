<?php
require __DIR__.'/_lib/config.php';
session_start(); // セッションを開始する

// セッションにユーザー名がセットされているか確認
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    echo "<p>ログインしていません。</p>";
    exit; // ログインしていない場合はここで終了
}
?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>プロフィール設定</title>
    <link rel="stylesheet" type="text/css" href="./main.css">
</head>
<body>

    <?php require PARTS_DIR.'/sidebar.php'; ?>

    <!-- コンテンツエリア -->
    <div class="content" id="content">
       <h1>ようこそ、<?php htmlspecialchars($_SESSION['username']) ?>さん！</h1>
        <h2>プロフィール設定</h2>
        <p>ユーザー名: <?php echo htmlspecialchars($_SESSION['username']); ?></p>
        <p>ここでプロフィール情報の変更ができます。</p>
    </div>
</body>
</html>
