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
    <title>いいね・ブックマーク</title>
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
    <h2>ツイート自動処理 登録フォーム</h2>
    <form method="POST">
        <label for="tweet_id">対象ツイートID</label>
        <input type="text" id="tweet_id" name="tweet_id" required>

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
            <input type="number" id="like_count" name="like_count" min="0">

            <label for="bookmark_count">ブックマーク数</label>
            <input type="number" id="bookmark_count" name="bookmark_count" min="0">

            <label for="reply_count">リプライ数</label>
            <input type="number" id="reply_count" name="reply_count" min="0">

            <label for="repost_count">リポスト数</label>
            <input type="number" id="repost_count" name="repost_count" min="0">
        </div>

        <div class="form-block">
            <label><input type="checkbox" name="follow_enable">フォロー操作</label>
            <label><input type="radio" name="follow_action" value="add">フォロー</label>
            <label><input type="radio" name="follow_action" value="remove">アンフォロー</label>

            <label for="follow_screen_name">対象アカウント名 (@なし)</label>
            <input type="text" id="follow_screen_name" name="follow_screen_name">
        </div>

        <button type="submit" class="btn">登録する</button>
    </form>
      </div>
      </div>
      </div>
</body>
</html>
