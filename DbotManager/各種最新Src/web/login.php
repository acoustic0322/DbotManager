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

    /*
    if (isset($_POST['guest'])) {
        $_SESSION['user_id'] = 'guest';
        $_SESSION['is_guest'] = true;
        $_SESSION['user_id'] = 1;
        $_SESSION['is_logged_in'] = false;
        header("Location: menu.php");
        exit;
    }
        */

	$_SESSION['is_guest'] = false;
  $_SESSION['is_logged_in'] = true;

  $username = $_POST['username'] ?? '';
  $password = $_POST['password'] ?? '';

    // 接続チェック
    if ($conn->connect_error) {
        die("Connection failed: " . $conn->connect_error);
    }

  // データベースからユーザー情報を取得
  // 変更後
$stmt = $conn->prepare("SELECT password,id,hide_sensitive_fields FROM user_master WHERE username = ?");
$stmt->bind_param("s", $username);
$stmt->execute();
$stmt->store_result();
$stmt->bind_result($stored_hashed_password, $user_id, $hide_sensitive_fields);
$stmt->fetch();

if ($stmt->num_rows > 0) {
    if ($password == $stored_hashed_password) {
        $_SESSION['user_id'] = $user_id;
        $_SESSION['hide_sensitive_fields'] = (int)$hide_sensitive_fields;
        header("Location: menu.php");
        exit;
    }else {
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
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0" />
    <title>ログイン - X-DBOT</title>   
    <link rel="stylesheet" href="css/top-login.css" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin />
    <link
      href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;600;700&display=swap"
      rel="stylesheet"
    />
  </head>
  <body>
      <div class="layout">
    <div class="noise-overlay"></div>

    <a href="index.html" class="back-link">ホームに戻る</a>

    <div class="login-container">
      <div class="login-box fade-in">
        <div class="login-header">
          <h1>X-DBOT<span class="gold-dot">.</span></h1>
          <p>アカウントにログイン</p>
        </div>

        <form action="#" method="POST">
          <div class="form-group">
            <label for="email">ユーザーID</label>
            <input
              type="text"
              id="username"
              name="username"
              class="form-control"
              required
            />
          </div>

          <div class="form-group">
            <label for="password">パスワード</label>
            <input
              type="password"
              id="password"
              name="password"
              class="form-control"
              required
            />
          </div>

          <button type="submit" class="btn-login">ログイン</button>

          <p
            style="
              color: #d4af37;
              font-size: 16px;
              text-align: center;
              margin: 20px 0;
            "
          >
          <!--
          ↓デモのため、こちらで管理画面に遷移
          </p>
          <a
            href="./sidebar.html"
            class="btn-signup"
            style="
              color: #fff;
              background-color: #007bff;
              padding: 10px 15px;
              border-radius: 5px;
              text-decoration: none;
            "
            >ログインページに遷移</a
          >
-->
        </form>
      </div>
    </div>

    <script src="js/animations.js"></script>
  </body>
</div>
</html>
