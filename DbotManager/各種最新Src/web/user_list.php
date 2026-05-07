<?php
require __DIR__.'/_lib/config.php';
session_start(); // セッションを開始する
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    header("Location: login.php");
    exit;
}

if (!isset($_SESSION['admin']) && $_SESSION['admin'] == 1){
    echo '権限が足りません';
    exit;
}

// 新規ユーザー登録処理
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $type = $_POST['type']??'';
    if ($type == 'user_del') {
        $id = $_POST['id'];

        if (empty($id)) {
            echo 'idを指定してください';
            exit;
        }else if ((string)$id === (string)$_SESSION['user_id']) {
            echo '現在のユーザーは削除できません';
            exit;
        }

        // SQLを準備して実行
        $stmt = $conn->prepare("DELETE FROM user_master WHERE id = ?");
        $stmt->bind_param("i", $id);

        if ($stmt->execute()) {
            /* 更新成功 */
        } else {
            /* 更新失敗 */
        }

        $stmt->close();
        $conn->close();

        // 登録後にリダイレクト
        header("Location: user_list.php");
        exit;        
    }
    else if ($type == 'group_update') {
        $client_id_1 = $_POST['client_id_1'];
        $client_secret_1 = $_POST['client_secret_1'];

        $stmt = $conn->prepare("
            UPDATE user_group_master 
            SET client_id_1 = ?, client_secret_1 = ?
            WHERE id = ?
        ");
        $stmt->bind_param("ssi", $client_id_1, $client_secret_1, $_SESSION['group_id']);
        $stmt->execute();
        $stmt->close();

        header("Location: user_list.php");
        exit;
    }    
    else{
        $new_username = $_POST['new_username'];
        $new_password = $_POST['new_password'];
        $is_admin = isset($_POST['is_admin']) ? 1 : 0;

        // 既存のユーザー名を確認
        $stmt = $conn->prepare("SELECT COUNT(*) FROM user_master WHERE username = ? and group_id = ?");
        $stmt->bind_param("ss", $new_username , $_SESSION['group_id']);
        $stmt->execute();
        $stmt->bind_result($count);
        $stmt->fetch();
        $stmt->close();

        // 重複している場合の処理
        if ($count > 0) {
            echo "<script>alert('このユーザー名は既に存在します。別のユーザー名を使用してください。');</script>";
        } else {
            // ユーザーをデータベースに登録
            $stmt = $conn->prepare("INSERT INTO user_master (username, password, admin, group_id) VALUES (?, ?, ?, ?)");
            $stmt->bind_param("ssi", $new_username, $new_password, $is_admin, $_SESSION['group_id']);
            $stmt->execute();
            $stmt->close();
            $conn->close();

            // 登録後にリダイレクト
            header("Location: user_list.php");
            exit;        
        }

    }
}

// ユーザーリストを取得（自分のユーザーを除外）
$current_userid = $_SESSION['user_id'];

//$stmt = $conn->prepare("SELECT * FROM user_master WHERE id != ?");
//$stmt->bind_param("s", $current_userid);
$stmt = $conn->prepare("SELECT * FROM user_master where group_id = ?");
$stmt->bind_param("s", $_SESSION['group_id']);
$stmt->execute();
$result = $stmt->get_result();

