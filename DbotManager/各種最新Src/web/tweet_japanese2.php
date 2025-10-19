<?php
require 'vendor/autoload.php';
use Stripe\Stripe;
use Stripe\Checkout\Session;
require __DIR__ . '/_lib/config.php';
session_start();

// DB接続
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);
if ($conn->connect_error) {
    die('DB接続失敗: ' . $conn->connect_error);
}

// ログインユーザー確認
current_user($conn);
$userId = $_SESSION['user_id'];

// Stripeキー設定
Stripe::setApiKey('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');

// Post/Redirect/Get セッションID処理
$sessionId = $_GET['session_id'] ?? '';
$paid = false;
if ($sessionId) {
    try {
        if (empty($_SESSION['processed_session_id']) || $_SESSION['processed_session_id'] !== $sessionId) {
            $stripeSession = Session::retrieve($sessionId);
            $m = $stripeSession->metadata;
            $_SESSION['tweet_id']        = $m->tweet_id     ?? '';
            $_SESSION['like_enable']     = (int)($m->like   ?? 0);
            $_SESSION['bookmark_enable'] = (int)($m->bookmark ?? 0);
            $_SESSION['repost_enable']   = (int)($m->repost ?? 0);
            $_SESSION['profile_enable']   = (int)($m->profile ?? 0);
            $_SESSION['detail_enable']   = (int)($m->detail ?? 0);
            $_SESSION['count']           = (int)($m->count  ?? 0);
            $mode = 1;
            $likeCount     = $_SESSION['like_enable']     ? $_SESSION['count'] : 0;
            $bookmarkCount = $_SESSION['bookmark_enable'] ? $_SESSION['count'] : 0;
            $repostCount   = $_SESSION['repost_enable']   ? $_SESSION['count'] : 0;
            $profileCount   = $_SESSION['profile_enable']   ? $_SESSION['count'] : 0;
            $detailCount   = $_SESSION['detail_enable']   ? $_SESSION['count'] : 0;
            $sql = "INSERT INTO tweet_process_list
                        (user_id,tweet_id,like_enable,bookmark_enable,repost_enable,updatetime,japanese_mode,jap_like_count,jap_bookmark_count,jap_repost_count,jap_profile_count,jap_detail_count)
                    VALUES (?,?,?,?,?,NOW(),?,?,?,?,?,?)";
            $stmt = $conn->prepare($sql);
            $stmt->bind_param('isiiiiiiiii',
                $userId,
                $_SESSION['tweet_id'],
                $_SESSION['like_enable'],
                $_SESSION['bookmark_enable'],
                $_SESSION['repost_enable'],
                $mode,
                $likeCount,
                $bookmarkCount,
                $repostCount,
                $profileCount,
                $detailCount
            );
            $stmt->execute();
            $stmt->close();
            $_SESSION['processed_session_id'] = $sessionId;
            $paid = true;
        }
        $conn->close();
        header('Location: ' . strtok($_SERVER['REQUEST_URI'], '?'));
        exit;
    } catch (\Exception $e) {
        echo '<p>Stripeセッション取得エラー: ' . htmlspecialchars($e->getMessage(), ENT_QUOTES) . '</p>';
    }
} else {
    $conn->close();
}
?>

<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>日本人いいね</title>
  <link rel="stylesheet" href="_lib/style.css">
  <script src="https://js.stripe.com/v3/"></script>
  <style>
    /* CSS */
    .history-delete { margin-left:8px; color:#f00; cursor:pointer; border:none; background:none; }

    /* リンクを白くする */
    .line-link,
    .line-link:visited,
    .footer-links a,
    .footer-links a:visited,
    #history-list a {
    color: #fff !important;
    }

    /* 対象ツイートID用（テキスト）のサイズ設定 */
      .input-group input[type="text"] {
        width: 100%;        /* この100%を固定pxに変える */
        max-width: 600px;   /* ここを例えば300pxに */
        box-sizing: border-box;
        padding: 8px;
      }

      /* 数量入力（number）のサイズ設定 */
      .input-group input[type="number"] {
        width: 120px !important;  /* この横幅を変更 */
        margin-left: 0px !important;   /* ラベルとのスペース */
        padding: 4px 8px !important;
        display: inline-block;
     }

  </style>
