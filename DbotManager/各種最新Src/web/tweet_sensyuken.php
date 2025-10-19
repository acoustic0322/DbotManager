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
    <link rel="stylesheet" href="./css/admin-dashboard.css" />
</head>
<body class="tweet-sensyuken-page">
<div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
  <div class="main">
    <!-- コンテンツエリア -->
    <div class="content" id="content">
        <h2>選手権</h2>
<!--        <label>本日の残り回数： <?php //echo ($exe_enable_count); ?> </label><br><br>-->
        <form method="POST" action="?">

            <!-- JS用にPHP変数を埋め込み -->
            <script>
                const maxLikeCount = <?php echo max(0, $exe_enable_like_count); ?>;
                const maxBookmarkCount = <?php echo max(0, $exe_enable_bookmark_count); ?>;
            </script> 

        <div class="input-group" checkbox-group">
            <label>
                <input type="text" name="tweet_id" id="tweet_id" placeholder="対象ツイートID" required size="80" maxlength="100" require>
                <br><br>
                <label><input type="checkbox" name="like_enable">いいね（残り <?php echo max(0, $exe_enable_like_count); ?> 回）</label>
                <input type="number" id="like_count" name="like_count" min="0" class="short">                
                <br><br>
                <label><input type="checkbox" name="bookmark_enable">ブックマーク（残り <?php echo max(0, $exe_enable_bookmark_count); ?> 回）</label>
                <input type="number" id="bookmark_count" name="bookmark_count" min="0" class="short">                


            </label><br><br>
        </div>

            <button type="submit">実行</button>

                <!-- バリデーションスクリプト -->
                <script>
                document.querySelector("form").addEventListener("submit", function(event) {
                    const likeEnable = document.querySelector("input[name='like_enable']").checked;
                    const likeCount = parseInt(document.querySelector("input[name='like_count']").value || "0", 10);
                    const bookmarkEnable = document.querySelector("input[name='bookmark_enable']").checked;
                    const bookmarkCount = parseInt(document.querySelector("input[name='bookmark_count']").value || "0", 10);

                    if (likeEnable && likeCount > maxLikeCount) {
                        alert("指定したいいね数が本日の残り回数を超えています（残り " + maxLikeCount + " 回）");
                        event.preventDefault();
                        return;
                    }

                    if (bookmarkEnable && bookmarkCount > maxBookmarkCount) {
                        alert("指定したブックマーク数が本日の残り回数を超えています（残り " + maxBookmarkCount + " 回）");
                        event.preventDefault();
                        return;
                    }
                });
                </script>


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
              "SELECT id, tweet_id, like_count, bookmark_count, repost_count, updatetime
             FROM tweet_process_list
             WHERE user_id = ? and (japanese_mode != 1 or japanese_mode is null) AND hidden_flag = 0 
             ORDER BY updatetime DESC LIMIT 30"
          );

          $stmt->bind_param('i', $current_userid);
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

              if ($row['like_count']) echo " , 👍:{$row['like_count']}";
              if ($row['bookmark_count']) echo " , 📌:{$row['bookmark_count']}";
              if ($row['repost_count']) echo " , 🔁:{$row['repost_count']}";
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
