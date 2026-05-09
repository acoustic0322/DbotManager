<link rel="stylesheet" href="./css/admin-dashboard.css" />

<!-- サイドメニュー -->
<div class="sidebar">
    <h2>設定メニュー</h2>
    <?php if (isset($_SESSION['is_guest']) && $_SESSION['is_guest'] === true): ?>
        <!-- ゲストモード用メニュー -->
        <a href="tweet_japanese.php">日本人いいね</a> 
    <?php else: ?>

        <?php if (isset($_SESSION['japanese_mode']) && $_SESSION['japanese_mode'] === 1): ?>
            <a href="tweet_japanese.php">Twitter拡散サービス</a>
        <?php endif; ?>
        <?php if (isset($_SESSION['japanese_mode']) && $_SESSION['japanese_mode'] === 2): ?>
            <a href="tweet_japanese2.php">Twitter拡散サービス</a>
        <?php endif; ?>

        <?php if (isset($_SESSION['sensyuken_mode']) && $_SESSION['sensyuken_mode'] !== 0): ?>
            <a href="tweet_sensyuken.php">選手権</a>
        <?php endif; ?>        

        <?php if (
            (isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1) ||
            (isset($_SESSION['reply_enable']) && $_SESSION['reply_enable'] == 1) ||
            (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1) ||
            (isset($_SESSION['repost_enable']) && $_SESSION['repost_enable'] == 1) ||
            (isset($_SESSION['follow_enable']) && $_SESSION['follow_enable'] == 1) 
       ): ?>    
            <a href="tweet.php">(自)いいね・ブクマ</a>
        <?php endif; ?>

    <!--
    <a href="account_list.php">Xアカウント設定</a>
    -->

    <a href="account_list.php">Xアカウント一覧(通常)</a>
    <a href="account_regist.php">通常登録</a>

    <a href="account_list_react.php">Xアカウント一覧(クイック)</a>
    <a href="account_regist_react.php">クイック登録</a>

    <?php if (isset($_SESSION['api_master_id']) && $_SESSION['api_master_id'] != 0): ?>
    <a href="account_regist2.php">通常登録(貸出API専用)</a>
    <?php endif; ?>

<!--    <a href="comment_list.php">コメント設定</a>  -->
    <a href="password.php">パスワード変更</a>
    <?php if (isset($_SESSION['media_enable']) && $_SESSION['media_enable'] == 1): ?>
        <a href="upload.php?type=m">動画アップロード</a>
        <a href="upload.php?type=p">画像アップロード</a>
    <?php endif; ?>

    <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
        <a href="user_master.php">AIツイート・リプ<BR>API設定</a>
    <?php endif; ?>

    <?php if (isset($_SESSION['admin']) && $_SESSION['admin'] == 1): ?>
        <a href="user_list.php">ユーザー編集(管理者)</a>
    <?php endif; ?>
    <?php endif; ?>
    
    <?php if (isset($_SESSION['is_logged_in']) && $_SESSION['is_logged_in'] === true): ?>
    <a href="logout.php">ログアウト</a>
    <?php endif; ?>

</div>