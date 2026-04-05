<?php
require __DIR__ . '/_lib/config.php';
session_start(); // セッションを開始する

// データベース接続
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

// セッションによるユーザー確認
if (!current_user($conn)) {
    echo "<p>ログインしていません。</p>";
    exit;
}

$current_userid = $_SESSION['user_id'];
$sensyuken_mode = $_SESSION['sensyuken_mode'];



$stmt = $conn->prepare("
SELECT 
  SUM(like_count) AS total_likes,
  SUM(bookmark_count) AS total_bookmarks,
  SUM(reply_count) AS total_replys
FROM tweet_process_list
WHERE user_id = ? 
  AND sensyuken_mode != 0 
  AND sensyuken_mode IS NOT NULL
  AND DATE(updatetime) = CURDATE()"
);

$stmt->bind_param("s", $current_userid);
$stmt->execute();

$result = $stmt->get_result();
$row = $result->fetch_assoc();
//$total_likes = $row['total_likes'];
//$total_bookmarks = $row['total_bookmarks'];
$total_likes = is_null($row['total_likes']) ? 0 : (int)$row['total_likes'];
$total_bookmarks = is_null($row['total_bookmarks']) ? 0 : (int)$row['total_bookmarks'];
$total_replys = is_null($row['total_replys']) ? 0 : (int)$row['total_replys'];
$exe_enable_like_count = $_SESSION['sensyuken_like_limit'] - $total_likes;
$exe_enable_bookmark_count = $_SESSION['sensyuken_bookmark_limit'] - $total_bookmarks;
$exe_enable_reply_count = $_SESSION['sensyuken_reply_limit'] - $total_replys;

//echo $current_userid ;
//echo $total_likes ;
//echo $total_bookmarks ;

$stmt->close();

// POSTリクエストの場合
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // 引数の準備
    $tweetId = isset($_POST['tweet_id']) ? $_POST['tweet_id'] : '';
    $like_count = isset($_POST['like_count']) ? (int)$_POST['like_count'] : 0;
    $bookmark_count = isset($_POST['bookmark_count']) ? (int)$_POST['bookmark_count'] : 0;
    $like_enable = isset($_POST['like_enable']) ? 1 : 0;
    $bookmark_enable = isset($_POST['bookmark_enable']) ? 1 : 0;

    // 超過チェック（サーバー側）
    if ($like_count > $exe_enable_like_count || $bookmark_count > $exe_enable_bookmark_count) {
        header("Location: " . $_SERVER['PHP_SELF'] . "?result=error_overlimit");
        exit;
    }

    $reply_count = 30;
    $reply_enable = 1;

    // reply制限チェック
    if ($exe_enable_reply_count <= 30) {
        $reply_count = $exe_enable_reply_count;
    }

    if ($exe_enable_reply_count == 0) {
        $reply_enable = 0;
    }    

    // INSERT文
    $sql = "INSERT INTO tweet_process_list (
    user_id, tweet_id, 
    updatetime, sensyuken_mode,
    like_count, bookmark_count, reply_count,
    like_enable, bookmark_enable, reply_enable
    ) 
    VALUES (
    ?, ?, NOW(), ?, ?, ?, ?, ?, ?, ?
    )";    

    // プリペアドステートメント
    $stmt = $conn->prepare($sql);

    // バインド（型指定修正）
//    $stmt->bind_param('isi', $current_userid, $tweetId, $sensyuken_mode);
    $stmt = $conn->prepare($sql);
    $stmt->bind_param(
        'isiiiiiii',
        $current_userid,
        $tweetId,
        $sensyuken_mode,
        $like_count,
        $bookmark_count,
        $reply_count,
        $like_enable,
        $bookmark_enable,
        $reply_enable
    );

    // 実行
    $stmt->execute();    
    $stmt->close();
    $conn->close();    

    // リダイレクト（PRGパターン）
    header("Location: " . $_SERVER['PHP_SELF']);
    exit;

}
?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>選手権</title>
    <meta name="format-detection" content="telephone=no">
    <link rel="stylesheet" href="./css/admin-dashboard.css" />
</head>
<body class="tweet-sensyuken-page">
<div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
  <div class="main">
    <div class="content" id="content">
        <h2>選手権<br></h2>
