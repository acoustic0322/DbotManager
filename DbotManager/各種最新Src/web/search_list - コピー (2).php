<?php
require __DIR__.'/_lib/config.php';
session_start(); // セッションを開始する
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    header("Location: login.php");
    exit;
}

//$current_userid = $_SESSION['user_id'];
$account_id = $_POST['post_account_id'] ?? $_GET['account_id'] ?? null;//$_GET['account_id'];

//echo "<script>alert('{$account_id}');</script>";

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $type = $_POST['type'] ?? '';

    if ($type === 'update') {
        // 送信されたデータを取得
        $id = $_POST['id'];
        $time_enable = isset($_POST["time_enable"]) ? 1 : 0;

        //        $start_hour = $_POST["start_hour"];
//        $end_hour = $_POST["end_hour"];

        $start_hour = isset($_POST['start_hour']) ? (int)$_POST['start_hour'] : 0;
        $end_hour = isset($_POST['end_hour']) ? (int)$_POST['end_hour'] : 24;        

    // SQLクエリの準備
    $stmt = $conn->prepare("
        UPDATE search_list SET 
                time_enable = ?, 
                start_hour = ?, 
                end_hour = ? 
                WHERE id = ?");


        $stmt->bind_param(
            "iiii",
            $time_enable, $start_hour, $end_hour, $id
        );
    
//    echo "<script>alert('{$id}');</script>";
echo $id;
echo $time_enable;
echo $start_hour;
echo $end_hour;

        // SQLクエリ実行
        $stmt->execute();
        $stmt->close();    

        $account_id = isset($_POST['account_id']);

        // 更新成功後、リダイレクト（更新を反映）
//        header("Location: search_list.php?account_id=1");
 //       exit;
    }    
    else if ($type == 'del') {
        $id = $_POST['id'];

        if (empty($id)) {
            echo 'idを指定してください';
            exit;
        }

        // SQLを準備して実行
        $stmt = $conn->prepare("DELETE FROM search_list WHERE id = ?");
        $stmt->bind_param("i", $id);

        if ($stmt->execute()) {
            /* 更新成功 */
        } else {
            /* 更新失敗 */
        }

        $stmt->close();
        $conn->close();

        $account_id = isset($_POST['account_id']);

        // 登録後にリダイレクト
        header("Location: search_list.php?account_id={$account_id}");
        exit;        
    } else {

        $new_account_id = isset($_POST['account_id']);
        $new_search_user_name = str_replace('@', '', $_POST['search_user_name']);
//        $new_search_user_name = "test";
        $new_enable = isset($_POST['enable']) ? 1 : 0;
        $new_post_enable = isset($_POST['post_enable']) ? 1 : 0;
        $new_reply_enable = isset($_POST['reply_enable']) ? 1 : 0;
        $new_monomane_enable = isset($_POST['monomane_enable']) ? 1 : 0;

        $new_time_enable = isset($_POST['time_enable']) ? 1 : 0;
        $new_start_hour = isset($_POST['start_hour']);
        $new_end_hour = isset($_POST['end_hour']);

        // コメントをデータベースに登録
        $stmt = $conn->prepare("INSERT INTO search_list (
            search_user_id, search_user_name, enable, post_enable , reply_enable , monomane_enable, post_account_id , reply_account_id , monomane_account_id ,time_enable,start_hour,end_hour
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ? ,? ,? ,?)");

        $stmt->bind_param(
            "isiiiissssss",
            $_SESSION['user_id'],$new_search_user_name, $new_enable, 
            $new_post_enable, $new_reply_enable, $new_monomane_enable,
            $new_account_id, $new_account_id, $new_account_id ,
            $new_time_enable , $new_start_hour , $new_end_hour
        );

        $stmt->execute();
        $stmt->close();
        $conn->close();

        // 登録後にリダイレクト
        header("Location: search_list.php?account_id={$new_account_id}");
        exit;        
    }
}

$stmt = $conn->prepare("SELECT * FROM search_list WHERE post_account_id = ? ");
$stmt->bind_param("i", $account_id);
$stmt->execute();
$result_check = $stmt->get_result();

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
    
