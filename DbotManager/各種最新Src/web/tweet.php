<?php
require __DIR__ . '/_lib/config.php';
session_start();

$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);
if (!current_user($conn)) {
    echo "<p>ログインしていません。</p>";
    exit;
}

$current_userid = $_SESSION['user_id'];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $tweetId = $_POST['tweet_id'] ?? '';
    $likeEnable = !empty($_POST['like_enable']) ? 1 : 0;
    $bookmarkEnable = !empty($_POST['bookmark_enable']) ? 1 : 0;
    $replyEnable = !empty($_POST['reply_enable']) ? 1 : 0;
    $repostEnable = !empty($_POST['repost_enable']) ? 1 : 0;
    $repToRep = !empty($_POST['rep_to_rep']) ? 1 : 0;

    $likeCount = intval($_POST['like_count'] ?? 0);
    $bookmarkCount = intval($_POST['bookmark_count'] ?? 0);
    $replyCount = intval($_POST['reply_count'] ?? 0);
    $repostCount = intval($_POST['repost_count'] ?? 0);

    $followEnable = !empty($_POST['follow_enable']) ? 1 : 0;
    $followAction = $_POST['follow_action'] ?? '';
    $targetAccountName = $_POST['follow_screen_name'] ?? '';

    $exeFollow = ($followEnable && $followAction === 'add') ? 1 : 0;
    $exeUnfollow = ($followEnable && $followAction === 'remove') ? 1 : 0;

    $sql = "INSERT INTO tweet_process_list (
        user_id, tweet_id, like_enable, bookmark_enable, reply_enable, repost_enable,
        like_count, bookmark_count, reply_count, repost_count, updatetime, rep_to_rep,
        exe_follow, exe_unfollow, target_account_name
    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW(), ?, ?, ?, ?)";

    $stmt = $conn->prepare($sql);
    $stmt->bind_param('isiiiiiiiiiiis', $current_userid, $tweetId, $likeEnable, $bookmarkEnable, $replyEnable, $repostEnable, $likeCount, $bookmarkCount, $replyCount, $repostCount, $repToRep, $exeFollow, $exeUnfollow, $targetAccountName);
    $stmt->execute();
    $stmt->close();
    $conn->close();
}
?>

<!DOCTYPE html>
<html lang="ja">
  <head>
    <meta charset="UTF-8" />
    <title>(自)いいね・ブクマ</title>
    <link rel="stylesheet" href="./css/admin-dashboard.css" />
    <link
      href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap"
      rel="stylesheet"
    />
  </head>
<body>
  <div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
    <div class="main">
    <!-- コンテンツエリア -->
    <div class="content" id="content">    
    <h2>(自)いいね・ブクマ</h2>
    <form method="POST">
        <label for="tweet_id">対象ツイートID</label>
        <input type="text" id="tweet_id" name="tweet_id">

        <div class="form-block">
            <label>実行機能</label>
            <label><input type="checkbox" name="like_enable">いいね</label>
            <label><input type="checkbox" name="bookmark_enable">ブックマーク</label>
            <label><input type="checkbox" name="reply_enable">リプライ</label>
            <label><input type="checkbox" name="repost_enable">リポスト</label>
            <label><input type="checkbox" name="rep_to_rep">リプライにリプライ</label>
        </div>

        <div class="form-block">
            <label for="like_count">いいね数</label>
            <input type="number" id="like_count" name="like_count" min="0" class="short">

            <label for="bookmark_count">ブックマーク数</label>
            <input type="number" id="bookmark_count" name="bookmark_count" min="0" class="short">

            <label for="reply_count">リプライ数</label>
            <input type="number" id="reply_count" name="reply_count" min="0" class="short">

            <label for="repost_count">リポスト数</label>
            <input type="number" id="repost_count" name="repost_count" min="0" class="short">
        </div>

        <div class="form-block">
            <label><input type="checkbox" name="follow_enable">フォロー操作</label>
            <label><input type="radio" name="follow_action" value="add" checked>フォロー</label>
            <label><input type="radio" name="follow_action" value="remove">アンフォロー</label>

            <label for="follow_screen_name">対象アカウント名 (@なし)</label>
            <input type="text" id="follow_screen_name" name="follow_screen_name">
        </div>

        <button type="submit" class="btn">登録する</button>
    </form>
      </div>
      </div>
      </div>

<script>
document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    const tweetIdInput = document.querySelector('input[name="tweet_id"]');
    const followCheckbox = document.querySelector('input[name="follow_enable"]');
    const followScreenNameInput = document.querySelector('input[name="follow_screen_name"]');

    form.addEventListener("submit", function (e) {
        const actions = [
            { check: 'like_enable', input: 'like_count', label: 'いいね数' },
            { check: 'bookmark_enable', input: 'bookmark_count', label: 'ブックマーク数' },
            { check: 'reply_enable', input: 'reply_count', label: 'リプライ数' },
            { check: 'repost_enable', input: 'repost_count', label: 'リポスト数' }
        ];

        let requireTweetId = false;

        for (const { check, input, label } of actions) {
            const checkEl = document.querySelector(`input[name="${check}"]`);
            const inputEl = document.querySelector(`input[name="${input}"]`);
            const isChecked = checkEl?.checked;

            if (isChecked) {
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

        // リプライにリプライ（数値不要だがtweet_idは必要）
        const repToRepChecked = document.querySelector('input[name="rep_to_rep"]')?.checked;
        if (repToRepChecked) {
            requireTweetId = true;
        }

        // tweet_idが必要なのに空ならエラー
        if (requireTweetId && tweetIdInput?.value.trim() === "") {
            alert("対象ツイートIDを入力してください。");
            tweetIdInput.focus();
            e.preventDefault();
        }

        // フォロー操作がONなら、対象アカウント必須
        if (followCheckbox?.checked) {
            const target = followScreenNameInput?.value.trim();
            if (!target) {
                alert("フォロー対象アカウント名を入力してください。");
                followScreenNameInput.focus();
                e.preventDefault();
                return;
            }
        }        
    });
});
</script>




</body>
</html>

