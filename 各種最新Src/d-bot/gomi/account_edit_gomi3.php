<?php
require __DIR__ . '/_lib/config.php';
session_start(); // セッションを開始する

// データベース接続
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

// セッションによるユーザー確認
if (!current_user($conn)) {
    echo "<p>ログインしていません。</p>";
    exit;
}


// idの確認
//$id = $_GET['id'] ?? null;
$id = $_POST['id'] ?? $_GET['id'] ?? null;


if (empty($id)) {
    echo 'IDを指定してください';
    exit;
}

$edit_account = get_account($conn, $id);
if ($edit_account === null) {
    echo 'アカウントが存在しません';
    exit;
}

// POSTリクエストの場合
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // 必須フィールドのサニタイズ
    $name = htmlspecialchars(trim($_POST['name'] ?? ''));
    $login_id = htmlspecialchars(trim($_POST['login_id'] ?? ''));

    // その他のフィールドの処理（オプションの場合はチェック）
    $login_password = trim($_POST['login_password'] ?? '');
    $client_id = trim($_POST['client_id'] ?? '');
    $client_secret = trim($_POST['client_secret'] ?? '');

    $api_key = trim($_POST['api_key'] ?? '');
    $api_key_secret = trim($_POST['api_key_secret'] ?? '');

    /*
    $access_token = trim($_POST['access_token'] ?? '');
    $access_token_secret = trim($_POST['access_token_secret'] ?? '');
    $bearer_token = trim($_POST['bearer_token'] ?? '');
    $refresh_token = trim($_POST['refresh_token'] ?? '');
    */

    // チェックボックスの値をバインド
    $enable = isset($_POST['enable']) ? 1 : 0;
    $like_enable = isset($_POST['like_enable']) ? 1 : 0;
    $bookmark_enable = isset($_POST['bookmark_enable']) ? 1 : 0;
    $reply_enable = isset($_POST['reply_enable']) ? 1 : 0;
    $paid = isset($_POST['paid']) ? 1 : 0;
    $paid_like = isset($_POST['paid_like']) ? 1 : 0;
    $paid_bookmark = isset($_POST['paid_bookmark']) ? 1 : 0;
    $repost_enable = isset($_POST['repost_enable']) ? 1 : 0;
    $post_enable = isset($_POST['post_enable']) ? 1 : 0;

    // 予約の処理（Reserve1-4）
    $reserve1_enable = isset($_POST['reserve1_enable']) ? 1 : 0;
    $reserve1_start_hour = $_POST['reserve1_start_hour'] ?? 0;
    $reserve1_end_hour = $_POST['reserve1_end_hour'] ?? 0;
    $reserve1_count = $_POST['reserve1_count'] ?? 0;

    $reserve2_enable = isset($_POST['reserve2_enable']) ? 1 : 0;
    $reserve2_start_hour = $_POST['reserve2_start_hour'] ?? 0;
    $reserve2_end_hour = $_POST['reserve2_end_hour'] ?? 0;
    $reserve2_count = $_POST['reserve2_count'] ?? 0;

    $reserve3_enable = isset($_POST['reserve3_enable']) ? 1 : 0;
    $reserve3_start_hour = $_POST['reserve3_start_hour'] ?? 0;
    $reserve3_end_hour = $_POST['reserve3_end_hour'] ?? 0;
    $reserve3_count = $_POST['reserve3_count'] ?? 0;

    $reserve4_enable = isset($_POST['reserve4_enable']) ? 1 : 0;
    $reserve4_start_hour = $_POST['reserve4_start_hour'] ?? 0;
    $reserve4_end_hour = $_POST['reserve4_end_hour'] ?? 0;
    $reserve4_count = $_POST['reserve4_count'] ?? 0;

    $dmm_id = $_POST['dmm_id'];

    $search_enable = isset($_POST['search_enable']) ? 1 : 0;
    $proxy_enable = isset($_POST['proxy_enable']) ? 1 : 0;
    $proxy_url = $_POST['proxy_url'];
    $check_interval = $_POST['check_interval'];

    // 入力値のバリデーション
//    if (empty($name) || empty($login_id) || empty($login_password)) {
    if (empty($name) || empty($login_id)) {
            echo '必須項目を全て入力してください';
        exit;
    }

