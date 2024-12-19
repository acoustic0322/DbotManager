<?php
require __DIR__.'/_lib/config.php';

// テスト用の認証情報
$api_key = '72Wzr0E71pUGiokxQZ0whs5Kf';
$api_key_secret = 'YovFtffCIhlWaHK2XtYrP2eb0y9FOSod9uCO0iCyXFYyd1B3Jc';

// TwitterOAuthオブジェクトの作成
$connection = new TwitterOAuth($api_key, $api_key_secret);

// リクエストトークンの取得
$request_token = $connection->oauth('oauth/request_token', ['oauth_callback' => 'oob']);

// 認証URLの取得と表示
$url = $connection->url('oauth/authorize', ['oauth_token' => $request_token['oauth_token']]);
echo "以下のURLにアクセスして認証コード（PIN）を取得してください:\n";
echo $url . PHP_EOL;

// ユーザーから認証コード（PIN）を取得
echo "認証コード（PIN）を入力してください: ";
$pin = trim(fgets(STDIN));

// アクセストークンの取得
$connection->setOauthToken($request_token['oauth_token'], $request_token['oauth_token_secret']);
$access_token = $connection->oauth('oauth/access_token', ['oauth_verifier' => $pin]);

// アクセストークンの表示
echo "アクセストークンの情報:\n";
echo "Token: " . $access_token['oauth_token'] . "\n";
echo "Token Secret: " . $access_token['oauth_token_secret'] . "\n";

// 必要であればアクセストークンを保存する処理を追加
file_put_contents('access_token.json', json_encode($access_token));
echo "アクセストークンを access_token.json に保存しました。\n";
