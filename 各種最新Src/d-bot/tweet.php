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

// POSTリクエストの場合
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // 引数の準備
    $tweetId = isset($_POST['tweet_id']) ? $_POST['tweet_id'] : '';

    // フラグを 0 か 1 に正規化
    $likeEnable = (!empty($_POST['like_enable'])) ? 1 : 0;
    $bookmarkEnable = (!empty($_POST['bookmark_enable'])) ? 1 : 0;
    $replyEnable = (!empty($_POST['reply_enable'])) ? 1 : 0;
    $repostEnable = (!empty($_POST['repost_enable'])) ? 1 : 0;

    // 件数を取得
    $likeCount = isset($_POST['like_count']) ? intval($_POST['like_count']) : 0;
    $bookmarkCount = isset($_POST['bookmark_count']) ? intval($_POST['bookmark_count']) : 0;
    $replyCount = isset($_POST['reply_count']) ? intval($_POST['reply_count']) : 0;
    $repostCount = isset($_POST['repost_count']) ? intval($_POST['repost_count']) : 0;

    // INSERT文
    $sql = "INSERT INTO tweet_process_list (
        user_id, tweet_id, like_enable, bookmark_enable, reply_enable, repost_enable, 
        like_count, bookmark_count, reply_count, repost_count, updatetime
    ) 
    VALUES (
        ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, NOW()
    )";    

    // プリペアドステートメント
    $stmt = $conn->prepare($sql);

    // バインド（型指定修正）
    $stmt->bind_param('isiiiiiiii', $current_userid, $tweetId, $likeEnable, $bookmarkEnable, $replyEnable, $repostEnable, $likeCount, $bookmarkCount, $replyCount, $repostCount);

    // 実行
    $stmt->execute();    
    $stmt->close();
    $conn->close();    

}
?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>いいね・ブックマーク処理</title>
    <link rel="stylesheet" type="text/css" href="./main.css">
    <style>
        .registration-form {
/*            display: flex;*/
            margin-bottom: 20px;
        }
        .registration-form input {
            width: 100%; /* 幅を調整 */
            margin-bottom: 5px; /* 各入力欄の間にスペースを設ける */
            padding: 8px;
            font-size: 16px;
        }
        .registration-form button {
            padding: 8px 12px;
            font-size: 16px;
            cursor: pointer;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .button_form{
            display: inline-block;
        }

        .checkbox-group {
           display: flex;
            gap: 10px; /* チェックボックス間のスペース */
        }

        .checkbox-group label {
            display: flex;
            align-items: center; /* チェックボックスとテキストを縦方向で中央揃え */
        }        
    </style>

</head>
<body>

    <?php require PARTS_DIR.'/sidebar.php'; ?>

    <!-- コンテンツエリア -->
    <div class="content" id="content">
<!--        <form action="?" method="post">  -->
        <h2>いいね・ブックマーク処理</h2>
        <form method="POST" action="?">
        <!--
        <label for="user_id">ユーザーID: 
            <span id="user_id"><?php echo htmlspecialchars($current_userid); ?></span>
        </label><br><br>
        -->

        <div class="input-group" checkbox-group">
            <label>
                <input type="text" name="tweet_id" id="tweet_id" placeholder="対象ツイートID" required size="80" maxlength="100">>
            </label><br>

            <?php if (isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="like_enable" value="1">いいね
                <input type="number" name="like_count" min="1" value="10" placeholder="件数" style="width: 60px; margin-left: 5px;">                
            </label><br>
            <?php endif; ?>

            <?php if (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="bookmark_enable" value="1">ブックマーク
                <input type="number" name="bookmark_count" min="1" value="10" placeholder="件数" style="width: 60px; margin-left: 5px;">                
            </label><br>
            <?php endif; ?>

            <?php if (isset($_SESSION['reply_enable']) && $_SESSION['reply_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="reply_enable" value="1">リプライ
                <input type="number" name="reply_count" min="1" value="10" placeholder="件数" style="width: 60px; margin-left: 5px;">                
            </label><br>
            <?php endif; ?>

            <?php if (isset($_SESSION['repost_enable']) && $_SESSION['repost_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="repost_enable" value="1">リポスト
                <input type="number" name="repost_count" min="1" value="10" placeholder="件数" style="width: 60px; margin-left: 5px;">                
            </label><br>
            <?php endif; ?>
        </div>

            <button type="submit">実行</button>
        </form>
    </div>

</body>
</html>
