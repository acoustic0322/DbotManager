<?php
require __DIR__ . '/_lib/config.php';
session_start();

header('Content-Type: application/json');

// JSONを受け取る
$raw = file_get_contents("php://input");
$data = json_decode($raw, true);

if (!isset($data['id'])) {
    echo json_encode(['success' => false, 'error' => 'ID not specified']);
    exit;
}

$id = (int)$data['id'];

// DB接続
$conn = new mysqli(
    $config['servername'],
    $config['username'],
    $config['password'],
    $config['dbname']
);

if ($conn->connect_error) {
    echo json_encode(['success' => false, 'error' => 'DB connection error']);
    exit;
}

// ソフトデリート実行
$stmt = $conn->prepare("UPDATE tweet_process_list SET hidden_flag = 1 WHERE id = ?");
$stmt->bind_param('i', $id);

if ($stmt->execute()) {
    echo json_encode(['success' => true]);
} else {
    echo json_encode(['success' => false, 'error' => 'SQL execution error']);
}

$stmt->close();
$conn->close();
