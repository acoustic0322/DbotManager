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
    $new_password = $_POST['password'];

    $stmt = $conn->prepare("UPDATE user_master SET password = ? WHERE id = ?");
    $stmt->bind_param("ss", $new_password, $current_userid);

    if ($stmt->execute()) {
        /* 更新成功 */
    } else {
        /* 更新失敗 */
    }

    $stmt->close();
    $conn->close();

    // 登録後にリダイレクト
    header("Location: password.php");
    exit;     
}

$password = $current_user['password'];

?>
<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>パスワード変更</title>
  <link rel="stylesheet" href="./css/admin-dashboard.css" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
</head>
<body class="password-page">
<div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
<div class="main">
    <!-- コンテンツエリア -->
    <div class="content" id="content">
        <form action="?" method="post">
            <label for="password">パスワード:</label>
            <input type="password" id="password" name="password" value="<?php echo htmlspecialchars($password); ?>" required><br><br>
            
            <button type="submit">変更</button>
        </form>  
    </div>
    </div>
</body>
</html>
