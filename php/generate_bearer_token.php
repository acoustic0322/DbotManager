<?php
require __DIR__.'/_lib/config.php';

// POSTデータを受け取る
// 必要なデータの取得
$api_key = $_POST['api_key'] ?? null;
$api_key_secret = $_POST['api_key_secret'] ?? null;

$credentials = base64_encode($api_key . ':' . $api_key_secret);
$url = 'https://api.twitter.com/oauth2/token';

$headers = [
'Authorization: Basic ' . $credentials,
'Content-Type: application/x-www-form-urlencoded;charset=UTF-8'
];

$options = [
'http' => [
'header' => implode("\r\n", $headers),
'method' => 'POST',
'content' => 'grant_type=client_credentials'
]
];

$context = stream_context_create($options);
$result = file_get_contents($url, false, $context);

$result = @file_get_contents($url, false, $context);
if ($result === false) {
    $error = error_get_last();
    echo 'エラーがa発生しました: ' . $error['message'];
    exit;
}

$data = json_decode($result);
$bearer_token = $data->access_token;

echo $bearer_token;

?>
