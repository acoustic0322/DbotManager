<?php
require 'twitteroauth/vendor/autoload.php';
use Abraham\TwitterOAuth\TwitterOAuth;

// APIキーとシークレットキー
// テスト用の認証情報
$api_key = '72Wzr0E71pUGiokxQZ0whs5Kf';
$api_key_secret = 'YovFtffCIhlWaHK2XtYrP2eb0y9FOSod9uCO0iCyXFYyd1B3Jc';

// コールバックURL
$callback_url = 'http://localhost/callback.php'; // 実際の環境に合わせて変更

// TwitterOAuthインスタンス作成
$connection = new TwitterOAuth($api_key, $api_key_secret);

// リクエストトークンを取得
try {
    $request_token = $connection->oauth('oauth/request_token', ['oauth_callback' => $callback_url]);

    // セッションにトークンを保存
    session_start();
    $_SESSION['oauth_token'] = $request_token['oauth_token'];
    $_SESSION['oauth_token_secret'] = $request_token['oauth_token_secret'];

    // 認証URLを取得してリダイレクト
    $url = $connection->url('oauth/authorize', ['oauth_token' => $request_token['oauth_token']]);
    header("Location: $url");
    exit;
} catch (Exception $e) {
    echo "エラーが発生しました: " . $e->getMessage();
}
?>
