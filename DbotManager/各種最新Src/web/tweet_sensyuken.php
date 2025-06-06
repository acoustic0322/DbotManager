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

//echo $current_userid ;

$stmt = $conn->prepare("
SELECT COUNT(*) AS today_count
FROM tweet_process_list
WHERE user_id = ? and sensyuken_mode != 0 and sensyuken_mode is not null
and DATE(updatetime) = CURDATE()");

$stmt->bind_param("s", $current_userid);
$stmt->execute();

$result = $stmt->get_result();
$row = $result->fetch_assoc();
$today_count = $row['today_count'];
$exe_enable_count = ($sensyuken_mode * 5) - $today_count;

$stmt->close();

// POSTリクエストの場合
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // 引数の準備
    $tweetId = isset($_POST['tweet_id']) ? $_POST['tweet_id'] : '';


    // INSERT文
    $sql = "INSERT INTO tweet_process_list (
        user_id, tweet_id, 
        updatetime , sensyuken_mode
    ) 
    VALUES (
        ?, ?, NOW() , ? 
    )";    

    // プリペアドステートメント
    $stmt = $conn->prepare($sql);

    // バインド（型指定修正）
    $stmt->bind_param('isi', $current_userid, $tweetId, $sensyuken_mode);

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
    <title>選手権 いいね・ブックマーク処理</title>
    <link rel="stylesheet" href="./css/admin-dashboard.css" />
</head>
<body class="tweet-sensyuken-page">
<div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
  <div class="main">
    <!-- コンテンツエリア -->
    <div class="content" id="content">
        <h2>選手権 いいね・ブックマーク処理</h2>
        <label>本日の残り回数： <?php echo ($exe_enable_count); ?> </label><br><br>
        <form method="POST" action="?">
        <div class="input-group" checkbox-group">
            <label>
                <input type="text" name="tweet_id" id="tweet_id" placeholder="対象ツイートID" required size="80" maxlength="100">>
            </label><br><br>
        </div>

            <button type="submit" <?php if ($exe_enable_count <= 0) echo 'disabled'; ?>>実行</button>
        </form>
    </div>
</div>

</body>
</html>
