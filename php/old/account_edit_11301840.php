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
$id = $_GET['id'] ?? null;
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
    $login_password = trim($_POST['login_password'] ?? '');

    // その他のフィールドの処理（オプションの場合はチェック）
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
    $tweet_enable = isset($_POST['tweet_enable']) ? 1 : 0;
    $paid = isset($_POST['paid']) ? 1 : 0;

    // 入力値のバリデーション
    if (empty($name) || empty($login_id) || empty($login_password)) {
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
            tweet_enable = ?, 
            paid = ?
        WHERE id = ?
    ");

    $stmt->bind_param(
        "ssssssssssiiiiiii", 
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
        $tweet_enable, 
        $paid, 
        $id
    );

    // クエリの実行
    if ($stmt->execute()) {
        echo "<script>alert('更新が完了しました');</script>";
    } else {
        echo "<script>alert('更新に失敗しました: {$stmt->error}');</script>";
    }

    // リソース解放
    $stmt->close();
    $conn->close();

    echo "<script>alert('更新が完了しました');</script>";
    
    // リダイレクト
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
</head>
<body>

    <?php require PARTS_DIR.'/sidebar.php'; ?>

    <!-- コンテンツエリア -->
    <div class="content" id="content">
        <form action="?" method="post">
            <label for="user_id">ユーザーID:</label>
            <input type="text" id="user_id" name="user_id" value="<?php echo htmlspecialchars($edit_account['user_id'] ?? '') ?>" required><br><br>

            <label for="name">名前:</label>
            <input type="text" id="name" name="name" value="<?php echo htmlspecialchars($edit_account['name'] ?? '') ?>" required><br><br>

            <label for="login_id">ログインID:</label>
            <input type="text" id="login_id" name="login_id" value="<?php echo htmlspecialchars($edit_account['login_id'] ?? '') ?>" required><br><br>

            <label for="login_password">パスワード:</label>
            <input type="password" id="login_password" name="login_password" required><br><br>

            <label for="client_id">クライアントID:</label>
            <input type="text" id="client_id" name="client_id" value="<?php echo htmlspecialchars($edit_account['client_id'] ?? '') ?>"><br><br>

            <label for="client_secret">クライアントシークレット:</label>
            <input type="text" id="client_secret" name="client_secret" value="<?php echo htmlspecialchars($edit_account['client_secret'] ?? '') ?>"><br><br>

            <label for="api_key">APIキー:</label>
            <input type="text" id="api_key" name="api_key" value="<?php echo htmlspecialchars($edit_account['api_key'] ?? '') ?>"><br><br>

            <label for="api_key_secret">APIキーシークレット:</label>
            <input type="text" id="api_key_secret" name="api_key_secret" value="<?php echo htmlspecialchars($edit_account['api_key_secret'] ?? '') ?>"><br><br>

            <label for="access_token">アクセストークン:</label>
            <input type="text" id="access_token" name="access_token" value="<?php echo htmlspecialchars($edit_account['access_token'] ?? '') ?>"><br><br>

            <label for="access_token_secret">アクセストークンシークレット:</label>
            <input type="text" id="access_token_secret" name="access_token_secret" value="<?php echo htmlspecialchars($edit_account['access_token_secret'] ?? '') ?>"><br><br>

            <label for="bearer_token">ベアラートークン:</label>
            <input type="text" id="bearer_token" name="bearer_token" value="<?php echo htmlspecialchars($edit_account['bearer_token'] ?? '') ?>"><br><br>

            <label for="refresh_token">リフレッシュトークン:</label>
            <input type="text" id="refresh_token" name="refresh_token" value="<?php echo htmlspecialchars($edit_account['refresh_token'] ?? '') ?>"><br><br>

            <label for="enable">有効:</label>
            <input type="checkbox" id="enable" name="enable" value="1" <?php echo !empty($edit_account['enable']) ? 'checked' : '' ?>><br><br>

            <label for="like_enable">いいね有効:</label>
            <input type="checkbox" id="like_enable" name="like_enable" value="1" <?php echo !empty($edit_account['like_enable']) ? 'checked' : '' ?>><br><br>

            <label for="bookmark_enable">ブックマーク有効:</label>
            <input type="checkbox" id="bookmark_enable" name="bookmark_enable" value="1" <?php echo !empty($edit_account['bookmark_enable']) ? 'checked' : '' ?>><br><br>

            <label for="reply_enable">リプライ有効:</label>
            <input type="checkbox" id="reply_enable" name="reply_enable" value="1" <?php echo !empty($edit_account['reply_enable']) ? 'checked' : '' ?>><br><br>

            <label for="tweet_enable">ツイート有効:</label>
            <input type="checkbox" id="tweet_enable" name="tweet_enable" value="1" <?php echo !empty($edit_account['tweet_enable']) ? 'checked' : '' ?>><br><br>

            <label for="paid">支払い済み:</label>
            <input type="checkbox" id="paid" name="paid" value="1" <?php echo !empty($edit_account['paid']) ? 'checked' : '' ?>><br><br>

            <!-- Reserve 1 -->
            <fieldset>
                <legend>予約1:</legend>
                <label for="reserve1_enable">有効:</label>
                <input type="checkbox" id="reserve1_enable" name="reserve1_enable" value="1" <?php echo !empty($edit_account['reserve1_enable']) ? 'checked' : '' ?>><br><br>
                <label for="reserve1_start_hour">開始時刻:</label>
                <input type="time" id="reserve1_start_hour" name="reserve1_start_hour" value="<?php echo htmlspecialchars($edit_account['reserve1_start_hour'] ?? '') ?>"><br><br>
                <label for="reserve1_end_hour">終了時刻:</label>
                <input type="time" id="reserve1_end_hour" name="reserve1_end_hour" value="<?php echo htmlspecialchars($edit_account['reserve1_end_hour'] ?? '') ?>"><br><br>
                <label for="reserve1_count">カウント:</label>
                <input type="number" id="reserve1_count" name="reserve1_count" value="<?php echo htmlspecialchars($edit_account['reserve1_count'] ?? '') ?>"><br><br>
            </fieldset>

            <!-- 他の予約（Reserve2-4）は同様に追加） -->

            <button type="submit">変更</button>
        </form>
    </div>


</body>
</html>