</head>
<body>
  <div class="layout">
    <?php require PARTS_DIR . '/sidebar.php'; ?>
    <div class="main"><div class="content" id="content">

              <!-- 商品説明 -->
        <div style="margin: 5px auto; max-width: 800px; font-size: 14px; line-height: 1.6; border-top: 1px solid #ccc; padding-top: 5px;">
          <h3>商品説明</h3>
          <p>【サービス内容】</p>
          <p>ご自身のSNS投稿URLを登録すると、自動化スクリプトによる投稿パフォーマンス最適化処理が実行されます。<br>※本サービスはデジタルコンテンツとして提供されます。</p>
          <p>【ご利用開始】</p>
          <p>決済完了後5分以内に付与。技術的問題や外部要因で遅れる可能性があります。（最大24時間）<br>※24時間を超えて付与されない場合はLINE公式アカウントまでご連絡ください。</p>
          <p>【返金条件】</p>
          <p>上記期限内に権限が付与されない場合に限り、返金対応いたします。</p>
          <p>【お問い合わせ】</p>
          <p>お問い合わせは<a href="https://lin.ee/Tn8KPh8" target="_blank" rel="noopener" class="line-link">LINE公式アカウント</a>までお願いいたします。<br>※問い合わせの際は、X-DBOTユーザーID・ツイートID・実行数をお知らせください。</p>
        </div>

        <!-- フォーム -->
        <div style="margin: 40px auto; max-width: 800px; font-size: 14px; line-height: 1.6; border-top: 1px solid #ccc; padding-top: 8px;">
          <?php if ($paid): ?>
            <div class="paid-label">✅ 決済が完了しました</div>
          <?php endif; ?>
          <form method="POST" action="?">
            <div class="input-group">
        <!-- 遅延等をアナウンスする -->      
        <p class="input-note" id="tweet-id-note" style="color: red; margin: 0 0 20px;">
        使用可能※いいね復活してます。
        最高350いいねまで可能です
        ブクマは500まで可能です。
        お間違えにならぬようご注意ください
        </p>  

              <label>対象ツイートID：<input type="text" name="tweet_id" id="tweet_id" placeholder="対象ツイートID" required value="<?= htmlspecialchars($_SESSION['tweet_id'] ?? '', ENT_QUOTES) ?>"></label><br>
              <label>数量：<input type="number" name="count" id="count" placeholder="カウント" required min="20" value="<?= htmlspecialchars($_SESSION['count'] ?? '', ENT_QUOTES) ?>"></label>
              <div id="total-amount" style="margin:8px 0; font-size:14px;">上記数量の合計決済額: ¥0</div>
              <p>※カード決済は50円以上から可能です。</p>
              <?php if (empty($_SESSION['is_guest']) || $_SESSION['is_guest'] === false): ?>

               <!--  <label><input type="checkbox" name="like_enable" value="1" > 👍現在使用できません</label>  -->
              <label><input type="checkbox" name="like_enable" value="1" <?= (!empty($_SESSION['like_enable'])) ? 'checked' : '' ?>> 👍350いいねまで可能</label> 

              <label><input type="checkbox" name="bookmark_enable" value="1" <?= (!empty($_SESSION['bookmark_enable'])) ? 'checked' : '' ?>> 📌※10以上必須一回の実行500までが推奨</label>
                <label><input type="checkbox" name="repost_enable" value="1" <?= (!empty($_SESSION['repost_enable'])) ? 'checked' : '' ?>> 🔁※10以上必須一回の実行200まで</label>
                <label><input type="checkbox" name="profile_enable" value="1" > 👤(プロフ) ※100以上必須</label>
                <label><input type="checkbox" name="detail_enable" value="1" > ℹ️ (詳細)※100以上必須</label>
              <?php endif; ?>
            </div>
            <div style="margin:16px 0;"><label><input type="checkbox" id="terms-agree" required> 利用規約に同意する</label></div>
            <button id="checkout-button" type="button" style="padding:10px 20px; font-size:16px;">決済</button>
          </form>
        </div>

         <!-- 実行履歴 -->
        <section
         id="execution-history"
         style="
         margin: 40px auto;
         max-width: 800px;
         font-size: 14px;
         line-height: 0.1;
         padding-top: 0.5px;
         "
