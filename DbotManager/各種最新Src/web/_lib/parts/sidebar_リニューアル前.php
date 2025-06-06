<style>
  .sidebar {
    background: #1e1e1e;
    padding: 30px 20px;
    border-radius: 12px;
    width: 260px;
    color: white;
    font-family: 'Inter', sans-serif;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.4);
  }
  .sidebar h2 {
    font-size: 20px;
    margin-bottom: 20px;
    border-bottom: 1px solid #3b82f6;
    padding-bottom: 10px;
    color: #3b82f6;
  }
  .sidebar a {
    display: block;
    padding: 12px 16px;
    margin: 6px 0;
    text-decoration: none;
    color: white;
    background: #2a2a2a;
    border-radius: 8px;
    transition: 0.3s;
    font-size: 14px;
  }
  .sidebar a:hover {
    background: linear-gradient(to right, #3b82f6, #2563eb);
    transform: translateX(4px);
  }
</style>


<!-- サイドメニュー -->
<div class="sidebar">
    <h2>設定メニュー</h2>
    <?php if (isset($_SESSION['is_guest']) && $_SESSION['is_guest'] === true): ?>
        <!-- ゲストモード用メニュー -->
        <a href="tweet_japanese.php">日本人いいね</a> 
    <?php else: ?>
        <?php if (
            (isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1) ||
            (isset($_SESSION['reply_enable']) && $_SESSION['reply_enable'] == 1) ||
            (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1) ||
            (isset($_SESSION['repost_enable']) && $_SESSION['repost_enable'] == 1) ||
            (isset($_SESSION['follow_enable']) && $_SESSION['follow_enable'] == 1) 
       ): ?>    

            <?php if (isset($_SESSION['japanese_mode']) && $_SESSION['japanese_mode'] !== 0): ?>
                <a href="tweet_japanese.php">Twitter拡散サービス(日本人いいね)</a>
            <?php endif; ?>

            <?php if (isset($_SESSION['sensyuken_mode']) && $_SESSION['sensyuken_mode'] !== 0): ?>
                <a href="tweet_sensyuken.php">選手権いいね</a>
            <?php endif; ?>

            <a href="tweet.php">いいね・ﾌﾞｯｸﾏｰｸ</a>
        <?php endif; ?>

    <!--
    <a href="account_list.php">Xアカウント設定</a>
    -->

    <a href="account_list.php">Xアカウント一覧</a>

    <a href="account_regist.php">Xアカウント登録</a>

    <?php if (isset($_SESSION['api_master_id']) && $_SESSION['api_master_id'] != 0): ?>
    <a href="account_regist2.php">Xアカウント登録(貸出)</a>
    <?php endif; ?>

<!--    <a href="comment_list.php">コメント設定</a>  -->
    <a href="password.php">パスワード変更</a>
    <?php if (isset($_SESSION['media_enable']) && $_SESSION['media_enable'] == 1): ?>
        <a href="upload.php?type=m">動画アップロード</a>
        <a href="upload.php?type=p">画像アップロード</a>
    <?php endif; ?>

    <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
        <a href="user_master.php">AI API設定</a>
    <?php endif; ?>

    <?php if (isset($_SESSION['admin']) && $_SESSION['admin'] == 1): ?>
        <a href="user_list.php">ユーザー編集(管理者)</a>
    <?php endif; ?>
    <?php endif; ?>
    
    <?php if (isset($_SESSION['is_logged_in']) && $_SESSION['is_logged_in'] === true): ?>
    <a href="logout.php">ログアウト</a>
    <?php endif; ?>

</div>