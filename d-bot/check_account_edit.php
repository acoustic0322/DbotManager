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

$edit_account = get_check_account($conn, $id);
if ($edit_account === null) {
    echo 'アカウントが存在しません';
    exit;
}

// POSTリクエストの場合
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // 必須フィールドのサニタイズ
    $check_account = htmlspecialchars(trim($_POST['check_account'] ?? ''));
    // チェックボックスの値をバインド
    $enable = isset($_POST['enable']) ? 1 : 0;

    /*
    // 判別処理
    if (!empty($_POST['mode'])) {
        if ($_POST['mode'] === 'check') {
            $mode = 'check';
        } elseif ($_POST['mode'] === 'checkrep') {
            $mode = 'checkrep';
        } else {
            $mode = null; // デフォルト値
        }
    } else {        
        $mode = null; // POSTに値が含まれていない場合
    } 
        */
    
    $mode = $_POST['mode'];

    // 入力値のバリデーション
//    if (empty($name) || empty($login_id) || empty($login_password)) {
    if (empty($check_account) || empty($mode)) {
            echo '必須項目を全て入力してください';
        exit;
    }

    // SQLクエリの準備
    $stmt = $conn->prepare("
        UPDATE check_account_list
        SET 
            enable = ?,
            mode = ?,
            check_account = ?
        WHERE id = ?
    ");

    $stmt->bind_param(
        "issi", // 型指定
        $enable , 
        $mode, 
        $check_account,
        $id
    );
    
//    echo "<script>alert('{$id}');</script>";

    // SQLクエリ実行
    $stmt->execute();
    $stmt->close();

//    echo "<script>alert('test1');</script>";


    // 登録後にリダイレクト
    header("Location: check_account_list.php?account_id={$edit_account['account_id']}");
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

            <div class="input-group" checkbox-group">

                <label>
                    <input type="checkbox" name="enable" value="1" <?php echo !empty($edit_account['enable']) ? 'checked' : '' ?>>有効
                </label><br>

                <label>
                    <input type="radio" name="mode" value="CHECK" <?php echo ($edit_account['mode'] === 'CHECK') ? 'checked' : ''; ?>> 監視
                </label>
                <br>
                <label>
                    <input type="radio" name="mode" value="CHECKREP" <?php echo ($edit_account['mode'] === 'CHECKREP') ? 'checked' : ''; ?>> 監視toREP
                </label>
                <br>            
            </div>

            <div class="input-group">
                <label for="name">アカウント名:</label><br>
                <input type="text" id="check_account" name="check_account" placeholder="アカウント名" value="<?php echo htmlspecialchars($edit_account['check_account'] ?? '') ?>" required>
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

</body>
</html>
