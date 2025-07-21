<?php

require 'vendor/autoload.php';


use Stripe\Stripe;
use Stripe\Checkout\Session;

\Stripe\Stripe::setApiKey('sk_test_51REokc2KckKYw0LSL7yZtg5VZccdocrzto6thNvp1dEZkyY86BgC2Pw0iCpoKQV8cp2QpiKZGSDvc9Xtl1yVfvHI00yfvKYfmL'); // シークレットキー

require __DIR__ . '/_lib/config.php';
session_start(); // セッションを開始する

// データベース接続
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);


//echo $_SESSION['user_id'];

// セッションによるユーザー確認
//if (!current_user($conn)) {
//    echo "<p>ログインしていません。</p>";
//    exit;
//}

current_user($conn);
//echo $_SESSION['is_logged_in'];

//$current_userid = $_SESSION['user_id'];
//$sensyuken_mode = $_SESSION['sensyuken_mode'];

$session_id = $_GET['session_id'] ?? '';

if ($session_id) {
    try {
        $session = \Stripe\Checkout\Session::retrieve($session_id);
        $metadata = $session->metadata;
        $paid = true; // フラグを立てる

        /*
        echo "<h2>決済が完了しました</h2>";
        echo "<ul>";
        echo "<li>Tweet ID: " . htmlspecialchars($metadata->tweet_id ?? '未設定') . "</li>";
        echo "<li>Bookmark: " . ($metadata->bookmark ?? 0 ? '有効' : '無効') . "</li>";
        echo "<li>Reply: " . ($metadata->reply ?? 0 ? '有効' : '無効') . "</li>";
        echo "<li>Reply to Reply: " . ($metadata->rep_to_rep ?? 0 ? '有効' : '無効') . "</li>";
        echo "<li>Repost: " . ($metadata->repost ?? 0 ? '有効' : '無効') . "</li>";
        echo "</ul>";
        */

       // メタデータ取得してセッションに保存
       $_SESSION['tweet_id'] = $session->metadata->tweet_id ?? '';
       $_SESSION['like_enable'] = $session->metadata->like ?? 0;
       $_SESSION['bookmark_enable'] = $session->metadata->bookmark ?? 0;
       $_SESSION['repost_enable'] = $session->metadata->repost ?? 0;
       $_SESSION['count'] = $session->metadata->count ?? 0;

       $jap_like_count = ($_SESSION['like_enable'] == 1) ? $_SESSION['count'] : 0;
       $jap_bookmark_count = ($_SESSION['bookmark_enable'] == 1) ? $_SESSION['count'] : 0;
       $jap_repost_count = ($_SESSION['repost_enable'] == 1) ? $_SESSION['count'] : 0;


//       $_SESSION['rep_to_rep'] = $session->metadata->rep_to_rep ?? 0;
//       $_SESSION['repost_enable'] = $session->metadata->repost ?? 0;   
       

        // INSERT文
        $sql = "INSERT INTO tweet_process_list (
            user_id, tweet_id, like_enable, bookmark_enable, repost_enable, 
            updatetime , japanese_mode ,
            jap_like_count , jap_bookmark_count , jap_repost_count
        ) 
        VALUES (
            ?, ?, ?, ?, ?, 
            NOW() , ? ,
            ?, ?, ?
        )";    

/*
        // プリペアドステートメント
        $stmt = $conn->prepare($sql);

        // バインド（型指定修正）
        $stmt->bind_param('isiiiiii', 
        $current_userid,
        $_SESSION['tweet_id'],
        '1',
        $_SESSION['bookmark_enable'],
        $_SESSION['reply_enable'],
        $_SESSION['repost_enable'],
        $_SESSION['rep_to_rep'] ,
        '1'
        );

        // 実行
//        $stmt->execute();    
        $stmt->close();
        $conn->close();           
        */

    } catch (\Exception $e) {
        $paid = false; 
        echo "<p>Stripeセッションの取得に失敗しました: " . $e->getMessage() . "</p>";
    }
} else {
    $paid = false; 
//    echo "<h2>通常アクセス</h2>";
//    echo "<p>このページは Stripe 決済後でない通常表示です。</p>";
    // ここに通常アクセス時に表示するコンテンツを書く
}
?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>日本人いいね</title>
    <link rel="stylesheet" href="_lib/style.css">    
    <script src="https://js.stripe.com/v3/"></script>

