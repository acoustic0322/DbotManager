<?php
require_once __DIR__ . '/_lib/config.php';
session_start();

$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

$bulk_ids = $_POST['bulk_ids'] ?? '';
$xuser = $_POST['xuser'] ?? '';
$type = $_POST['type'] ?? 'm';

if ($bulk_ids === '') {
    die('削除対象がありません');
}

$id_list = array_filter(array_map('intval', explode(",", $bulk_ids)));

if (empty($id_list)) {
    die('削除IDが不正です');
}

$file_prefix = ($type == 'p') ? 'p' : 'm';
$file_type = ($type == 'p') ? 'photo' : 'movie';

// 物理ファイル削除
foreach ($id_list as $id) {
    $sql = "SELECT ext FROM media_master WHERE media_id = ? AND account_id = ?";
    $stmt = $conn->prepare($sql);
    $stmt->bind_param("ii", $id, $xuser);
    $stmt->execute();
    $res = $stmt->get_result()->fetch_assoc();
    $stmt->close();

    if ($res) {
        $file = UPLOAD_DIR . '/' . $xuser . '/' . $file_prefix . $id . '.' . $res['ext'];
        if (file_exists($file)) @unlink($file);
    }
}

// DB 削除
$in = implode(",", array_fill(0, count($id_list), "?"));
$types = str_repeat("i", count($id_list));

$sql = "DELETE FROM media_master WHERE media_id IN ($in)";
$stmt = $conn->prepare($sql);
$stmt->bind_param($types, ...$id_list);
$stmt->execute();
$stmt->close();

header("Location: upload.php?type=$type&xuser=$xuser");
exit;
