<?php
require __DIR__.'/_lib/config.php';
session_start(); // セッションを開始する
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    header("Location: login.php");
    exit;
}

$current_userid = $_SESSION['user_id'];
$account_id = $_POST['account_id'] ?? $_GET['account_id'] ?? null;//$_GET['account_id'];

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
        header("Location: comment_list.php?account_id={$account_id}");
        exit;        
    }
}

$stmt = $conn->prepare("SELECT * FROM comment_master WHERE account_id = ? and mode = 'post'");
$stmt->bind_param("i", $account_id);
$stmt->execute();
$result_post = $stmt->get_result();

$stmt = $conn->prepare("SELECT * FROM comment_master WHERE account_id = ? and mode = 'reply'");
$stmt->bind_param("i", $account_id);
$stmt->execute();
$result_reply = $stmt->get_result();

$stmt = $conn->prepare("SELECT * FROM comment_master WHERE account_id = ? and mode = 'replytoreply'");
$stmt->bind_param("i", $account_id);
$stmt->execute();
$result_replytoreply = $stmt->get_result();

?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>コメント一覧</title>
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
    <h2>ポスト一覧</h2>
    <table>
        <thead>
            <tr>
                <th>有効</th>
                <th>コメント</th>
                <?php if (isset($_SESSION['media_enable']) && $_SESSION['media_enable'] == 1): ?>
                <th>動画/画像</th>
                <?php endif; ?>                
                <th>時間帯</th>

                <!--                <th>ChatGPT</th>-->
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result_post->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['enable']) == 1 ? '〇' : '×'; ?></td>
                    <td><?php echo htmlspecialchars($row['comment']); ?></td>

                    <?php if (isset($_SESSION['media_enable']) && $_SESSION['media_enable'] == 1): ?>
                            <td><?php echo htmlspecialchars($row['movie_enable']) == 1 ? '動画' : (htmlspecialchars($row['photo_enable']) == 1 ? '画像' : 'なし'); ?></td>
                    <?php endif; ?>               

                    <!-- 時間帯の表示 -->
                    <td>
                        <?php 
                        switch ($row['reserve_mode']) {
                            case 1:
                                echo "時間帯1";
                                break;
                            case 2:
                                echo "時間帯2";
                                break;
                            case 3:
                                echo "時間帯3";
                                break;
                            case 4:
                                echo "時間帯4";
                                break;
                            default:
                                echo "なし";
                                break;
                        }
                        ?>
                    </td>

                    <!-- 隠し要素 -->                     
                    <td class="hidden"><?php echo htmlspecialchars($row['chatgpt']) == 1 ? '〇' : '×'; ?></td>
                    <td class="hidden"><?php echo htmlspecialchars($row['id']); ?></td>

                    <td>
                        <button onclick="editComment(<?php echo $row['id']; ?>)">編集</button>
                        <form class="button_form" method="POST" action="?">
                        <input type="hidden" name="type" value="comment_del">
                        <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                        <input type="hidden" name="account_id" value="<?php echo htmlspecialchars($account_id); ?>">
                        <button type="button" onclick="deleteComment(this,<?php echo htmlspecialchars($row['id']) ?>)">削除</button>
                    </form>
                    </td>
                </tr>
            <?php endwhile; ?>
        </tbody>
    </table>

    <h2>リプライ一覧</h2>
    <table>
        <thead>
            <tr>
                <th>有効</th>
                <th>コメント</th>
                <?php if (isset($_SESSION['media_enable']) && $_SESSION['media_enable'] == 1): ?>
                <th>動画/画像</th>
                <?php endif; ?>   
<!--                <th>ChatGPT</th> -->
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result_reply->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['enable']) == 1 ? '〇' : '×'; ?></td>
                    <td><?php echo htmlspecialchars($row['comment']); ?></td>

                    <?php if (isset($_SESSION['movie_enable']) && $_SESSION['movie_enable'] == 1): ?>
                    <?php if (isset($_SESSION['photo_enable']) && $_SESSION['photo_enable'] == 1): ?>
                            <td><?php echo htmlspecialchars($row['movie_enable']) == 1 ? '動画' : (htmlspecialchars($row['photo_enable']) == 1 ? '画像' : 'なし'); ?></td>
                    <?php endif; ?>                
                    <?php endif; ?>                

                    <td class="hidden"><?php echo htmlspecialchars($row['chatgpt']) == 1 ? '〇' : '×'; ?></td>
                    <td class="hidden"><?php echo htmlspecialchars($row['id']); ?></td>

                    <td>
                        <button onclick="editComment(<?php echo $row['id']; ?>)">編集</button>
                        <form class="button_form" method="POST" action="?">
                        <input type="hidden" name="type" value="comment_del">
                        <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                        <input type="hidden" name="account_id" value="<?php echo htmlspecialchars($account_id); ?>">
                        <button type="button" onclick="deleteComment(this,<?php echo htmlspecialchars($row['id']) ?>)">削除</button>
                    </form>
                    </td>
                </tr>
            <?php endwhile; ?>
        </tbody>
    </table>

    <h2>リプライtoリプライ一覧</h2>
    <table>
        <thead>
            <tr>
                <th>有効</th>
                <th>コメント</th>
                <?php if (isset($_SESSION['movie_enable']) && $_SESSION['movie_enable'] == 1): ?>
                <?php if (isset($_SESSION['photo_enable']) && $_SESSION['photo_enable'] == 1): ?>
                <th>動画/画像</th>
                <?php endif; ?>
                <?php endif; ?> 
<!--                <th>ChatGPT</th> -->
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result_replytoreply->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['enable']) == 1 ? '〇' : '×'; ?></td>
                    <td><?php echo htmlspecialchars($row['comment']); ?></td>

                    <?php if (isset($_SESSION['media_enable']) && $_SESSION['media_enable'] == 1): ?>
                            <td><?php echo htmlspecialchars($row['movie_enable']) == 1 ? '動画' : (htmlspecialchars($row['photo_enable']) == 1 ? '画像' : 'なし'); ?></td>
                    <?php endif; ?>                

                    <td class="hidden"><?php echo htmlspecialchars($row['chatgpt']) == 1 ? '〇' : '×'; ?></td>
                    <td class="hidden"><?php echo htmlspecialchars($row['id']); ?></td>

                    <td>
                        <button onclick="editComment(<?php echo $row['id']; ?>)">編集</button>
                        <form class="button_form" method="POST" action="?">
                        <input type="hidden" name="type" value="comment_del">
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
            window.location.href = './comment_edit.php?id='+id;
        }

        function deleteComment(button,id) {
            button.form.submit();
        }

    </script>

</div>

</body>
</html>
