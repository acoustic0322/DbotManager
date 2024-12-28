<?php
require __DIR__ . '/_lib/config.php';
use Abraham\TwitterOAuth\TwitterOAuth;

session_start(); // セッションを開始する


// データベース接続
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

// セッションによるユーザー確認
if (!current_user($conn)) {
    echo "<p>ログインしていません。</p>";
    exit;
}

$signature = $_GET['sig'] ?? null;

if ($signature != '') {
    require __DIR__.'/_lib/auth/callback_1.php';
    exit;
}

require __DIR__.'/_lib/auth/callback_2.php';