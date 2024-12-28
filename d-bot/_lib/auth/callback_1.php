<?php 
use Abraham\TwitterOAuth\TwitterOAuth;

// 認証成功後のアクセストークン取得
$oauth_token = $_SESSION['oauth_token']??null;
$oauth_token_secret = $_SESSION['oauth_token_secret']??null;
$oauth_verifier = $_GET['oauth_verifier']??null;


if ($oauth_token && $oauth_token_secret && $oauth_verifier) {

}else{
    die("必要なデータが見つかりません。");
}

$local_user_id = $_GET['suid'] ?? null;
$signature = $_GET['sig'] ?? null;

// セッションからHMAC秘密鍵を取得
$hmac_secret_key = $_SESSION['hmac_secret_key'] ?? null;

// HMAC署名を検証
if ($hmac_secret_key && $local_user_id && $signature) {
    $expected_signature = hash_hmac('sha256', $local_user_id, $hmac_secret_key);

    if (!hash_equals($expected_signature, $signature)) {
        die("署名の検証に失敗しました。不正なリクエストです。");
    }
} else {
    die("必要なデータが見つかりません。");
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

$api_key = $edit_account['api_key'];
$api_key_secret = $edit_account['api_key_secret'];


$connection = new TwitterOAuth($api_key, $api_key_secret, $oauth_token, $oauth_token_secret);
$access_token_data = $connection->oauth("oauth/access_token", ["oauth_verifier" => $oauth_verifier]);


$access_token = $access_token_data['oauth_token']??'';
$access_token_secret = $access_token_data['oauth_token_secret']??'';


//var_dump($local_user_id);
//var_dump($access_token);
//var_dump($access_token_secret);


if (!$access_token || !$access_token_secret) {
    exit('Access token or refresh token is missing');
}

// データベース更新クエリ
//$stmt = $conn->prepare('UPDATE account_master SET access_token = ?, refresh_token = ? ,bearer_token = ?, access_token_secret = ? WHERE id = ?');
$stmt = $conn->prepare('UPDATE account_master SET access_token = ?, access_token_secret = ? WHERE id = ?');
if (!$stmt) {
    exit('Failed to prepare statement: ' . $conn->error);
}

//$stmt->bind_param('ssssi', $access_token, $refresh_token, $bearer_token, $access_token_secret, $edit_account['id']);
$stmt->bind_param('ssi', $access_token, $access_token_secret, $edit_account['id']);



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