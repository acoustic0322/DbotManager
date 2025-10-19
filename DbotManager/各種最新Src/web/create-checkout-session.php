<?php
require 'vendor/autoload.php';
//require 'C:/Users/winserverroot/vendor/autoload.php';

// 大輔本番用
\Stripe\Stripe::setApiKey('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'); // シークレットキー
// test用
//\Stripe\Stripe::setApiKey('sk_test_51REokc2KckKYw0LSL7yZtg5VZccdocrzto6thNvp1dEZkyY86BgC2Pw0iCpoKQV8cp2QpiKZGSDvc9Xtl1yVfvHI00yfvKYfmL'); // シークレットキー

ini_set('display_errors', 1);
ini_set('display_startup_errors', 1);
error_reporting(E_ALL);

header('Content-Type: application/json');

// JSONデータを受け取る
$data = json_decode(file_get_contents('php://input'), true);

// 値を取り出す
$count = $data['count'] ?? 0;
$tweet_id = $data['tweet_id'] ?? '';
$like = $data['like_enable'] ?? 0;
$bookmark = $data['bookmark_enable'] ?? 0;
$repost = $data['repost_enable'] ?? 0;
$profile = $data['profile_enable'] ?? 0;
$detail = $data['detail_enable'] ?? 0;

$actionCount = $like + $bookmark + $repost + $profile + $detail;
$finalCount = $count * $actionCount;

// 商品名の動的設定
$product_name = '';

// 判定順はリクエストの順番に応じて組み合わせる
if ($like) {
    $product_name = '👍';
}
if ($bookmark) {
    $product_name .= ($product_name ? '・' : '') . '📌';
}
if ($repost) {
    $product_name .= ($product_name ? '・' : '') . '🔁';
}
if ($profile) {
    $product_name .= ($product_name ? '・' : '') . '👤';
}
if ($detail) {
    $product_name .= ($product_name ? '・' : '') . 'ℹ️';
}


$product_name = $product_name . '(' . $count . '個)';

try {
    $session = \Stripe\Checkout\Session::create([
        'payment_method_types' => ['card'],
        'line_items' => [[
            'price_data' => [
                'currency' => 'jpy',
                'product_data' => [
                    'name' => $product_name,
                ],
                'unit_amount' => $finalCount, // ¥1,000 → 単位は「円」ではなく「最小通貨単位（=1円→1000 = 100000）」
//                'unit_amount' => 1000 * 100, // ¥1,000 → 単位は「円」ではなく「最小通貨単位（=1円→1000 = 100000）」
            ],
            'quantity' => 1,
        ]],
        'mode' => 'payment',
        'metadata' => [
            'tweet_id' => $tweet_id,
            'like' => $like,
            'bookmark' => $bookmark,
            'repost' => $repost,
            'profile' => $profile,
            'detail' => $detail,
            'count' => $count
            
        ],
        'success_url' => 'https://d-bot.happywinds.net/d-bot/tweet_japanese2.php?session_id={CHECKOUT_SESSION_ID}',        
        'cancel_url' => 'https://d-bot.happywinds.net/d-bot/tweet_japanese2.php',
    ]);

    echo json_encode(['id' => $session->id]);
} catch (\Throwable $e) {
    http_response_code(500);

    // ログファイルにエラー書き出し
    file_put_contents(__DIR__ . '/debug.log', "[Stripe Error] " . $e->getMessage() . "\n", FILE_APPEND);

    echo json_encode(['error' => $e->getMessage()]);
}
