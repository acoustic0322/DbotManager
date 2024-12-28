<?php
require __DIR__.'/_lib/config.php';
session_start(); // セッションを開始する
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    header("Location: login.php");
    exit;
}

$current_userid = $_SESSION['user_id'];

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $type = $_POST['type'] ?? '';
    if ($type == 'comment_del') {
        $id = $_POST['id'];

        if (empty($id)) {
            echo 'idを指定してください';
            exit;
        }

        // SQLを準備して実行
        $stmt = $conn->prepare("DELETE FROM comment_master WHERE id = ?");
        $stmt->bind_param("i", $id);

        if ($stmt->execute()) {
            /* 更新成功 */
        } else {
            /* 更新失敗 */
        }

        $stmt->close();
        $conn->close();

        // 登録後にリダイレクト
        header("Location: comment_list.php");
        exit;        
    } else {

        $new_user_id = $current_userid;
        $new_account_id = $_POST['new_account_id'];
        $new_comment = $_POST['new_comment'];
        $new_enable = $_POST['new_enable'] ?? 1;
        $new_chatgpt = $_POST['new_chatgpt'] ?? 1;
        $new_mode = $_POST['new_mode'];
        $new_movie_enable = $_POST['new_movie_enable'] ?? 0;
        $new_photo_enable = $_POST['new_photo_enable'] ?? 0;

        // コメントをデータベースに登録
        $stmt = $conn->prepare("INSERT INTO comment_master (
            user_id, account_id, comment, enable, chatgpt, mode, movie_enable, photo_enable
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");

        $stmt->bind_param(
            "iisiiiii",
            $new_user_id, $new_account_id, $new_comment, $new_enable, $new_chatgpt,
            $new_mode, $new_movie_enable, $new_photo_enable
        );

        if ($stmt->execute()) {
            echo "<script>alert('\u30b3\u30e1\u30f3\u30c8\u304c\u767b\u9332\u3055\u308c\u307e\u3057\u305f\u3002');</script>";
        } else {
            echo "<script>alert('\u30b3\u30e1\u30f3\u30c8\u306e\u767b\u9332\u306b\u5931\u6557\u3057\u307e\u3057\u305f\u3002');</script>";
        }

        $stmt->close();
        $conn->close();

        // 登録後にリダイレクト
        header("Location: comment_list.php");
        exit;        
    }
}

$stmt = $conn->prepare("SELECT * FROM comment_master WHERE user_id = ?");
$stmt->bind_param("i", $current_userid);
$stmt->execute();
$result = $stmt->get_result();
?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>コメント一覧</title>
    <link rel="stylesheet" type="text/css" href="./main.css">
    <style>
        .registration-form {
            margin-bottom: 20px;
        }
        .registration-form input {
            width: 100%;
            margin-bottom: 5px;
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
    </style>
</head>
<body>
    
<?php require PARTS_DIR.'/sidebar.php'; ?>

<div class="content" id="content">
    <h2>新規コメント登録</h2>
    <form method="POST" action="?" class="registration-form">
    <div class="input-group">
            <input type="text" name="new_account_id" placeholder="アカウントID" required>
        </div>
        <div class="input-group">
            <textarea name="new_comment" placeholder="コメント" required></textarea>
        </div>
        <div class="input-group">
            <input type="text" name="new_mode" placeholder="モード">
        </div>
        <div class="input-group">
            <input type="number" name="new_movie_enable" placeholder="ムービー有効">
        </div>
        <div class="input-group">
            <input type="number" name="new_photo_enable" placeholder="フォト有効">
        </div>

        <button type="submit">登録</button>
    </form>

    <h2>コメント一覧</h2>
    <table>
        <thead>
            <tr>
                <th>ID</th>
                <th>コメント</th>
                <th>アカウントID</th>
                <th>モード</th>
                <th>有効</th>
                <th>ChatGPT</th>
                <th>ムービー有効</th>
                <th>フォト有効</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['id']); ?></td>
                    <td><?php echo htmlspecialchars($row['comment']); ?></td>
                    <td><?php echo htmlspecialchars($row['account_id']); ?></td>
                    <td><?php echo htmlspecialchars($row['mode']); ?></td>
                    <td><?php echo htmlspecialchars($row['enable']); ?></td>
                    <td><?php echo htmlspecialchars($row['chatgpt']); ?></td>
                    <td><?php echo htmlspecialchars($row['movie_enable']); ?></td>
                    <td><?php echo htmlspecialchars($row['photo_enable']); ?></td>
                </tr>
            <?php endwhile; ?>
        </tbody>
    </table>
</div>

</body>
</html>