$stmt = $conn->prepare("SELECT * FROM user_group_master where id = ?");
$stmt->bind_param("s", $_SESSION['group_id']);
$stmt->execute();
$result_gp = $stmt->get_result();
$row_gp = $result_gp->fetch_assoc();
?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>ユーザー一覧</title>
    <link rel="stylesheet" type="text/css" href="./main.css">
    <style>
        .registration-form {
            display: flex;
            margin-bottom: 20px;
        }
        .registration-form input {
            margin-right: 10px; /* 各入力欄の間にスペースを設ける */
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
    </style>
</head>
<body>

    <?php require PARTS_DIR.'/sidebar.php'; ?>

    <!-- コンテンツエリア -->
    <div class="content" id="content">

   <h2>API設定</h2>
<!--    <form method="POST" action="?" class="registration-form">  -->
    <form method="POST" action="?">
        <input type="hidden" name="type" value="group_update">
        <div>
        ClientID1
        </div>
        <div>
        <input type="text" id="client_id_1" name="client_id_1" placeholder="client_id_1" value="<?php echo htmlspecialchars($row_gp['client_id_1'] ?? '') ?>" style="width:600px;">
        </div>

        <div>
        ClientSecret1
        </div>
        <div>
        <input type="text" id="client_secret_1" name="client_secret_1" placeholder="client_secret_1" value="<?php echo htmlspecialchars($row_gp['client_secret_1'] ?? '') ?>" style="width:600px;">
        </div>

        <!--
        <div>
        ClientID2
        </div>
        <div>
        <input type="text" id="client_id_2" name="client_id_2" placeholder="client_id_2" value="<?php echo htmlspecialchars($row_gp['client_id_2'] ?? '') ?>" style="width:600px;">
        </div>

        <div>
        ClientSecret2
        </div>
        <div>
        <input type="text" id="client_secret_2" name="client_secret_2" placeholder="client_secret_2" value="<?php echo htmlspecialchars($row_gp['client_secret_2'] ?? '') ?>" style="width:600px;">
        </div>

        <div>
        ClientID3
        </div>
        <div>
        <input type="text" id="client_id_3" name="client_id_3" placeholder="client_id_3" value="<?php echo htmlspecialchars($row_gp['client_id_3'] ?? '') ?>" style="width:600px;">
        </div>

        <div>
        ClientSecret3
        </div>
        <div>
        <input type="text" id="client_secret_3" name="client_secret_3" placeholder="client_secret_3" value="<?php echo htmlspecialchars($row_gp['client_secret_3'] ?? '') ?>" style="width:600px;">
        </div>
-->

    <button type="submit">更新</button>
    </form>

   <h2>新規ユーザー登録</h2>
    <form method="POST" action="?" class="registration-form">
        <input type="text" name="new_username" value="<?php echo htmlspecialchars($_POST['new_username']??'') ?>" placeholder="ユーザー名" required>
        <input type="text" name="new_password" placeholder="パスワード" required>
        <label>
            <input type="checkbox" name="is_admin"> 管理者
        </label>
        <button type="button" id="reg_btn">登録</button>
    </form>

    <h2>ユーザー一覧</h2>
    <form method="GET" style="margin-bottom: 20px;">
        <input type="text" name="search" placeholder="ユーザー名で絞り込み" value="<?php echo isset($_GET['search']) ? htmlspecialchars($_GET['search']) : ''; ?>">
        <button type="submit">検索</button>
    </form>

    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>ユーザー名</th>
                <th>パスワード</th> <!-- パスワード列 -->
                <th>管理者</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result->fetch_assoc()): ?>
            <tr>
                <td><?php echo htmlspecialchars($row['id']); ?></td>
                <td><?php echo htmlspecialchars($row['username']); ?></td>
                <td><?php echo htmlspecialchars($row['password']); ?></td> <!-- プレーンテキストのパスワードを表示 -->
                <td><?php echo $row['admin'] ? 'はい' : 'いいえ'; ?></td>
                <td>
                    <button onclick="editUser(<?php echo $row['id']; ?>)">編集</button>
                    <form class="button_form" method="POST" action="?">
                    <input type="hidden" name="type" value="user_del">
                    <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                    <button type="button" onclick="deleteUser(this,<?php echo htmlspecialchars($row['id']) ?>)">削除</button>
                    </form>
                </td>
            </tr>
            <?php endwhile; ?>
        </tbody>
    </table>
    </div>


    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function editUser(id) {
            // 編集機能の実装（必要に応じて）
            alert("ユーザー ID " + id + " を編集します。");
            window.location.href = './user_edit.php?user_id='+id;
        }

        function deleteUser(button,id) {
            if (confirm("ユーザー ID " + id + " を削除します。")) {
                button.form.submit();
            }
        }

    </script>

    <script>
        $(document).ready(function() {
            $("#reg_btn").on("click", function(event) {
                event.preventDefault();
                let form = event.target.closest("form");
                var username = $("input[name='new_username']").val();

                if (form.checkValidity()) {
                    // ユーザー名が空でない場合にチェック
                    if (username) {
                        $.get("./ajax/check_username.php", { username: username }, function(data) {
                            var result = JSON.parse(data);
                            if (result.exists) {
                                alert("このユーザー名は既に存在します。別のユーザー名を使用してください。");
                            } else {
                                form.submit();
                            }
                        });
                    }
                }else{
                    form.reportValidity();
                }
            });
        });
    </script>
 
</body>
</html>
