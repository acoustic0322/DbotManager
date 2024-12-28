<?php

require __DIR__.'/_lib/config.php';

session_start();

// データベース接続
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    header("Location: login.php");
    exit();
}

?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>ユーザー設定</title>
    <link rel="stylesheet" type="text/css" href="./main.css">
</head>
<body>

    <?php require PARTS_DIR.'/sidebar.php'; ?>

    <!-- コンテンツエリア -->
    <div class="content" id="content">

    </div>
</body>
</html>
