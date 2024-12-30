<?php 

// トークン取得用のエンドポイントなど
$token_endpoint = 'https://api.twitter.com/2/oauth2/token';


// コールバックで受け取るデータ
$state = $_GET['state'] ?? null;
$authorization_code = $_GET['code'] ?? null;

// セッションから保存したデータを取得
$expected_state_random = $_SESSION['oauth_state'] ?? null;
$hmac_secret_key = $_SESSION['hmac_secret_key'] ?? null;

// コールバック時のGETパラメータ確認
if (!isset($state) || !isset($authorization_code)) {
    exit('Missing state or code parameter');
}

// state検証
if ($state !== $expected_state_random) {
    exit('Invalid state parameter');
}


if ($state && $expected_state_random && $hmac_secret_key) {
    [$state_random, $local_user_id, $received_signature] = explode('-', $state);

    // HMAC署名の検証
    $expected_signature = hash_hmac('sha256', $local_user_id, $hmac_secret_key);
    if (!hash_equals($expected_signature, $received_signature)) {
        die("不正なリクエスト: 署名が一致しません。");
    }
}else{
    exit('Invalid state parameter');
}

$edit_account = get_account($conn, $local_user_id);
if ($edit_account === null) {
    echo 'アカウントが存在しません';
    exit;
}

if ((string)$current_user['id'] !== (string)$edit_account['user_id']) {
    echo 'このアカウントの権限がありません';
    exit;
}

// code_verifierをセッションから取得
$code_verifier = $_SESSION['code_verifier'] ?? null;
if (!$code_verifier) {
    exit('No code_verifier in session');
}

#$client_id = $edit_account['client_id'];
#$client_secret = $edit_account['client_secret'];
$client_id = $edit_account['api_key'];
$client_secret = $edit_account['api_key_secret'];


// トークンリクエスト用パラメータ
$post_fields = [
    'grant_type' => 'authorization_code',
    'code' => $authorization_code,
    'redirect_uri' => OAUTH_CALLBACK,
    'code_verifier' => $code_verifier,
];

$ch = curl_init($token_endpoint);
curl_setopt($ch, CURLOPT_RETURNTRANSFER, true);
curl_setopt($ch, CURLOPT_POST, true);
curl_setopt($ch, CURLOPT_POSTFIELDS, http_build_query($post_fields));
curl_setopt($ch, CURLOPT_HTTPHEADER, [
    'Content-Type: application/x-www-form-urlencoded',
    'Authorization: Basic ' . base64_encode($client_id . ':' . $client_secret),
]);

$response = curl_exec($ch);
$http_code = curl_getinfo($ch, CURLINFO_HTTP_CODE);
curl_close($ch);

if ($http_code !== 200) {
    exit('Failed to get access token: ' . htmlspecialchars($response));
}

// レスポンスJSONを解析
$data = json_decode($response, true);
$bearer_token = $data['access_token'] ?? null;
$refresh_token = $data['refresh_token'] ?? null;

//var_dump($local_user_id);
//var_dump($access_token);
//var_dump($access_token);

if (!$bearer_token || !$refresh_token) {
    exit('Access token or refresh token is missing');
}

// データベース更新クエリ
//$stmt = $conn->prepare('UPDATE account_master SET access_token = ?, refresh_token = ? ,bearer_token = ?, access_token_secret = ? WHERE id = ?');
$stmt = $conn->prepare('UPDATE account_master SET bearer_token = ?, refresh_token = ? , refresh_updatetime = NOW() WHERE id = ?');
if (!$stmt) {
    exit('Failed to prepare statement: ' . $conn->error);
}

//$stmt->bind_param('ssssi', $access_token, $refresh_token, $bearer_token, $access_token_secret, $edit_account['id']);
$stmt->bind_param('ssi', $bearer_token, $refresh_token, $edit_account['id']);

if ($stmt->execute()) {
    $stmt->close();
    $conn->close();
    
    // トークン更新成功時にリダイレクト
    header('Location: account_list.php');
    exit;
} else {

    echo 'トークンの更新に失敗しました: ' . $stmt->error;
    $stmt->close();
    $conn->close();
}