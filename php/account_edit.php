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
    $access_token = trim($_POST['access_token'] ?? '');
    $access_token_secret = trim($_POST['access_token_secret'] ?? '');
    $bearer_token = trim($_POST['bearer_token'] ?? '');
    $refresh_token = trim($_POST['refresh_token'] ?? '');

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

    // 入力値のバリデーション
//    if (empty($name) || empty($login_id) || empty($login_password)) {
    if (empty($name) || empty($login_id)) {
            echo '必須項目を全て入力してください';
        exit;
    }

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
            access_token = ?, 
            access_token_secret = ?, 
            bearer_token = ?, 
            refresh_token = ?, 
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
            reserve4_count = ?
        WHERE id = ?
    ");

    $stmt->bind_param(
        "sssssssssssiiiiiiiiiiiiiiiiiiiiiiiiii", // 型指定
        $name, 
        $login_id, 
        $hashed_password, 
        $client_id, 
        $client_secret, 
        $api_key, 
        $api_key_secret, 
        $access_token, 
        $access_token_secret, 
        $bearer_token, 
        $refresh_token, 
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
        $id
    );
    
    echo "<script>alert('{$id}');</script>";

    // SQLクエリ実行
    $stmt->execute();
    $stmt->close();

    echo "<script>alert('test1');</script>";


    // 登録後にリダイレクト
    header("Location: account_list.php");
    exit; 
}

?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>プロフィール設定</title>
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
        <form method="POST" action="?" class="registration-form">
            <!--
            <label for="user_id">ユーザーID:</label>
            <input type="text" id="user_id" name="user_id" value="<?php echo htmlspecialchars($edit_account['user_id'] ?? '') ?>" required><br><br>
            -->

            <div class="input-group">
            <input type="text" id="name" name="name" placeholder="名前" value="<?php echo htmlspecialchars($edit_account['name'] ?? '') ?>" required>
        </div>
        <div class="input-group">
            <input type="text" id="login_id" name="login_id" placeholder="ログインID" value="<?php echo htmlspecialchars($edit_account['login_id'] ?? '') ?>" required>
        </div>
        <div class="input-group">
            <input type="text" id="login_pass" name="login_pass" placeholder="ログインパス" value="<?php echo htmlspecialchars($edit_account['login_password'] ?? '') ?>">
        </div>
        <div class="input-group">
            <input type="text" name="client_id" placeholder="ClientID" value="<?php echo htmlspecialchars($edit_account['client_id'] ?? '') ?>">
        </div>
        <div class="input-group">
            <input type="text" name="client_secret" placeholder="ClientSecret" value="<?php echo htmlspecialchars($edit_account['client_secret'] ?? '') ?>">
        </div>
        <div class="input-group">
            <input type="text" name="api_key" placeholder="ApiKey" value="<?php echo htmlspecialchars($edit_account['api_key'] ?? '') ?>">
        </div>
        <div class="input-group">
            <input type="text" name="api_key_secret" placeholder="ApiKeySecret" value="<?php echo htmlspecialchars($edit_account['api_key_secret'] ?? '') ?>">
        </div>
        <div class="input-group">
            <input type="text" name="access_token" placeholder="AccessToken" value="<?php echo htmlspecialchars($edit_account['access_token'] ?? '') ?>">
        </div>
        <div class="input-group">
            <input type="text" name="access_token_secret" placeholder="AccessTokenSecret" value="<?php echo htmlspecialchars($edit_account['access_token_secret'] ?? '') ?>">
        </div>
        <div class="input-group">
            <input type="text" name="bearer_token" placeholder="BearerToken" value="<?php echo htmlspecialchars($edit_account['bearer_token'] ?? '') ?>">
        </div>
        <div class="input-group">
            <input type="text" name="refresh_token" placeholder="RefreshToken" value="<?php echo htmlspecialchars($edit_account['refresh_token'] ?? '') ?>">
        </div>

        <div class="input-group" checkbox-group">
            <label>
                <input type="checkbox" name="enable" value="1" <?php echo !empty($edit_account['enable']) ? 'checked' : '' ?>>有効
            </label>
            <label>
                <input type="checkbox" name="post_enable" value="1" <?php echo !empty($edit_account['post_enable']) ? 'checked' : '' ?>>ポスト機能
            </label>
            <label>
                <input type="checkbox" name="like_enable" value="1" <?php echo !empty($edit_account['like_enable']) ? 'checked' : '' ?>>いいね機能
            </label>
            <label>
                <input type="checkbox" name="bookmark_enable" value="1" <?php echo !empty($edit_account['bookmark_enable']) ? 'checked' : '' ?>>ブックマーク機能
            </label>
            <label>
                <input type="checkbox" name="reply_enable" value="1" <?php echo !empty($edit_account['reply_enable']) ? 'checked' : '' ?>>リプライ機能
            </label>
            <label>
                <input type="checkbox" name="repost_enable" value="1" <?php echo !empty($edit_account['repost_enable']) ? 'checked' : '' ?>>リポスト機能
            </label>
        </div>

        <div class="input-group">
            <label>
                <input type="checkbox" name="paid" value="1" <?php echo !empty($edit_account['paid']) ? 'checked' : '' ?>>有料アカウント
            </label>
            <label>
                <input type="checkbox" name="paid_like" value="1" <?php echo !empty($edit_account['paid_like']) ? 'checked' : '' ?>>有料API(いいね)
            </label>
            <label>
                <input type="checkbox" name="paid_bookmark" value="1" <?php echo !empty($edit_account['paid_bookmark']) ? 'checked' : '' ?>>有料API(ブックマーク)
            </label>
        </div>

            <input type="hidden" name="id" value="<?php echo htmlspecialchars($id); ?>">
            <button type="submit">更新</button>
        </form>
    </div>

</body>
</html>
