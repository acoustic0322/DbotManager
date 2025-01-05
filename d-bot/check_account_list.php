<?php
require __DIR__.'/_lib/config.php';
session_start(); // セッションを開始する
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    header("Location: login.php");
    exit;
}

//$current_userid = $_SESSION['user_id'];
$account_id = $_POST['account_id'] ?? $_GET['account_id'] ?? null;//$_GET['account_id'];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $type = $_POST['type'] ?? '';
    if ($type == 'del') {
        $id = $_POST['id'];

        if (empty($id)) {
            echo 'idを指定してください';
            exit;
        }

        // SQLを準備して実行
        $stmt = $conn->prepare("DELETE FROM check_account_list WHERE id = ?");
        $stmt->bind_param("i", $id);

        if ($stmt->execute()) {
            /* 更新成功 */
        } else {
            /* 更新失敗 */
        }

        $stmt->close();
        $conn->close();

        // 登録後にリダイレクト
        header("Location: check_account_list.php?account_id={$account_id}");
        exit;        
    } else {

        $new_account_id = $account_id;
        $new_target_account_name = $_POST['new_target_account_name'];
        $new_enable = isset($_POST['new_enable']) ? 1 : 0;

        /*
        // 判別処理
        if (!empty($_POST['new_mode'])) {
            if ($_POST['new_mode'] === 'check') {
                $new_mode = 'CHECK';
            } elseif ($_POST['new_mode'] === 'checkrep') {
                $new_mode = 'CHECKREP';
            } else {
                $new_mode = null; // デフォルト値
            }
        } else {        
            $new_mode = null; // POSTに値が含まれていない場合
        }
            */

        $new_mode = $_POST['new_mode'];

        // $new_modeがnullの場合のエラーハンドリング
        if ($new_mode === null) {
            echo "<script>alert('モードが選択されていません。');</script>";
            exit;
        }    

        // コメントをデータベースに登録
        $stmt = $conn->prepare("INSERT INTO check_account_list (
            account_id, enable, mode, target_account_name
        ) VALUES (?, ?, ?, ?)");

        $stmt->bind_param(
            "iiss",
            $new_account_id, $new_enable, $new_mode, $new_target_account_name
        );

        $stmt->execute();
        $stmt->close();
        $conn->close();

        // 登録後にリダイレクト
        header("Location: check_account_list.php?account_id={$account_id}");
        exit;        
    }
}

$stmt = $conn->prepare("SELECT * FROM check_account_list WHERE account_id = ? and mode = 'CHECK'");
$stmt->bind_param("i", $account_id);
$stmt->execute();
$result_check = $stmt->get_result();

$stmt = $conn->prepare("SELECT * FROM check_account_list WHERE account_id = ? and mode = 'CHECKREP'");
$stmt->bind_param("i", $account_id);
$stmt->execute();
$result_checkrep = $stmt->get_result();

?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>監視ユーザー一覧</title>
    <link rel="stylesheet" type="text/css" href="./main.css">
    <style>
        .registration-form {
/*            display: flex;*/
            margin-bottom: 20px;
        }
        .registration-form input {
            width: 80%; /* 幅を調整 */
            margin-bottom: 5px; /* 各入力欄の間にスペースを設ける */
            padding: 8px;
            font-size: 12px;
        }
        .registration-form button {
            padding: 8px 12px;
            font-size: 12px;
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

<div class="content" id="content">
    <h2>新規監視登録</h2>
<!--    <form method="POST" action="?" class="registration-form">  -->
    <form method="POST" action="?">
        <input type="hidden" name="account_id" value="<?php echo htmlspecialchars($account_id); ?>">
        <div class="input-group">
            <input type="checkbox" name="new_enable" placeholder="有効" checked>有効
        </div>
        <label>
            <input type="radio" name="new_mode" value="CHECK" checked>
            監視
        </label>
        <label>
            <input type="radio" name="new_mode" value="CHECKREP">
            監視toRep
        </label>
        <div class="input-group">
            アカウント名<br>
            <input type="text" name="new_target_account_name" placeholder="アカウント名" required style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px;">
        </div>
        <button type="submit">登録</button>
    </form>

    <h2>監視対象</h2>
    <table>
        <thead>
            <tr>
                <th>有効</th>
                <th>アカウント名</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result_check->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['enable']) == 1 ? '〇' : '×'; ?></td>
                    <td><?php echo htmlspecialchars($row['target_account_name']); ?></td>
                    <td class="hidden"><?php echo htmlspecialchars($row['id']); ?></td>

                    <td>
                        <button onclick="editComment(<?php echo $row['id']; ?>)">編集</button>
                        <form class="button_form" method="POST" action="?">
                        <input type="hidden" name="type" value="del">
                        <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                        <input type="hidden" name="account_id" value="<?php echo htmlspecialchars($account_id); ?>">
                        <button type="button" onclick="deleteComment(this,<?php echo htmlspecialchars($row['id']) ?>)">削除</button>
                    </form>
                    </td>
                </tr>
            <?php endwhile; ?>
        </tbody>
    </table>

    <h2>監視toRep対象</h2>
    <table>
        <thead>
            <tr>
                <th>有効</th>
                <th>アカウント名</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result_checkrep->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['enable']) == 1 ? '〇' : '×'; ?></td>
                    <td><?php echo htmlspecialchars($row['target_account_name']); ?></td>
                    <td class="hidden"><?php echo htmlspecialchars($row['id']); ?></td>

                    <td>
                        <button onclick="editComment(<?php echo $row['id']; ?>)">編集</button>
                        <form class="button_form" method="POST" action="?">
                        <input type="hidden" name="type" value="del">
                        <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                        <input type="hidden" name="account_id" value="<?php echo htmlspecialchars($account_id); ?>">
                        <button type="button" onclick="deleteComment(this,<?php echo htmlspecialchars($row['id']) ?>)">削除</button>
                    </form>
                    </td>
                </tr>
            <?php endwhile; ?>
        </tbody>
    </table>

    <style>
    .hidden {
        display: none;
    }
    </style>

    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function editComment(id) {
            window.location.href = './check_account_edit.php?id='+id;
        }

        function deleteComment(button,id) {
            button.form.submit();
        }

    </script>

</div>

</body>
</html>