//    echo $login_password,

    // パスワードをハッシュ化
    $hashed_password = password_hash($login_password, PASSWORD_DEFAULT);

    // SQLクエリの準備
    $stmt = $conn->prepare("
        UPDATE account_master
        SET 
            name = ?, 
            login_id = ?, 
            login_password = ?, 
            client_id = ?, 
            client_secret = ?, 
            api_key = ?, 
            api_key_secret = ?, 
            enable = ?, 
            like_enable = ?, 
            bookmark_enable = ?, 
            reply_enable = ?, 
            paid = ?, 
            paid_like = ?, 
            paid_bookmark = ?, 
            repost_enable = ?, 
            post_enable = ?, 
            reserve1_enable = ?, 
            reserve1_start_hour = ?, 
            reserve1_end_hour = ?, 
            reserve1_count = ?, 
            reserve2_enable = ?, 
            reserve2_start_hour = ?, 
            reserve2_end_hour = ?, 
            reserve2_count = ?, 
            reserve3_enable = ?, 
            reserve3_start_hour = ?, 
            reserve3_end_hour = ?, 
            reserve3_count = ?, 
            reserve4_enable = ?, 
            reserve4_start_hour = ?, 
            reserve4_end_hour = ?, 
            reserve4_count = ?,
            dmm_id = ? ,
            search_enable = ? ,
            proxy_enable = ? ,
            proxy_url = ? ,
            check_interval = ?
        WHERE id = ?
    ");

//    "sssssssssssiiiiiiiiiiiiiiiiiiiiiiiiii", // 型指定
    $stmt->bind_param(
        "sssssssiiiiiiiiiiiiiiiiiiiiiiiiisiisis", // 型指定
        $name, 
        $login_id, 
#        $hashed_password, 
        $login_password,
        $client_id, 
        $client_secret, 
        $api_key, 
        $api_key_secret, 
        $enable, 
        $like_enable, 
        $bookmark_enable, 
        $reply_enable, 
        $paid, 
        $paid_like, 
        $paid_bookmark, 
        $repost_enable, 
        $post_enable, 
        $reserve1_enable, 
        $reserve1_start_hour, 
        $reserve1_end_hour, 
        $reserve1_count, 
        $reserve2_enable, 
        $reserve2_start_hour, 
        $reserve2_end_hour, 
        $reserve2_count, 
        $reserve3_enable, 
        $reserve3_start_hour, 
        $reserve3_end_hour, 
        $reserve3_count, 
        $reserve4_enable, 
        $reserve4_start_hour, 
        $reserve4_end_hour, 
        $reserve4_count,
        $dmm_id,
        $search_enable ,
        $proxy_enable ,
        $proxy_url ,
        $check_interval ,
        $id
    );
    
//    echo "<script>alert('{$reserve1_enable}');</script>";

    // SQLクエリ実行
    $stmt->execute();
    $stmt->close();

//    echo "<script>alert('test1');</script>";


    // 登録後にリダイレクト
    header("Location: account_list.php");
    exit; 
}

?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Xアカウント編集</title>
    <link rel="stylesheet" type="text/css" href="./main.css">
    <style>
        .registration-form {
/*            display: flex;*/
            margin-bottom: 20px;
        }
        .registration-form input {
            width: 100%; /* 幅を調整 */
            margin-bottom: 5px; /* 各入力欄の間にスペースを設ける */
            padding: 8px;
            font-size: 16px;
        }
        .registration-form button {
            padding: 8px 12px;
            font-size: 16px;
            cursor: pointer;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
        }
        th, td {
            border: 1px solid #ddd;
            padding: 8px;
            text-align: left;
        }
        th {
            background-color: #f2f2f2;
        }
        .button_form{
            display: inline-block;
        }

        .checkbox-group {
           display: flex;
            gap: 10px; /* チェックボックス間のスペース */
        }

        .checkbox-group label {
            display: flex;
            align-items: center; /* チェックボックスとテキストを縦方向で中央揃え */
        }        
    </style>

</head>
<body>

    <?php require PARTS_DIR.'/sidebar.php'; ?>

    <!-- コンテンツエリア -->
    <div class="content" id="content">