</head>
<body>
<div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
  <div class="main">
    <!-- コンテンツエリア -->
    <div class="content" id="content">
<!--        <form action="?" method="post">  -->

        <img src="image/japanese_like.png" alt="ロゴ" width="45%"  height="40%">

        <!-- 特定商取引法に基づく表記 -->
<!--        <div style="margin: 40px auto; max-width: 800px; font-size: 14px; line-height: 1.6; border-top: 1px solid #ccc; padding-top: 20px;"> -->
        <div>
        <h3>商品説明</h3>
        <p>本サービスは、個人および法人のSNS運用を支援するWebアプリケーションを提供します。</p>
        <p>ユーザーは自身のSNS投稿URLを登録することで、当社が提供する「アカウント運用補助スクリプト」や「アルゴリズム解析ツール」を用い、SNS上での反応・表示最適化を図ることが可能です。</p>
        <p>決済後は5分以内付与されますが、時間がかかる場合もあります。</p>
        <p>24時間以内に付与されない場合はご連絡ください。</p>
        </div>


        <div style="margin: 40px auto; max-width: 800px; font-size: 14px; line-height: 1.6; border-top: 1px solid #ccc; padding-top: 20px;">
        </div>

        <?php if ($paid): ?>
        <div class="paid-label">✅ 決済が完了しました</div>
        <?php endif; ?>        

        <form method="POST" action="?">
        <!--
        <label for="user_id">ユーザーID: 
            <span id="user_id"><?php echo htmlspecialchars($current_userid); ?></span>
        </label><br><br>
        -->
        <div class="input-group" checkbox-group">

        <label>

        数量：
        <input type="number" name="count" id="count" placeholder="カウント"
            required size="20" maxlength="20" min="20" required 
            value="<?= htmlspecialchars($_SESSION['count'] ?? '', ENT_QUOTES) ?>"> 
        </label><br><br>

        <label>
        対象ツイートID：
        <input type="text" name="tweet_id" id="tweet_id" placeholder="対象ツイートID"
            required size="40" maxlength="40" required 
            value="<?= htmlspecialchars($_SESSION['tweet_id'] ?? '', ENT_QUOTES) ?>">
        </label><br><br>

        <?php if (empty($_SESSION['is_guest']) || $_SESSION['is_guest'] === false): ?>

        <label>
        <input type="checkbox" name="like_enable" value="1"
            <?= (!empty($_SESSION['like_enable'])) ? 'checked' : '' ?>>
        いいね
        </label><br>

        <label>
        <input type="checkbox" name="bookmark_enable" value="1"
            <?= (!empty($_SESSION['bookmark_enable'])) ? 'checked' : '' ?>>
        ブックマーク
        </label><br>

        <!--
        <label>
        <input type="checkbox" name="reply_enable" value="1"
            <?= (!empty($_SESSION['reply_enable'])) ? 'checked' : '' ?>>
        リプライ
        </label><br>
        -->

        <!--
        <input type="checkbox" name="rep_to_rep" value="1"
            <?= (!empty($_SESSION['rep_to_rep'])) ? 'checked' : '' ?>>
        (リプライへのリプライ)
        -->

        <label>
        <input type="checkbox" name="repost_enable" value="1"
            <?= (!empty($_SESSION['repost_enable'])) ? 'checked' : '' ?>>
        リポスト
        </label><br>
        <?php endif; ?>        

    </div>

    <button id="checkout-button" type="button">決済</button>
    </div>

