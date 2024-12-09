<?php
require 'twitteroauth/vendor/autoload.php';
use Abraham\TwitterOAuth\TwitterOAuth;


// POSTデータを受け取る
// 必要なデータの取得
$api_key = $_POST['api_key'] ?? null;
$api_key_secret = $_POST['api_key_secret'] ?? null;

if (!$api_key || !$api_key_secret) {
    http_response_code(400);
    echo 'API KeyまたはAPI Key Secretが指定されていません。';
    exit;
}

// APIキーとシークレットキー
//$api_key = '72Wzr0E71pUGiokxQZ0whs5Kf';
//$api_key_secret = 'YovFtffCIhlWaHK2XtYrP2eb0y9FOSod9uCO0iCyXFYyd1B3Jc';

// コールバックURL
$callback_url = 'https://script.google.com/macros/s/AKfycbzVkmUti3NUc5T1MxSfX586zn8Iv4i1l-fMSlMb99gIl5Wlius5Sf-CkQP4zenPlpl_AQ/exec';

// TwitterOAuthインスタンス作成
$connection = new TwitterOAuth($api_key, $api_key_secret);

try {
    // リクエストトークンを取得
    $request_token = $connection->oauth('oauth/request_token', ['oauth_callback' => $callback_url]);
    
    // セッション開始とトークン保存
    session_start();
    $_SESSION['oauth_token'] = $request_token['oauth_token'];
    $_SESSION['oauth_token_secret'] = $request_token['oauth_token_secret'];

    // 認証URLを返す
    $url = $connection->url('oauth/authorize', ['oauth_token' => $request_token['oauth_token']]);
    echo $url;
} catch (Exception $e) {
    // エラー処理
    http_response_code(500);
    echo "エラーが発生しました: " . $e->getMessage();
}

?>