<?php require PARTS_DIR.'/sidebar.php'; ?>6

<div class="content" id="content">
    <h2>新規監視登録</h2>
<!--    <form method="POST" action="?" class="registration-form">  -->
    <form method="POST" action="?">
        <input type="hidden" name="account_id" value="<?php echo htmlspecialchars($account_id); ?>">
        <div class="input-group">
            <input type="checkbox" name="enable" placeholder="有効" checked>有効
        </div>
        <label>
            <input type="checkbox" name="post_enable" value="post_enable" checked>
            監視
        </label>
        <label>
            <input type="checkbox" name="reply_enable" value="reply_enable" checked>
            監視toRep
        </label>
        <label>
            <input type="checkbox" name="monomane_enable" value="monomane_enable" checked>
            モノマネ
        </label>    

        <div class="input-group">
            監視するXユーザー名<br>
            <input type="text" name="search_user_name" required style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px;">
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
    
        <button type="submit">登録</button>
    
    </form>

    <h2>監視一覧</h2>
    <table>
        <thead>
            <tr>
                <th>有効</th>
                <th>監視するXユーザー名</th>
                <th>監視toREP</th>
                <th>監視RepToRep</th>
                <th>モノマネ</th>
                <th>時間帯有効</th>
                <th>開始時間</th>
                <th>終了時間</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result_check->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['enable']) == 1 ? '〇' : '×'; ?></td>
                    <td><?php echo htmlspecialchars($row['search_user_name']); ?></td>
                    <td><?php echo htmlspecialchars($row['post_enable']) == 1 ? '〇' : '×'; ?></td>
                    <td><?php echo htmlspecialchars($row['reply_enable']) == 1 ? '〇' : '×'; ?></td>
                    <td><?php echo htmlspecialchars($row['monomane_enable']) == 1 ? '〇' : '×'; ?></td>

                    <!-- 時間帯有効/無効 -->
                    <td>
                        <input type="checkbox" name="time_enable" value="time_enable" 
                        <?php echo (isset($row['time_enable']) && $row['time_enable'] == 1) ? 'checked' : ''; ?>>
                    </td>
                
                    <!-- 開始時間 -->
                    <td>
                        <input type="number" name="start_hour" min="0" max="24" step="1" 
                        value="<?php echo isset($row['start_hour']) ? htmlspecialchars($row['start_hour']) : 0; ?>" style="width: 50px;">
                    </td>
                
                    <!-- 終了時間 -->
                    <td>
                        <input type="number" name="end_hour" min="0" max="24" step="1" 
                        value="<?php echo isset($row['end_hour']) ? htmlspecialchars($row['end_hour']) : 24; ?>" style="width: 50px;">
                    </td>

                    <td class="hidden"><?php echo htmlspecialchars($row['id']); ?></td>

                    <td>

                        <form class="button_form" method="POST" action="?">
                            <input type="hidden" name="type" value="update">
                            <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                            <input type="hidden" name="start_hour" value="<?php echo htmlspecialchars($row['start_hour']) ?>">
                            <input type="hidden" name="end_hour" value="<?php echo htmlspecialchars($row['end_hour']) ?>">
                            <input type="hidden" name="account_id" value="<?php echo htmlspecialchars($row['post_account_id']) ?>">
                            <button type="submit">保存</button>
                        </form> 

                        <button onclick="editComment(<?php echo $row['id']; ?>)">編集</button>
                        <form class="button_form" method="POST" action="?">
                        <input type="hidden" name="type" value="del">
                        <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                        <input type="hidden" name="search_account_id" value="<?php echo htmlspecialchars($account_id); ?>">
                        <button type="button" onclick="deleteComment(this,<?php echo htmlspecialchars($account_id); ?>)">削除</button>
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
            window.location.href = './search_list_edit.php?id='+id;
        }

        function deleteComment(button,id) {
            button.form.submit();
        }

    </script>

</div>

</body>
</html>
