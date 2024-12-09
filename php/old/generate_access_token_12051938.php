<?php
// 出力バッファリングを開始
ob_start();

require 'twitteroauth/vendor/autoload.php';
use Abraham\TwitterOAuth\TwitterOAuth;

// APIキーとシークレットキー
$api_key = '72Wzr0E71pUGiokxQZ0whs5Kf';
$api_key_secret = 'YovFtffCIhlWaHK2XtYrP2eb0y9FOSod9uCO0iCyXFYyd1B3Jc';

// コールバックURL
$callback_url = 'https://script.google.com/macros/s/AKfycbzVkmUti3NUc5T1MxSfX586zn8Iv4i1l-fMSlMb99gIl5Wlius5Sf-CkQP4zenPlpl_AQ/exec';

// デバッグ用ログ
error_log("アクセストークン生成処理開始");

// TwitterOAuthインスタンス作成
$connection = new TwitterOAuth($api_key, $api_key_secret);
error_log("TwitterOAuthインスタンス作成成功");

try {
    // リクエストトークンを取得
    error_log("リクエストトークンを取得中...");
    $request_token = $connection->oauth('oauth/request_token', ['oauth_callback' => $callback_url]);
    
    // セッション開始とトークン保存
    session_start();
    $_SESSION['oauth_token'] = $request_token['oauth_token'];
    $_SESSION['oauth_token_secret'] = $request_token['oauth_token_secret'];

    // 認証URLを取得してリダイレクト
    $url = $connection->url('oauth/authorize', ['oauth_token' => $request_token['oauth_token']]);
    error_log("認証URL取得成功: $url");

    // リダイレクト
    header("Location: $url");
    exit;
} catch (Exception $e) {
    // エラー処理
    echo "エラーが発生しました: " . $e->getMessage();
    error_log("エラーが発生しました: " . $e->getMessage());
}

// 出力バッファリング終了
ob_end_flush();
?>