<!--        <form action="?" method="post">  -->
<!--        <form method="POST" action="?" class="registration-form">-->
        <form method="POST" action="?">
            <!--
            <label for="user_id">ユーザーID:</label>
            <input type="text" id="user_id" name="user_id" value="<?php echo htmlspecialchars($edit_account['user_id'] ?? '') ?>" required><br><br>
            -->

    <!-- ラジオボタン api_master_modeが設定されてるときのみ表示 -->
    <?php if (isset($_SESSION['api_master_id']) && $_SESSION['api_master_id'] != 0): ?>     
        <div class="input-group">
        <label>
            <input type="radio" name="new_use_admin_api" value="search" checked onclick="toggleUseAdminApi()"> 監視専用
        </label>
        <label>
            <input type="radio" name="new_use_admin_api" value="process" onclick="toggleUseAdminApi()"> いいね・ブックマーク専用
        </label>
        <br>
        </div>
    <?php else: ?>
        <!-- modeがnormalのまま送信されるようにする -->
        <input type="hidden" name="new_use_admin_api" value="normal">    
    <?php endif; ?>


        <div class="input-group">
            <label for="name">名前:</label><br>
            <input type="text" id="name" name="name" placeholder="名前" value="<?php echo htmlspecialchars($edit_account['name'] ?? '') ?>" required>
        </div>
        <div class="input-group">
            <label for="name">ログインID:</label><br>
            <input type="text" id="login_id" name="login_id" placeholder="ログインID" value="<?php echo htmlspecialchars($edit_account['login_id'] ?? '') ?>" required>
        </div>
        <div class="input-group">
            <label for="name">ログインパス:</label><br>
            <input type="text" id="login_pass" name="login_password" placeholder="ログインパス" value="<?php echo htmlspecialchars($edit_account['login_password'] ?? '') ?>">
        </div>


    <!-- チェックボックス (通常モード用) -->
    <div id="search-options">
        <div class="input-group">
            <label for="name">クライアントID:</label><br>
            <input type="text" name="client_id" placeholder="ClientID" value="<?php echo htmlspecialchars($edit_account['client_id'] ?? '') ?>">
        </div>
        <div class="input-group">
            <label for="name">クライアントシークレット:</label><br>
            <input type="text" name="client_secret" placeholder="ClientSecret" value="<?php echo htmlspecialchars($edit_account['client_secret'] ?? '') ?>">
        </div>
    </div>

    <!--

        <div class="input-group">
            <label for="name">クライアントID:</label><br>
            <input type="text" name="client_id" placeholder="ClientID" value="<?php echo htmlspecialchars($edit_account['client_id'] ?? '') ?>">
        </div>
        <div class="input-group">
            <label for="name">クライアントシークレット:</label><br>
            <input type="text" name="client_secret" placeholder="ClientSecret" value="<?php echo htmlspecialchars($edit_account['client_secret'] ?? '') ?>">
        </div>
    -->

        <!--
        <div class="input-group">
            <label for="name">bearer_token:</label>
            <input type="text" name="bearer_token" placeholder="BearerToken" value="<?php echo htmlspecialchars($edit_account['bearer_token'] ?? '') ?>">
        </div>
        <div class="input-group">
            <label for="name">refresh_token:</label>
            <input type="text" name="refresh_token" placeholder="RefreshToken" value="<?php echo htmlspecialchars($edit_account['refresh_token'] ?? '') ?>">
        </div>
    -->

        <div class="input-group" checkbox-group">
            <label>
                <input type="checkbox" name="enable" value="1" <?php echo !empty($edit_account['enable']) ? 'checked' : '' ?>>有効
            </label><br>

            <?php if (isset($_SESSION['post_enable']) && $_SESSION['post_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="post_enable" value="1" <?php echo !empty($edit_account['post_enable']) ? 'checked' : '' ?>>ポスト機能
            </label><br>
            <?php endif; ?>

            <?php if (isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="like_enable" value="1" <?php echo !empty($edit_account['like_enable']) ? 'checked' : '' ?>>いいね機能
            </label><br>
            <?php endif; ?>

            <?php if (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="bookmark_enable" value="1" <?php echo !empty($edit_account['bookmark_enable']) ? 'checked' : '' ?>>ブックマーク機能
            </label><br>
            <?php endif; ?>

            <?php if (isset($_SESSION['reply_enable']) && $_SESSION['reply_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="reply_enable" value="1" <?php echo !empty($edit_account['reply_enable']) ? 'checked' : '' ?>>リプライ機能
            </label><br>
            <?php endif; ?>

            <?php if (isset($_SESSION['repost_enable']) && $_SESSION['repost_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="repost_enable" value="1" <?php echo !empty($edit_account['repost_enable']) ? 'checked' : '' ?>>リポスト機能
            </label><br>
            <?php endif; ?>

            <div id="search-options">
            <?php if (isset($_SESSION['check_enable']) && $_SESSION['check_enable'] == 1): ?>

            <label>
                <input type="checkbox" name="search_enable" value="0" <?php echo !empty($edit_account['search_enable']) ? 'checked' : '' ?>>監視実施
            </label><br>

            <div class="input-group">
            <label for="check_interval">監視周期(分):</label>
            <input type="number" id="check_interval" name="check_interval" min="5" max="6000" step="1" value="<?php echo htmlspecialchars($edit_account['check_interval'] ?? '') ?>" style="width: 50px;">
            </div>             
            <?php endif; ?>
            </div>

            <label>
                <input type="checkbox" name="proxy_enable" value="0" <?php echo !empty($edit_account['proxy_enable']) ? 'checked' : '' ?>>プロキシ
            </label><br>
            <input type="text" name="proxy_url" placeholder="プロキシURL" value="<?php echo htmlspecialchars($edit_account['proxy_url'] ?? '') ?>">
            <br>

            <?php if ((isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1) || 
              (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1)): ?>
            <label>
                <input type="checkbox" name="paid" value="1" <?php echo !empty($edit_account['paid']) ? 'checked' : '' ?>>有料アカウント
            </label><br>
            <?php endif; ?>

            <div id="process-options">
            <?php if (isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="paid_like" value="1" <?php echo !empty($edit_account['paid_like']) ? 'checked' : '' ?>>有料API(いいね)
            </label><br>
            <?php endif; ?>

            <?php if (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="paid_bookmark" value="1" <?php echo !empty($edit_account['paid_bookmark']) ? 'checked' : '' ?>>有料API(ブックマーク)
            </label><br>
            <?php endif; ?>
            </div>
        </div>

        <div class="input-group">
            DMM ID:<br>
            <input type="text" id="dmm_id" name="dmm_id" placeholder="DMM ID" value="<?php echo htmlspecialchars($edit_account['dmm_id'] ?? '') ?>">
        </div>

        <div id="process-options">

        <br>
        【メディアポスト関連】
        <br>
        <div class="input-group">
            <label for="name">ApiKey:</label><br>
            <input type="text" name="api_key" placeholder="ApiKey" value="<?php echo htmlspecialchars($edit_account['api_key'] ?? '') ?>">
        </div>
        <div class="input-group">
            <label for="name">ApiKeySecret:</label><br>
            <input type="text" name="api_key_secret" placeholder="ApiKeySecret" value="<?php echo htmlspecialchars($edit_account['api_key_secret'] ?? '') ?>">
        </div>
        </div>
        
        <!--
        <div class="input-group">
            <label for="name">AccessToken:</label><br>
            <input type="text" name="access_token" placeholder="AccessToken" value="<?php echo htmlspecialchars($edit_account['access_token'] ?? '') ?>">
        </div>
        <div class="input-group">
            <label for="name">AccessTokenSecret:</label><br>
            <input type="text" name="access_token_secret" placeholder="AccessTokenSecret" value="<?php echo htmlspecialchars($edit_account['access_token_secret'] ?? '') ?>">
        </div>
            -->
            <div id="process-options">

        <br>
        【ポスト予約設定】
        <br>
        <label>
            <input type="checkbox" name="reserve1_enable" value="1" <?php echo !empty($edit_account['reserve1_enable']) ? 'checked' : '' ?>>時間帯１
            <input type="text" name="reserve1_start_hour" class="short" placeholder="開始" value="<?php echo htmlspecialchars($edit_account['reserve1_start_hour'] ?? '') ?>"> ～
            <input type="text" name="reserve1_end_hour" class="short" placeholder="終了" value="<?php echo htmlspecialchars($edit_account['reserve1_end_hour'] ?? '') ?>"> 時　
            <input type="text" name="reserve1_count" class="short" placeholder="" value="<?php echo htmlspecialchars($edit_account['reserve1_count'] ?? '') ?>"> 回
        </label><br>
        <label>
            <input type="checkbox" name="reserve2_enable" value="1" <?php echo !empty($edit_account['reserve2_enable']) ? 'checked' : '' ?>>時間帯２
            <input type="text" name="reserve2_start_hour" class="short" placeholder="開始" value="<?php echo htmlspecialchars($edit_account['reserve2_start_hour'] ?? '') ?>"> ～
            <input type="text" name="reserve2_end_hour" class="short" placeholder="終了" value="<?php echo htmlspecialchars($edit_account['reserve2_end_hour'] ?? '') ?>"> 時　
            <input type="text" name="reserve2_count" class="short" placeholder="" value="<?php echo htmlspecialchars($edit_account['reserve2_count'] ?? '') ?>"> 回
        </label><br>
        <label>
            <input type="checkbox" name="reserve3_enable" value="1" <?php echo !empty($edit_account['reserve3_enable']) ? 'checked' : '' ?>>時間帯３
            <input type="text" name="reserve3_start_hour" class="short" placeholder="開始" value="<?php echo htmlspecialchars($edit_account['reserve3_start_hour'] ?? '') ?>"> ～
            <input type="text" name="reserve3_end_hour" class="short" placeholder="終了" value="<?php echo htmlspecialchars($edit_account['reserve3_end_hour'] ?? '') ?>"> 時　
            <input type="text" name="reserve3_count" class="short" placeholder="" value="<?php echo htmlspecialchars($edit_account['reserve3_count'] ?? '') ?>"> 回
        </label><br>
        <label>
            <input type="checkbox" name="reserve4_enable" value="1" <?php echo !empty($edit_account['reserve4_enable']) ? 'checked' : '' ?>>時間帯４
            <input type="text" name="reserve4_start_hour" class="short" placeholder="開始" value="<?php echo htmlspecialchars($edit_account['reserve4_start_hour'] ?? '') ?>"> ～
            <input type="text" name="reserve4_end_hour" class="short" placeholder="終了" value="<?php echo htmlspecialchars($edit_account['reserve4_end_hour'] ?? '') ?>"> 時　
            <input type="text" name="reserve4_count" class="short" placeholder="" value="<?php echo htmlspecialchars($edit_account['reserve4_count'] ?? '') ?>"> 回
        </label><br>
        
        <br>
            </div>


            <input type="hidden" name="id" value="<?php echo htmlspecialchars($id); ?>">
            <button type="submit">更新</button>
        </form>
    </div>

<style>
    /* テキストボックスの幅を80%に設定 */
    .input-group input[type="text"] {
        width: 80%; /* 幅を80%に設定 */
        padding: 8px; /* パディングを追加 */
        font-size: 12px; /* フォントサイズを調整 */
        margin-bottom: 5px; /* ボックス間のスペース */
        box-sizing: border-box; /* パディングを含めた幅を計算 */
    }
</style> 

<style>
    /* テキストボックスの幅を短く設定 */
    input[type="text"].short {
        width: 40px; /* 必要に応じて調整 */
    }
</style>


<script>

document.addEventListener("DOMContentLoaded", function () {
    toggleUseAdminApi();
});

function toggleUseAdminApi() {

   
    const searchOptions = document.getElementById('search-options');
    const processOptions = document.getElementById('process-options');
    const selectedMode = document.querySelector('input[name="new_use_admin_api"]:checked').value;

    if (selectedMode === "search") {
        searchOptions.style.display = "block";
        processOptions.style.display = "none";
    } else {
        searchOptions.style.display = "none";
        processOptions.style.display = "block";
    }

//    if (isset($_SESSION['api_master_id']) && $_SESSION['api_master_id'] === 0)

    // PHPから取得したセッション変数をJavaScriptに渡す
    const apiMasterId = <?php echo json_encode($api_master_id); ?>;
    if (apiMasterId === 0)     
    {
//        searchOptions.style.display = "block";
//        processOptions.style.display = "block";
    }

}
</script>


</body>
</html>
