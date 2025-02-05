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
        header("Location: comment_regist.php?account_id={$account_id}");
        exit;        
    } else {

        $new_user_id = $current_userid;
        $new_account_id = $account_id;
        $new_enable = isset($_POST['new_enable']) ? 1 : 0;
        $new_chatgpt = isset($_POST['new_chatgpt']) ? 1 : 0;

        $new_mode = $_POST['new_mode'];
        if($_POST['new_mediatype'] == "")
        {
            $new_movie_enable = 0;
            $new_photo_enable = 0;
        }
        elseif($_POST['new_mediatype'] == "video")
        {
            $new_movie_enable = 1;
            $new_photo_enable = 0;
        }
        else{
            $new_movie_enable = 0;
            $new_photo_enable = 1;
        }

        // 時間帯設定の処理
        $time_zone_setting = $_POST['time_zone_setting'];
        switch ($time_zone_setting) {
            case "":
                $reserve_mode = 0; // なし
                break;
            case "time_zone_1":
                $reserve_mode = 1; // 時間帯1
                break;
            case "time_zone_2":
                $reserve_mode = 2; // 時間帯2
                break;
            case "time_zone_3":
                $reserve_mode = 3; // 時間帯3
                break;
            case "time_zone_4":
                $reserve_mode = 4; // 時間帯4
                break;
            default:
                $reserve_mode = 0; // デフォルト値
        }

        $new_comment1 = $_POST['new_comment1'];
        $new_comment2 = $_POST['new_comment2'];
        $new_comment3 = $_POST['new_comment3'];
        $new_comment4 = $_POST['new_comment4'];
        $new_comment5 = $_POST['new_comment5'];
        $new_comment6 = $_POST['new_comment6'];
        $new_comment7 = $_POST['new_comment7'];
        $new_comment8 = $_POST['new_comment8'];
        $new_comment9 = $_POST['new_comment9'];
        $new_comment10 = $_POST['new_comment10'];

//        echo "<script>alert('new_comment1: {$new_comment1}');</script>"; // デバッグ用
//        echo $new_comment1; // デバッグ用

//        echo "<script>alert('てすと２');</script>";
//        echo $new_comment1;

        // 変数の内容を確認
//        var_dump($new_comment1);

        // $new_modeがnullの場合のエラーハンドリング
        if ($new_mode === null) {
            echo "<script>alert('モードが選択されていません。');</script>";
            exit;
        }    

        // コメントをデータベースに登録
        $stmt = $conn->prepare("INSERT INTO comment_master (
            user_id, account_id, comment, enable, chatgpt, mode, movie_enable, photo_enable, reserve_mode
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)");

        $stmt->bind_param(
            "iisiisiii",
            $new_user_id, $new_account_id, $new_comment, $new_enable, $new_chatgpt,
            $new_mode, $new_movie_enable, $new_photo_enable, $reserve_mode
        );

        if (!empty($new_comment1)) {
            $new_comment = $new_comment1;
            $stmt->execute();
        }
        if (!empty($new_comment2)) {
            $new_comment = $new_comment2;
            $stmt->execute();
        }
        if (!empty($new_comment3)) {
            $new_comment = $new_comment3;
            $stmt->execute();
        }
        if (!empty($new_comment4)) {
            $new_comment = $new_comment4;
            $stmt->execute();
        }
        if (!empty($new_comment5)) {
            $new_comment = $new_comment5;
            $stmt->execute();
        }
        if (!empty($new_comment6)) {
            $new_comment = $new_comment6;
            $stmt->execute();
        }
        if (!empty($new_comment7)) {
            $new_comment = $new_comment7;
            $stmt->execute();
        }
        if (!empty($new_comment8)) {
            $new_comment = $new_comment8;
            $stmt->execute();
        }
        if (!empty($new_comment9)) {
            $new_comment = $new_comment9;
            $stmt->execute();
        }
        if (!empty($new_comment10)) {
            $new_comment = $new_comment10;
            $stmt->execute();
        }


//        $stmt->close();
//        $conn->close();

        // 登録後にリダイレクト
//        header("Location: comment_regist.php?account_id={$account_id}");
//        exit;      

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
        モード
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
        </label><br>

        <?php if (isset($_SESSION['media_enable']) && $_SESSION['media_enable'] == 1): ?>

        動画/画像
        <label>
            <input type="radio" name="new_mediatype" value="" checked>
            なし
        </label>
        <label>
            <input type="radio" name="new_mediatype" value="video">
            動画
        </label>
        <label>
            <input type="radio" name="new_mediatype" value="photo">
            画像
        </label>
        <?php endif; ?>
        <br>


        <!-- 時間帯設定のコンボボックスを追加 -->
        <div class="input-group">
            時間帯設定
            <select name="time_zone_setting">
                <option value="">なし</option>
                <option value="time_zone_1">時間帯1</option>
                <option value="time_zone_2">時間帯2</option>
                <option value="time_zone_3">時間帯3</option>
                <option value="time_zone_4">時間帯4</option>
            </select>
            ※ポスト設定時のみ有効
        </div>

        コメント１
        <div class="input-group">
            <textarea name="new_comment1" rows="3" cols="100" placeholder="コメント１" required style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px; height: 70px;"></textarea>
        </div>
        コメント２
        <div class="input-group">
            <textarea name="new_comment2" placeholder="コメント２" style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px; height: 70px;"></textarea>
        </div>
        コメント３
        <div class="input-group">
            <textarea name="new_comment3" placeholder="コメント３" style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px; height: 70px;"></textarea>
        </div>
        コメント４
        <div class="input-group">
            <textarea name="new_comment4" placeholder="コメント４" style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px; height: 70px;"></textarea>
        </div>
        コメント５
        <div class="input-group">
            <textarea name="new_comment5" placeholder="コメント５" style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px; height: 70px;"></textarea>
        </div>
        コメント６
        <div class="input-group">
            <textarea name="new_comment6" placeholder="コメント６" style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px; height: 70px;"></textarea>
        </div>
        コメント７
        <div class="input-group">
            <textarea name="new_comment7" placeholder="コメント７" style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px; height: 70px;"></textarea>
        </div>
        コメント８
        <div class="input-group">
            <textarea name="new_comment8" placeholder="コメント８" style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px; height: 70px;"></textarea>
        </div>
        コメント９
        <div class="input-group">
            <textarea name="new_comment9" placeholder="コメント９" style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px; height: 70px;"></textarea>
        </div>
        コメント１０
        <div class="input-group">
            <textarea name="new_comment10" placeholder="コメント１０" style="width: 100%; max-width: 600px; padding: 10px; font-size: 16px; height: 70px;"></textarea>
        </div>

        <!--
        <div class="input-group">
            <input type="checkbox" name="new_movie_enable" placeholder="動画">動画
        </div>
        <div class="input-group">
            <input type="checkbox" name="new_photo_enable" placeholder="画像">画像
        </div>
        -->

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
