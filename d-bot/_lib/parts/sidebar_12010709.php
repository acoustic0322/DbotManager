
<!-- サイドメニュー -->
<div class="sidebar">
    <h2>設定メニュー</h2>
    <a href="account_list.php">Xアカウント設定</a>
    <a href="password.php">パスワード変更</a>
    <a href="upload.php?type=m">動画アップロード</a>
    <a href="upload.php?type=p">画像アップロード</a>
    
    <?php if (isset($_SESSION['admin']) && $_SESSION['admin'] == 1): ?>
        <a href="user_list.php">ユーザー編集(管理者)</a>
    <?php endif; ?>
    
    <a href="logout.php">ログアウト</a>
</div>