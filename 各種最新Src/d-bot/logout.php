<?php
session_start();
session_unset(); // セッション変数を全て解除
session_destroy(); // セッションを破棄
header("Location: login.php"); // ログインページにリダイレクト
exit();
?>