<!-- 特定商取引法に基づく表記 -->
<div style="margin: 40px auto; max-width: 800px; font-size: 14px; line-height: 1.6; border-top: 1px solid #ccc; padding-top: 20px;">
    <h3>特定商取引法に基づく表記</h3>
    <p><strong>法人名：</strong> 合同会社 Aola</p>
    <p><strong>代表者：</strong> 橋倉 大輔</p>
    <p><strong>所在地：</strong> 熊本県玉名市月田2107-12</p>
    <p><strong>メールアドレス：</strong> <a href="mailto:aola101010@gmail.com">aola101010@gmail.com</a></p>
    <p><strong>サイトURL：</strong> <a href="https://d-bot.happywinds.net/d-bot/tweet_japanese.php" target="_blank">https://d-bot.happywinds.net/d-bot/tweet_japanese.php</a></p>
    <p><strong>販売価格：</strong> 各商品の紹介ページに記載された価格となります。</p>
    <p><strong>商品代金以外の必要料金：</strong> 特にございません。</p>
    <p><strong>お支払い方法およびお支払い時期：</strong> クレジットカード決済：ご注文時にお支払いが確定いたします。</p>
    <p><strong>商品の引渡時期：</strong> ご注文確認後、直ちに商品を発送いたします。（最大24時間以内）</p>
    <p><strong>返品・交換・キャンセルについて：</strong> 商品送信後の返品・交換・キャンセルは、基本的にお受けできません。ただし、商品に欠陥がある場合のみ交換を承りますので、その際はご連絡ください。</p>
    <p><strong>返品期限：</strong> 商品発送後24時間以内にご連絡ください。</p>
</div>
        </form>

<script>
//    const stripe = Stripe('pk_live_XXXXXXXXXXXXXXXXXXXXXXXX');
//    const stripe = Stripe('pk_live_XXXXXXXXXXXXXXXXXXXXXXXX');
//    const stripe = Stripe('pk_live_XXXXXXXXXXXXXXXXXXXXXXXX');
    const stripe = Stripe('pk_live_51RiDeMDwYR8Mx0oRHqvNwVlDliPi1rWq1hoIwFhhBID8cYpdwgnAh8fX6ETzPBDhZMcd9qPsBFlg9iWf8UTJ8oaP00LqivRJYX');


    
    document.getElementById('checkout-button').addEventListener('click', async function (event) {
        event.preventDefault();

                // ✅ ここでアラートを出す
    alert("決済処理を開始します。Stripeへ接続します…");


        const countValue = parseInt(document.getElementById('count').value, 10);
        const tweetId = document.getElementById('tweet_id').value.trim();
        const like = document.querySelector('input[name="like_enable"]')?.checked ? 1 : 0;
        const bookmark = document.querySelector('input[name="bookmark_enable"]')?.checked ? 1 : 0;
        const repost = document.querySelector('input[name="repost_enable"]')?.checked ? 1 : 0;

        if (isNaN(countValue) || countValue < 20) {
            alert("いいね数は最低20以上にしてください。");
            return;
        }

        if (!tweetId) {
            alert("対象ツイートIDを入力してください。");
            return;
        }


        fetch('create-checkout-session.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                count: countValue,
                tweet_id: tweetId,
                like_enable: like,
                bookmark_enable: bookmark,
                repost_enable: repost
            })
        })
        .then(async response => {
            const data = await response.json();
            console.log("Stripe response:", data);  // ← ここ追加！

            if (response.ok && data.id) {
                return stripe.redirectToCheckout({ sessionId: data.id });   
            } else {
                alert("Stripeセッションの作成に失敗しました。\n" + (data.error || "不明なエラー"));
            }
        })        
        .catch(error => {
            alert("決済処理中に通信エラーが発生しました。\n" + error);
            console.error("fetch通信エラー:", error);
        });
    });
</script>

        
    </div>

</body>
</html>
