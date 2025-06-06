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

$edit_account = get_search_list_row($conn, $id);
if ($edit_account === null) {
    echo 'アカウントが存在しません';
    exit;
}

$account_id = $edit_account['post_account_id'] ?? null;

// POSTリクエストの場合
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

//echo "<script>alert('{$account_id}');</script>";


    $new_account_id = $edit_account['post_account_id'];
    $new_search_user_name = $_POST['search_user_name'];
//        $new_search_user_name = "test";
    $new_enable = isset($_POST['enable']) ? 1 : 0;
    $new_post_enable = isset($_POST['post_enable']) ? 1 : 0;
    $new_reply_enable = isset($_POST['reply_enable']) ? 1 : 0;
    $new_monomane_enable = isset($_POST['monomane_enable']) ? 1 : 0;

    $new_time_enable = isset($_POST['time_enable']) ? 1 : 0;
    $new_start_hour = isset($_POST['start_hour']) ? (int)$_POST['start_hour'] : 0;
    $new_end_hour = isset($_POST['end_hour']) ? (int)$_POST['end_hour'] : 24;    

    // SQLクエリの準備
    $stmt = $conn->prepare("
        UPDATE search_list
        SET 
            search_user_name = ?,
            enable = ?,
            post_enable = ? ,
            reply_enable = ? ,
            monomane_enable = ?, 
            post_account_id = ? , 
            reply_account_id = ? , 
            monomane_account_id  = ? ,
            time_enable = ? ,
            start_hour = ? ,
            end_hour = ?
        WHERE id = ?
    ");

    $stmt->bind_param(
        "siiiisssssss",
        $new_search_user_name, $new_enable, 
        $new_post_enable, $new_reply_enable, $new_monomane_enable,
        $new_account_id, $new_account_id, $new_account_id,
        $new_time_enable , $new_start_hour , $new_end_hour ,
        $id
    );
    
//    echo "<script>alert('{$id}');</script>";

    // SQLクエリ実行
    $stmt->execute();
    $stmt->close();

//    echo "<script>alert('test1');</script>";


    // 登録後にリダイレクト
    header("Location: search_list.php?account_id={$edit_account['post_account_id']}");
    exit; 
}

?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Xアカウント編集</title>
    <link rel="stylesheet" href="_lib/style.css">

</head>
<body>
<div class="layout">

    <?php require PARTS_DIR.'/sidebar.php'; ?>
  <div class="main">

    <!-- コンテンツエリア -->
    <div class="content" id="content">
<!--        <form action="?" method="post">  -->
<!--        <form method="POST" action="?" class="registration-form">-->

    <form method="POST" action="?">
        <input type="hidden" name="search_account_id" value="<?php echo htmlspecialchars($account_id); ?>">
        <div class="input-group">
            <input type="checkbox" name="enable" placeholder="有効"  <?php echo ($edit_account['enable'] === 1) ? 'checked' : ''; ?> >有効
        </div>
        <label>
            <input type="checkbox" name="post_enable" value="post_enable" <?php echo ($edit_account['post_enable'] === 1) ? 'checked' : ''; ?>>
            監視
        </label>
        <label>
            <input type="checkbox" name="reply_enable" value="reply_enable" <?php echo ($edit_account['reply_enable'] === 1) ? 'checked' : ''; ?>>
            監視toRep
        </label>
        <label>
            <input type="checkbox" name="monomane_enable" value="monomane_enable" <?php echo ($edit_account['monomane_enable'] === 1) ? 'checked' : ''; ?>>
            モノマネ
        </label>    

        <div class="input-group">
            監視するXユーザー名<br>
            <input type="text" name="search_user_name" value="<?php echo htmlspecialchars($edit_account['search_user_name'] ?? '') ?>" required style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px;">
        </div>

        <!-- 時間帯有効/無効チェックボックス -->
        <div class="input-group">
            <label>
                <input type="checkbox" name="time_enable" value="time_enable">
                時間帯有効
            </label>
        </div>

        <!-- 開始時間 -->
        <div class="input-group">
            <label for="start_time">開始時間 (0～24):</label>
            <input type="number" id="start_hour" name="start_hour" min="0" max="24" step="1" value="0" style="width: 50px;">
        </div>

        <!-- 終了時間 -->
        <div class="input-group">
            <label for="end_time">終了時間 (0～24):</label>
            <input type="number" id="end_hour" name="end_hour" min="0" max="24" step="1" value="24" style="width: 50px;">
        </div>         

        <input type="hidden" name="account_id" value="<?php echo htmlspecialchars($id); ?>">
        <input type="hidden" name="id" value="<?php echo htmlspecialchars($id); ?>">
        <button type="submit">更新</button>

    </form>
    </div>
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

</body>
</html>
