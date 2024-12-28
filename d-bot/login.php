<?php
require __DIR__.'/_lib/config.php';
session_start();
error_reporting(E_ALL);
ini_set('display_errors', 1);


// データベース接続情報を取得
$servername = $config['servername'];
$username = $config['username'];
$password = $config['password'];
$dbname = $config['dbname'];

// データベース接続
$conn = new mysqli($servername, $username, $password, $dbname);

// エラーメッセージ変数
$error = "";

// ログイン処理
if ($_SERVER['REQUEST_METHOD'] == 'POST') {
    $username = $_POST['username'];
    $password = $_POST['password'];

    // 接続チェック
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

  // データベースからユーザー情報を取得
  $stmt = $conn->prepare("SELECT password,id FROM user_master WHERE username = ?");
  $stmt->bind_param("s", $username);
  $stmt->execute();
  $stmt->store_result();
  $stmt->bind_result($stored_hashed_password, $user_id);
  $stmt->fetch();

    if ($stmt->num_rows > 0) {
        // ユーザーが存在する場合
//        if (password_verify($password, $stored_hashed_password)) {
        if ($password == $stored_hashed_password) {
            // 認証成功: セッションにユーザー名を保存し、ユーザー設定画面へリダイレクト
            $_SESSION['user_id'] = $user_id;
            header("Location: menu.php"); // user_settings.php 画面に遷移
            exit;
        } else {
            // パスワードが一致しない場合
            $error = "パスワードが間違っています。";
        }
    } else {
        // ユーザーが存在しない場合
        $error = "ユーザーが存在しません。";
    }

    $stmt->close();
    $conn->close();
}
?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>ログイン</title>
</head>
<body>
    <h2>ログイン</h2>
    <?php if (!empty($error)) echo "<p style='color:red;'>$error</p>"; ?>
    <form method="POST">
        <label for="username">ユーザー名:</label>
        <input type="text" name="username" required>
        <br>
        <label for="password">パスワード:</label>
        <input type="password" name="password" required>
        <br>
        <button type="submit">ログイン</button>
    </form>
</body>
</html>
