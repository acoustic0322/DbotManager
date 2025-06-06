<?php
require __DIR__.'/_lib/config.php';
session_start(); // セッションを開始する

$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    echo "<p>ログインしていません。</p>";
    exit; // ログインしていない場合はここで終了
}

// 新規ユーザー登録処理
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $current_userid = $_SESSION['user_id'];
    $GROQ_API_KEY = $_POST['GROQ_API_KEY'];
    $OPENAI_API_KEY = $_POST['OPENAI_API_KEY'];

    $stmt = $conn->prepare("UPDATE user_master SET GROQ_API_KEY = ? , OPENAI_API_KEY = ? WHERE id = ?");
    $stmt->bind_param("sss", $GROQ_API_KEY, $OPENAI_API_KEY , $current_userid);

    if ($stmt->execute()) {
        /* 更新成功 */
    } else {
        /* 更新失敗 */
    }

    $stmt->close();
    $conn->close();

    // 登録後にリダイレクト
    header("Location: user_master.php");
    exit;     
}

$GROQ_API_KEY = $current_user['GROQ_API_KEY'];
$OPENAI_API_KEY = $current_user['OPENAI_API_KEY'];

?>
<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>プロフィール設定</title>
    <link rel="stylesheet" href="./css/admin-dashboard.css" />
</head>
<body>
<div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
  <div class="main">
    <!-- コンテンツエリア -->
    <div class="content" id="content">
        <form action="?" method="post">

            <label for="GROQ_API_KEY">GROQ_API_KEY:</label><br>
            <input type="GROQ_API_KEY" id="GROQ_API_KEY" name="GROQ_API_KEY" value="<?php echo htmlspecialchars($GROQ_API_KEY); ?>" style="width: 600px;"><br><br>

            <label for="OPENAI_API_KEY">OPENAI_API_KEY:</label><Br>
            <input type="OPENAI_API_KEY" id="OPENAI_API_KEY" name="OPENAI_API_KEY" value="<?php echo htmlspecialchars($OPENAI_API_KEY); ?>" style="width: 600px;"><br><br>
            
            <button type="submit">保存</button>
        </form>  
    </div>
</div>
</body>
</html>