>
        <section id="execution-history">
          <h4>実行履歴</h4>
          <ul id="history-list">

          <?php
          // 履歴取得（ソフトデリート対応）
          $conn = new mysqli(
            $config['servername'],
            $config['username'],
            $config['password'],
            $config['dbname']
          );
          $stmt = $conn->prepare(
              "SELECT id, tweet_id, jap_like_count, jap_bookmark_count, jap_repost_count, jap_profile_count, jap_detail_count, updatetime
             FROM tweet_process_list
             WHERE user_id = ? AND japanese_mode = 1 AND hidden_flag = 0
             ORDER BY updatetime DESC LIMIT 30"
          );
          $stmt->bind_param('i', $userId);
          $stmt->execute();
          $res = $stmt->get_result();
          while ($row = $res->fetch_assoc()) {
                $time = date('Y/m/d H:i', strtotime($row['updatetime']));

                // tweet_idを抽出（数字だけ抽出、URL対応）
                $tweet_id_raw = $row['tweet_id'];
                if (preg_match('/status\/(\d{10,})/', $tweet_id_raw, $match)) {
                    $tweet_id_only = $match[1];
                } else {
                    $tweet_id_only = htmlspecialchars($tweet_id_raw);
                } 

          //    echo "<li>{$time} - <a href='https://twitter.com/i/web/status/{$row['tweet_id']}' target='_blank'>ID:{$row['tweet_id']}</a> , 数量:{$row['total_count']}";
//              echo "<li>{$time} - <a href='https://twitter.com/i/web/status/{$row['tweet_id']}' target='_blank'>TweetID:{$row['tweet_id']}</a> ID:{$row['id']} ";
               echo "<li><button class='hidden_tweet_process_list' data-id='{$row['id']}'>削除</button>";
               echo "{$time} - <a href='https://twitter.com/i/web/status/{$tweet_id_only}' target='_blank'>TweetID:{$tweet_id_only}</a> ID:{$row['id']}";

              if ($row['jap_like_count']) echo " , 👍:{$row['jap_like_count']}";
              if ($row['jap_bookmark_count']) echo " , 📌:{$row['jap_bookmark_count']}";
              if ($row['jap_repost_count']) echo " , 🔁:{$row['jap_repost_count']}";
              if ($row['jap_profile_count']) echo " , 👤:{$row['jap_profile_count']}";
              if ($row['jap_detail_count']) echo " , ℹ️:{$row['jap_detail_count']}";
              echo "</li>";
            }
          $stmt->close();
          $conn->close();
          ?>
          </ul>
        </section>

        <!-- フッター -->
        <div class="footer-links" style="margin:40px auto; max-width:800px; text-align:center; font-size:14px; line-height:1.6; border-top:1px solid #ccc; padding-top:20px;">
          <a href="https://d-bot.happywinds.net/d-bot/trade.html" target="_blank" rel="noopener">特定取引法に基づく表記</a> |
          <a href="https://d-bot.happywinds.net/d-bot/terms.html" target="_blank" rel="noopener">利用規約</a>
        </div>
      </div>
    </div>
  </div>

  <script>
    const stripe = Stripe('pk_live_51RiDeMDwYR8Mx0oRxKkysaNEXBPADi20AU3hVh7Irn83E6Afh4qjRaQHjHB7L1ukgBds8IEAz3GTvO3irzZVvrR100KQl73UBA');
    // 決済額計算
    function updateAmount() {
      const count = parseInt(document.getElementById('count').value, 10) || 0;
      const like = document.querySelector('input[name="like_enable"]')?.checked ? 1 : 0;
      const bookmark = document.querySelector('input[name="bookmark_enable"]')?.checked ? 1 : 0;
      const repost = document.querySelector('input[name="repost_enable"]')?.checked ? 1 : 0;
      const profile = document.querySelector('input[name="profile_enable"]')?.checked ? 1 : 0;
      const detail = document.querySelector('input[name="detail_enable"]')?.checked ? 1 : 0;
      document.getElementById('total-amount').innerText = '上記数量の合計決済額: ¥' + (count * (like + bookmark + repost + profile + detail));
    }
    document.getElementById('count').addEventListener('input', updateAmount);
    ['like_enable','bookmark_enable','repost_enable','profile_enable','detail_enable'].forEach(name => {
      const chk = document.querySelector(`input[name="${name}"]`);
      if (chk) chk.addEventListener('change', updateAmount);
    });
    updateAmount();

    // チェックアウト処理
    let locked = false;
    document.getElementById('checkout-button').addEventListener('click', async e => {
      e.preventDefault();
      if (locked) return;
      locked = true;
      if (!document.getElementById('terms-agree').checked) {
        alert('利用規約に同意してください');
        locked = false;
        return;
      }
      const tweetId = document.getElementById('tweet_id').value.trim();
      const countValue = parseInt(document.getElementById('count').value, 10);
      const profileEnable = document.querySelector('input[name="profile_enable"]')?.checked;
      const detailEnable = document.querySelector('input[name="detail_enable"]')?.checked;

      // 基本チェック
      if (!tweetId || isNaN(countValue)) {
        alert('対象ツイートIDを入力してください。');
        locked = false;
        return;
      }      

      // 条件分岐
      if (profileEnable || detailEnable) {
        if (countValue < 100) {
          alert('プロフィールクリック または 詳細クリック を選択した場合は100以上にしてください。');
          locked = false;
          return;
        }
      } else {
        if (countValue < 20) {
          alert('個数は20以上にしてください。');
          locked = false;
          return;
        }
      }

      const response = await fetch('create-checkout-session.php', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({ 
        tweet_id: tweetId,
        count: countValue, 
        like_enable: +document.querySelector('input[name="like_enable"]')?.checked, 
        bookmark_enable: +document.querySelector('input[name="bookmark_enable"]')?.checked, 
        repost_enable: +document.querySelector('input[name="repost_enable"]')?.checked ,
        profile_enable: +document.querySelector('input[name="profile_enable"]')?.checked, 
        detail_enable: +document.querySelector('input[name="detail_enable"]')?.checked 
        })
      });
      const data = await response.json();
      if (data.id) {
        stripe.redirectToCheckout({ sessionId: data.id });
      } else {
        alert('Stripeセッション作成失敗: ' + (data.error || '不明なエラー'));
        locked = false;
      }
    });

    // 履歴削除
    document.querySelectorAll('.hidden_tweet_process_list').forEach(btn => {
      btn.addEventListener('click', async () => {
        if (!confirm('この履歴を削除しますか？')) return;
        const id = btn.dataset.id;
        const res = await fetch('hidden_tweet_process_list.php', {
          method: 'POST',
          credentials: 'same-origin',
          headers: {'Content-Type':'application/json'},
          body: JSON.stringify({ id })
        });
        const json = await res.json();
        if (json.success) {
          btn.closest('li').remove();
        } else {
          alert('削除に失敗しました');
        }
        
      });
    });
  </script>
