<?php
require __DIR__.'/_lib/config.php';
session_start();
error_reporting(E_ALL);
ini_set('display_errors', 1);

$servername = $config['servername'];
$username = $config['username'];
$password = $config['password'];
$dbname = $config['dbname'];

$conn = new mysqli($servername, $username, $password, $dbname);
$error = "";

if ($_SERVER['REQUEST_METHOD'] == 'POST') {
  $_SESSION['is_guest'] = false;
  $_SESSION['is_logged_in'] = true;

  $username = $_POST['username'];
  $password = $_POST['password'];

  if ($conn->connect_error) {
    die("Connection failed: " . $conn->connect_error);
  }

  $stmt = $conn->prepare("SELECT password,id FROM user_master WHERE username = ?");
  $stmt->bind_param("s", $username);
  $stmt->execute();
  $stmt->store_result();
  $stmt->bind_result($stored_hashed_password, $user_id);
  $stmt->fetch();

  if ($stmt->num_rows > 0) {
    if ($password == $stored_hashed_password) {
      $_SESSION['user_id'] = $user_id;
      header("Location: menu.php");
      exit;
    } else {
      $error = "パスワードが間違っています。";
    }
  } else {
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
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>D-Botへようこそ</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
  <style>
    body {
      margin: 0;
      font-family: 'Inter', sans-serif;
      background: #0a0f1a;
      color: white;
    }
    .hero {
      background: radial-gradient(ellipse at center, #1e3a8a 0%, #0a0f1a 100%);
      text-align: center;
      padding: 120px 10% 100px;
    }
    .hero h1 {
      font-size: 56px;
      margin-bottom: 20px;
    }
    .hero p {
      font-size: 20px;
      color: #cbd5e1;
    }
    .btn {
      margin-top: 30px;
      padding: 14px 40px;
      background: linear-gradient(to right, #3b82f6, #2563eb);
      color: white;
      border: none;
      border-radius: 10px;
      font-size: 18px;
      font-weight: bold;
      cursor: pointer;
      transition: background 0.3s ease;
    }
    .btn:hover {
      background: linear-gradient(to right, #2563eb, #1d4ed8);
    }
    .login-form {
      max-width: 400px;
      margin: 40px auto;
      background: #1f2937;
      padding: 40px;
      border-radius: 12px;
      box-shadow: 0 0 15px rgba(0,0,0,0.5);
    }
    .login-form h2 {
      font-size: 28px;
      margin-bottom: 20px;
      text-align: center;
    }
    .login-form label {
      display: block;
      margin-top: 20px;
      margin-bottom: 6px;
    }
    .login-form input[type="text"],
    .login-form input[type="password"] {
      width: 100%;
      padding: 12px;
      border: none;
      border-radius: 6px;
      background: #374151;
      color: white;
      font-size: 16px;
    }
    .login-form button {
      width: 100%;
      margin-top: 30px;
      padding: 12px;
      font-size: 16px;
      border-radius: 8px;
      border: none;
      background: #3b82f6;
      color: white;
      font-weight: bold;
      cursor: pointer;
    }
    .login-form .error {
      color: #f87171;
      margin-top: 10px;
      text-align: center;
    }
    .login-image {
      text-align: center;
      margin-top: 40px;
    }
    .login-image img {
      max-width: 300px;
      border-radius: 16px;
      box-shadow: 0 0 20px rgba(0,0,0,0.6);
    }
  </style>
</head>
<body>
  <section class="hero">
    <h1>D-Botへようこそ</h1>
    <p>Xアカウントの自動化と管理を、もっとスマートに。</p>
  </section>

  <div class="login-image">
    <img src="/img/robot-login.png" alt="D-Bot ログイン画面イメージ">
  </div>

  <div class="login-form">
    <h2>ログイン</h2>
    <?php if (!empty($error)) echo "<p class='error'>$error</p>"; ?>
    <form method="POST">
      <label for="username">ユーザー名</label>
      <input type="text" name="username" id="username" required>
      <label for="password">パスワード</label>
      <input type="password" name="password" id="password" required>
      <button type="submit">ログイン</button>
    </form>
  </div>
</body>
</html>
