<?php
require __DIR__.'/../_lib/config.php';
session_start();

$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if ($conn->connect_error) {
    die("接続エラー: " . $conn->connect_error);
}

if (isset($_GET['username'])) {
    $username = $_GET['username'];
    
    // 既存のユーザー名を確認
    $stmt = $conn->prepare("SELECT COUNT(*) FROM user_master WHERE username = ?");
    $stmt->bind_param("s", $username);
    $stmt->execute();
    $stmt->bind_result($count);
    $stmt->fetch();
    $stmt->close();
    
    // 結果を返す
    echo json_encode(['exists' => $count > 0]);
}

$conn->close();
?>
