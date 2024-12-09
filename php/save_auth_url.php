<?php
require __DIR__.'/_lib/config.php';
// save_auth_url.php

$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);


if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    try{
        $bearer_token = $_POST['bearer_token'];
        $id = $_POST['id'];
    
        // SQLを準備して実行
        $stmt = $conn->prepare("UPDATE account_master SET bearer_token = ? WHERE id = ?");
        $stmt->bind_param("si", $bearer_token , $id);
    
        if ($stmt->execute()) {
            /* 更新成功 */
        } else {
            /* 更新失敗 */
        }
    
        $stmt->close();
        $conn->close();
    } catch (PDOException $e) {
        http_response_code(500);
        echo 'Error: ' . $e->getMessage();
    }
} else {
    http_response_code(405); // メソッドが許可されていない
    echo 'Method Not Allowed';
}
