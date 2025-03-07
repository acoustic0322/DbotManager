
<!-- サイドメニュー -->
<div class="sidebar">
    <h2>設定メニュー</h2>
    <?php if (
        (isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1) ||
        (isset($_SESSION['reply_enable']) && $_SESSION['reply_enable'] == 1) ||
        (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1) ||
        (isset($_SESSION['repost_enable']) && $_SESSION['repost_enable'] == 1)
    ): ?>    
    <a href="tweet.php">いいね・ﾌﾞｯｸﾏｰｸ</a>
    <?php endif; ?>

    <?php if (isset($_SESSION['api_master_id']) && $_SESSION['api_master_id'] == 0): ?>
    <a href="account_list.php">Xアカウント設定</a>
    <?php else: ?>
    <a href="account_list_search.php">Xアカウント設定(監視)</a>
    <a href="account_list_process.php">Xアカウント設定(処理)</a>
    <?php endif; ?>

<!--    <a href="comment_list.php">コメント設定</a>  -->
    <a href="password.php">パスワード変更</a>
    <?php if (isset($_SESSION['media_enable']) && $_SESSION['media_enable'] == 1): ?>
        <a href="upload.php?type=m">動画アップロード</a>
        <a href="upload.php?type=p">画像アップロード</a>
    <?php endif; ?>
    
    <?php if (isset($_SESSION['admin']) && $_SESSION['admin'] == 1): ?>
        <a href="user_list.php">ユーザー編集(管理者)</a>
    <?php endif; ?>
    
    <a href="logout.php">ログアウト</a>
</div>