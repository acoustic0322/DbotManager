<?php 

$local_user_id = (string)$edit_account['id'];
$client_id = $edit_account['client_id'];

$authorization_endpoint = 'https://twitter.com/i/oauth2/authorize';

$scope = 'list.read list.write users.read offline.access tweet.read tweet.write like.read like.write tweet.moderate.write follows.read follows.write bookmark.read bookmark.write'; // 
// ランダムなCSRF用トークン生成

$hmac_secret_key = bin2hex(random_bytes(32));
$state_random = bin2hex(random_bytes(16));

// HMAC署名生成
$state_signature = hash_hmac('sha256', $local_user_id, $hmac_secret_key);

$state = $state_random . '-' . $local_user_id . '-' . $state_signature;

// PKCE用 code_verifier生成（A-Za-z0-9-._~が許容されていますが簡易的に16進文字列で生成します）
$code_verifier = bin2hex(random_bytes(32));

// code_challenge生成(SHA256ハッシュ→Base64URLエンコード)
$code_challenge = rtrim(strtr(base64_encode(hash('sha256', $code_verifier, true)), '+/', '-_'), '=');

// セッションに保存（コールバック時に取り出す）
$_SESSION['oauth_state'] = $state;
$_SESSION['code_verifier'] = $code_verifier;
$_SESSION['hmac_secret_key'] = $hmac_secret_key;

// 認可エンドポイントへリダイレクト
$params = [
    'response_type' => 'code',
    'client_id' => $client_id,
    'redirect_uri' => OAUTH_CALLBACK,
    'scope' => $scope,
    'state' => $state,
    'code_challenge' => $code_challenge,
    'code_challenge_method' => 'S256',
];
$authorize_url = $authorization_endpoint . '?' . http_build_query($params);

header('Location: ' . $authorize_url);
exit;
