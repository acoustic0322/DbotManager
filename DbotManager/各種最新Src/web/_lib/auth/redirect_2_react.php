<?php 

$local_user_id = (string)$edit_account['id'];

//$client_id = $edit_account['client_id'];
//$client_id = "RHhia084WGNtbmplMFlNeVRuUTM6MTpjaQ";
//
//$client_id = $client_id_api;
$client_id = $edit_account['client_id_api1'];
$client_secret = $edit_account['client_secret_api1'];

// 空チェック
if (empty($client_id)) {
    // ここで止める
    // 必要に応じてメッセージ出す or ログ出す
    echo 'client_id が未設定です';
    exit;
}

//echo $client_id;
//exit;

// 業者のURL
//https://x.com/i/oauth2/authorize?response_type=code&client_id=MDdfcmJRUGlVbmpQRWx2ZkUyalY6MTpjaQ&redirect_uri=https://twikakusan.com/lib/x_con.php&code_challenge=enLl0X33GV4_RdVepFMd92UT0-zAcivCLZNbuaKv0d4&state=state&code_challenge_method=s256&scope=tweet.read+tweet.write+offline.access+users.read+like.read+like.write+bookmark.write+media.write
//https://twikakusan.com/lib/x_con.php?cust_id=16&author_id=1363468304370372708&guild_id=1323149314226393130&id=3

//https://x.com/i/flow/login?redirect_after_login=%2Fi%2Foauth2%2Fauthorize%3Fresponse_type%3Dcode%26client_id%3DS0o0T2dOU3ZESDByR0ZTcW9vcE86MTpjaQ%26redirect_uri%3Dhttps%253A%252F%252Fd-bot.happywinds.net%252Fd-bot%252Fcallback.php%26scope%3Dlist.read%2Blist.write%2Busers.read%2Boffline.access%2Btweet.read%2Btweet.write%2Blike.read%2Blike.write%2Btweet.moderate.write%2Bfollows.read%2Bfollows.write%2Bbookmark.read%2Bbookmark.write%26state%3Dd22fca1d926839c0809e3cbcd68fc9fd-1-cbd60161e971d857559c0fdff30731257e82e281470dc6cd3e744cfdb841dba7%26code_challenge%3DVH_V-IqFQAphpGdAd2AaadlOkVOhBRZwpfoR_0p0V4g%26code_challenge_method%3DS256

//$authorization_endpoint = 'https://twitter.com/i/oauth2/authorize';
$authorization_endpoint = 'https://x.com/i/oauth2/authorize';


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

$_SESSION['oauth_config'] = [
    'client_id' => $client_id,
    'client_secret' => $client_secret,
    'type' => 'react',
];

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
