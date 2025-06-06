<?php
require 'vendor/autoload.php';
//require 'C:/Users/winserverroot/vendor/autoload.php';


\Stripe\Stripe::setApiKey('sk_test_51REokc2KckKYw0LSL7yZtg5VZccdocrzto6thNvp1dEZkyY86BgC2Pw0iCpoKQV8cp2QpiKZGSDvc9Xtl1yVfvHI00yfvKYfmL'); // シークレットキー

header('Content-Type: application/json');



// JSONデータを受け取る
$data = json_decode(file_get_contents('php://input'), true);

// 値を取り出す
$count = $data['count'] ?? 0;
$tweet_id = $data['tweet_id'] ?? '';
$bookmark = $data['bookmark_enable'] ?? 0;
$reply = $data['reply_enable'] ?? 0;
$rep_to_rep = $data['rep_to_rep'] ?? 0;
$repost = $data['repost_enable'] ?? 0;

try {
    $session = \Stripe\Checkout\Session::create([
        'payment_method_types' => ['card'],
        'line_items' => [[
            'price_data' => [
                'currency' => 'jpy',
                'product_data' => [
                    'name' => 'サンプル商品',
                ],
                'unit_amount' => $count, // ¥1,000 → 単位は「円」ではなく「最小通貨単位（=1円→1000 = 100000）」
//                'unit_amount' => 1000 * 100, // ¥1,000 → 単位は「円」ではなく「最小通貨単位（=1円→1000 = 100000）」
            ],
            'quantity' => 1,
        ]],
        'mode' => 'payment',
        'metadata' => [
            'tweet_id' => $tweet_id,
            'bookmark' => $bookmark,
            'reply' => $reply,
            'rep_to_rep' => $rep_to_rep,
            'repost' => $repost
        ],
        'success_url' => 'https://d-bot.happywinds.net/d-bot/tweet_japanese.php?session_id={CHECKOUT_SESSION_ID}',        
        'cancel_url' => 'https://d-bot.happywinds.net/d-bot/account_list.php',
    ]);

    echo json_encode(['id' => $session->id]);
} catch (Error $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
