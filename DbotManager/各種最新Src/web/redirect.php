<?php
require __DIR__ . '/_lib/config.php';

session_start(); // セッションを開始する

// データベース接続
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

// セッションによるユーザー確認
if (!current_user($conn)) {
    echo "<p>ログインしていません。</p>";
    exit;
}


// idの確認
$id = $_GET['id'] ?? null;

if (empty($id)) {
    echo 'IDを指定してください';
    exit;
}

$edit_account = get_account($conn, $id);
if ($edit_account === null) {
    echo 'アカウントが存在しません';
    exit;
}

if ((string)$current_user['id'] !== (string)$edit_account['user_id']) {
    echo 'このアカウントの権限がありません';
    exit;
}

$type = $_GET['type']??'';

if ($type == '2') {
    require __DIR__.'/_lib/auth/redirect_2.php';
    exit;
}
if ($type == '2_react') {
    $client_id_api = $edit_account['client_id_api1'];
    if (!empty($client_id_api)) {    
        require __DIR__.'/_lib/auth/redirect_2_react.php';
    }
    /*
    $client_id_api = $edit_account['client_id_api2'];
    if (!empty($client_id_api)) {    
        require __DIR__.'/_lib/auth/redirect_2_react.php';
    }
        */
    exit;
}
require __DIR__.'/_lib/auth/redirect_1.php';