<form method="POST" action="?">

            <script>
                const maxLikeCount = <?php echo max(0, $exe_enable_like_count); ?>;
                const maxBookmarkCount = <?php echo max(0, $exe_enable_bookmark_count); ?>;
            </script> 

        <div class="input-group" style="text-align: left; padding: 10px 0;">
            <label style="display: block; margin-bottom: 20px;">
                <input type="text" name="tweet_id" id="tweet_id" placeholder="対象ツイートURL" required style="width: 100%; max-width: 500px; font-size: 20px; padding: 12px; box-sizing: border-box;">
            </label>

            <div style="font-size: 20px; line-height: 2.2;">
                <label style="display: block; margin-bottom: 15px;">
                    <input type="checkbox" name="like_enable" style="transform: scale(1.6); margin-right: 10px;" checked>
                    いいね（残り <span style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-weight: bold;"><?php echo max(0, $exe_enable_like_count);?></span> 回）
                </label>
                <input type="number" id="like_count" name="like_count" min="0" style="font-size: 20px; width: 100px; padding: 5px;">                
                
                <br>

                <label style="display: block; margin-bottom: 15px;">
                    <input type="checkbox" name="bookmark_enable" style="transform: scale(1.6); margin-right: 10px;" checked>
                    ブックマーク（残り <span style="color: #ffffff !important; -webkit-text-fill-color: #ffffff !important; font-weight: bold;"><?php echo max(0, $exe_enable_bookmark_count); ?></span> 回）
                </label>
                <input type="number" id="bookmark_count" name="bookmark_count" min="0" style="font-size: 20px; width: 100px; padding: 5px;">                
            </div>
        </div>

        <button type="submit" style="margin-top: 15px; padding: 5px 20px; font-size: 20px; font-weight: bold; cursor: pointer;">実行</button>

        <section
         id="execution-history"
         style="
         margin: 60px 0;
         width: 100%;
         font-size: 20px;
         line-height: 1.8;
         text-align: left;
         "
        >
          <h4 style="border-bottom: 2px solid #666; padding-bottom: 12px; margin-bottom: 30px; font-size: 24px;">実行履歴</h4>
          <ul id="history-list" style="list-style: none; padding: 0; margin: 0;">

          <?php
          $conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);
          $stmt = $conn->prepare(
              "SELECT id, tweet_id, like_count, bookmark_count, repost_count, updatetime
             FROM tweet_process_list
             WHERE user_id = ? and (japanese_mode != 1 or japanese_mode is null) AND hidden_flag = 0 
             ORDER BY updatetime DESC LIMIT 10"
          );

          $stmt->bind_param('i', $current_userid);
          $stmt->execute();
          $res = $stmt->get_result();
          while ($row = $res->fetch_assoc()) {
                $time = date('Y/m/d H:i', strtotime($row['updatetime']));
                $tweet_id_raw = $row['tweet_id'];
                if (preg_match('/status\/(\d{10,})/', $tweet_id_raw, $match)) {
                    $tweet_id_only = $match[1];
                } else {
                    $tweet_id_only = htmlspecialchars($tweet_id_raw);
                } 

               echo "<li style='margin-bottom: 35px; border-bottom: 1px solid #444; padding-bottom: 20px;'>";
               
               // 日付とボタンを左右に分ける設定
               echo "<div style='display: flex; justify-content: space-between; align-items: center;'>";
               
               // 左側：日付とアイコン
               echo "<div>";
               echo "<strong style='color: #fff; font-size: 22px;'>{$time}</strong>";
               if ($row['like_count']) echo " <span style='color: #fff; margin-left:15px;'>👍{$row['like_count']}</span>";
               if ($row['bookmark_count']) echo " <span style='color: #fff; margin-left:15px;'>📌{$row['bookmark_count']}</span>";
               if ($row['repost_count']) echo " <span style='color: #fff; margin-left:15px;'>🔁{$row['repost_count']}</span>";
               echo "</div>";

               // 右側：削除ボタン
               echo "<button class='hidden_tweet_process_list' data-id='{$row['id']}' style='padding: 10px 16px; font-size: 16px; cursor: pointer;'>削除</button>";
               
               echo "</div>"; 

               // 2行目：リンク
               echo "<div style='margin-top: 12px; font-size: 18px; opacity: 0.9;'>";
               echo "<a href='https://twitter.com/i/web/status/{$tweet_id_only}' target='_blank' style='color: #1DA1F2; text-decoration: underline;'>Tweet:{$tweet_id_only}</a>";
               echo "<span style='font-size: 14px; margin-left: 15px; color: #888;'>(ID:{$row['id']})</span>";
               echo "</div>";
               
               echo "</li>";
            }
          $stmt->close();
          $conn->close();
          ?>
          </ul>
        </section>
        
        </form>

    </div>
</div>

<script>
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const tweetIdInput = document.querySelector('input[name="tweet_id"]');

    form.addEventListener("submit", function (e) {
        const actions = [
            { check: 'like_enable', input: 'like_count', label: 'いいね数' },
            { check: 'bookmark_enable', input: 'bookmark_count', label: 'ブックマーク数' },
        ];

        let requireCheckBox = false;
        let requireTweetId = false;

        for (const { check, input, label } of actions) {
            const checkEl = document.querySelector(`input[name="${check}"]`);
            const inputEl = document.querySelector(`input[name="${input}"]`);
            const isChecked = checkEl?.checked;

            if (isChecked) {

                requireCheckBox = true;

                const value = parseInt(inputEl?.value || "0", 10);
                if (isNaN(value) || value <= 0) {
                    alert(`「${label}」を1以上で入力してください。`);
                    inputEl?.focus();
                    e.preventDefault();
                    return;
                }
                requireTweetId = true;
            }
        }

        if(requireCheckBox == false)
        {
            alert("いいね、ブックマークのチェックボックスがOFFです");
        }
        // tweet_idが必要なのに空ならエラー
        else if (requireTweetId && tweetIdInput?.value.trim() === "") {
            alert("対象ツイートIDを入力してください。");
            tweetIdInput.focus();
            e.preventDefault();
        }
      
    });
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