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
    } else {

        $new_user_id = $current_userid;
        $new_account_id = $account_id;
        $new_comment = $_POST['new_comment'];
        $new_enable = isset($_POST['new_enable']) ? 1 : 0;
        $new_chatgpt = isset($_POST['new_chatgpt']) ? 1 : 0;
//        $new_mode = $_POST['new_mode'];
        $new_movie_enable = isset($_POST['new_movie_enable']) ? 1 : 0;
        $new_photo_enable = isset($_POST['new_photo_enable']) ? 1 : 0;

//        $new_mode = $_POST['new_mode'] ?? '';

        /*
        // 判別処理
        if (!empty($_POST['new_mode'])) {
            if ($_POST['new_mode'] === 'post') {
                $new_mode = 'tweet';
            } elseif ($_POST['new_mode'] === 'reply') {
                $new_mode = 'retweet';
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
        $stmt = $conn->prepare("INSERT INTO comment_master (
            user_id, account_id, comment, enable, chatgpt, mode, movie_enable, photo_enable
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)");

        $stmt->bind_param(
            "iisiisii",
            $new_user_id, $new_account_id, $new_comment, $new_enable, $new_chatgpt,
            $new_mode, $new_movie_enable, $new_photo_enable
        );

        /*

        if ($stmt->execute()) {
            echo "<script>alert('\u30b3\u30e1\u30f3\u30c8\u304c\u767b\u9332\u3055\u308c\u307e\u3057\u305f\u3002');</script>";
        } else {
            echo "<script>alert('\u30b3\u30e1\u30f3\u30c8\u306e\u767b\u9332\u306b\u5931\u6557\u3057\u307e\u3057\u305f\u3002');</script>";
        }
            */

        $stmt->execute();
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
    <h2>新規コメント登録</h2>
<!--    <form method="POST" action="?" class="registration-form">  -->
    <form method="POST" action="?">
        <input type="hidden" name="account_id" value="<?php echo htmlspecialchars($account_id); ?>">
        <div class="input-group">
            <input type="checkbox" name="new_enable" placeholder="有効" checked>有効
        </div>
        <label>
            <input type="radio" name="new_mode" value="post" checked>
            ポスト
        </label>
        <label>
            <input type="radio" name="new_mode" value="reply">
            リプライ
        </label>
        <label>
            <input type="radio" name="new_mode" value="replytoreply">
            リプライtoリプライ
        </label>
        <div class="input-group">
            コメント<br>
            <input type="text" name="new_comment" placeholder="コメント" required style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px;">
        </div>
        <div class="input-group">
            <input type="checkbox" name="new_movie_enable" placeholder="動画">動画
        </div>
        <div class="input-group">
            <input type="checkbox" name="new_photo_enable" placeholder="画像">画像
        </div>
        <!--
        <div class="input-group">
            <input type="checkbox" name="new_photo_enable" placeholder="ChatGPT(開発予定)">ChatGPT(開発予定)
        </div>
    -->

        <button type="submit">登録</button>
    </form>

    <h2>ポスト一覧</h2>
    <table>
        <thead>
            <tr>
                <th>有効</th>
                <th>コメント</th>
                <?php if (isset($_SESSION['movie_enable']) && $_SESSION['movie_enable'] == 1): ?>
                <th>動画</th>
                <?php endif; ?>
                <?php if (isset($_SESSION['photo_enable']) && $_SESSION['photo_enable'] == 1): ?>
                <th>画像</th>
                <?php endif; ?>                
<!--                <th>ChatGPT</th>-->
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result_post->fetch_assoc()): ?>
                <tr>
                    <td><?php echo htmlspecialchars($row['enable']) == 1 ? '〇' : '×'; ?></td>
                    <td><?php echo htmlspecialchars($row['comment']); ?></td>
                    <?php if (isset($_SESSION['movie_enable']) && $_SESSION['movie_enable'] == 1): ?>
                        <td><?php echo htmlspecialchars($row['movie_enable']) == 1 ? '〇' : '×'; ?></td>
                    <?php endif; ?>                
                    <?php if (isset($_SESSION['photo_enable']) && $_SESSION['photo_enable'] == 1): ?>
                        <td><?php echo htmlspecialchars($row['photo_enable']) == 1 ? '〇' : '×'; ?></td>
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

    <h2>リプライ一覧</h2>
    <table>
        <thead>
            <tr>
                <th>有効</th>
                <th>コメント</th>
                <?php if (isset($_SESSION['movie_enable']) && $_SESSION['movie_enable'] == 1): ?>
                <th>動画</th>
                <?php endif; ?>
                <?php if (isset($_SESSION['photo_enable']) && $_SESSION['photo_enable'] == 1): ?>
                <th>画像</th>
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
                        <td><?php echo htmlspecialchars($row['movie_enable']) == 1 ? '〇' : '×'; ?></td>
                    <?php endif; ?>                
                    <?php if (isset($_SESSION['photo_enable']) && $_SESSION['photo_enable'] == 1): ?>
                        <td><?php echo htmlspecialchars($row['photo_enable']) == 1 ? '〇' : '×'; ?></td>
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
                <th>動画</th>
                <?php endif; ?>
                <?php if (isset($_SESSION['photo_enable']) && $_SESSION['photo_enable'] == 1): ?>
                <th>画像</th>
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
                    <?php if (isset($_SESSION['movie_enable']) && $_SESSION['movie_enable'] == 1): ?>
                        <td><?php echo htmlspecialchars($row['movie_enable']) == 1 ? '〇' : '×'; ?></td>
                    <?php endif; ?>                
                    <?php if (isset($_SESSION['photo_enable']) && $_SESSION['photo_enable'] == 1): ?>
                        <td><?php echo htmlspecialchars($row['photo_enable']) == 1 ? '〇' : '×'; ?></td>
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
