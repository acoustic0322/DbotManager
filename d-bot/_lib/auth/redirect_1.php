<?php 
use Abraham\TwitterOAuth\TwitterOAuth;

$local_user_id = (string)$edit_account['id'];
$api_key = $edit_account['api_key'];
$api_key_secret = $edit_account['api_key_secret'];
$hmac_secret_key = bin2hex(random_bytes(32));

// HMAC署名を生成
$signature = hash_hmac('sha256', $local_user_id, $hmac_secret_key);

$signedData = http_build_query([
    'suid' => $local_user_id, // サイト側ユーザーID
    'sig'  => $signature   // HMAC署名
]);

// TwitterOAuthインスタンスを作成
$connection = new TwitterOAuth($api_key, $api_key_secret);

// リクエストトークンを取得
$requestToken = $connection->oauth('oauth/request_token', ['oauth_callback' => OAUTH_CALLBACK . '?' . $signedData]);

$_SESSION['oauth_token'] = $requestToken['oauth_token'];
$_SESSION['oauth_token_secret'] = $requestToken['oauth_token_secret'];
$_SESSION['hmac_secret_key'] = $hmac_secret_key;

$authorize_url = $connection->url('oauth/authorize', ['oauth_token' => $requestToken['oauth_token']]);

header('Location: ' . $authorize_url);
exit;