</body>
</html>

<?php
require __DIR__ . '/_lib/config.php';
if (session_status() === PHP_SESSION_NONE) {
    session_start();
}
// 2025.09.07 headerんお2重定義によりコメントアウト
// 最善の対応可は不明
//header('Content-Type: application/json');

// ログインチェック
if (empty($_SESSION['user_id'])) {
    echo json_encode(['success'=>false,'error'=>'ログインしてください']);
    exit;
}
// リクエストIDチェック
$input = json_decode(file_get_contents('php://input'), true);
$id = intval($input['id'] ?? 0);
if ($id <= 0) {
    echo json_encode(['success'=>false,'error'=>'無効なID']);
    exit;
}
// DB接続
$conn = new mysqli($config['servername'],$config['username'],$config['password'],$config['dbname']);
if ($conn->connect_error) {
    echo json_encode(['success'=>false,'error'=>'DB接続失敗']);
    exit;
}
// ソフトデリート: is_deleted フラグを立てる
$stmt = $conn->prepare('UPDATE tweet_process_list SET is_deleted=1 WHERE id=? AND user_id=?');
$stmt->bind_param('ii', $id, $_SESSION['user_id']);
$stmt->execute();
$success = ($stmt->affected_rows > 0);
$stmt->close();
$conn->close();

echo json_encode(['success'=>$success]);
?>
