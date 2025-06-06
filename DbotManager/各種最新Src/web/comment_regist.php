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
  <title>コメント登録</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./css/admin-dashboard.css" />
</head>
<body class="comment-regist-page">
  <div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
    <div class="main">
      <h2>新規コメント登録</h2>
      <form method="POST" action="?">
        <input type="hidden" name="account_id" value="<?= htmlspecialchars($account_id) ?>">

        <p><label><input type="checkbox" name="new_enable" checked>有効</label></p>

        <div class="mode-row">
          <span>モード:</span>
          <div class="radio-group">
            <label><input type="radio" name="new_mode" value="post" checked>ポスト</label>
            <label><input type="radio" name="new_mode" value="reply">リプライ</label>
            <label><input type="radio" name="new_mode" value="replytoreply">リプライtoリプライ</label>
          </div>
        </div>

        <?php if (!empty($_SESSION['media_enable'])): ?>
        <div class="mode-row">
          <span>メディア:</span>
          <div class="radio-group">
            <label><input type="radio" name="new_mediatype" value="" checked>なし</label>
            <label><input type="radio" name="new_mediatype" value="video">動画</label>
            <label><input type="radio" name="new_mediatype" value="photo">画像</label>
          </div>
        </div>
        <?php endif; ?>

        <p>
          時間帯:
          <select name="time_zone_setting">
            <option value="">なし</option>
            <option value="time_zone_1">時間帯1</option>
            <option value="time_zone_2">時間帯2</option>
            <option value="time_zone_3">時間帯3</option>
            <option value="time_zone_4">時間帯4</option>
          </select>
        </p>

<div class="comment-grid">
  <?php for ($i = 1; $i <= 10; $i++): ?>
    <div class="comment-item">
      <label for="new_comment<?= $i ?>">コメント<?= $i ?></label>
      <textarea name="new_comment<?= $i ?>" id="new_comment<?= $i ?>" placeholder="コメント<?= $i ?>"></textarea>
    </div>
  <?php endfor; ?>
</div>

        <button class="btn" type="submit">登録</button>
      </form>

      <h2 class="tx-white">ポスト一覧</h2>
      <table>
        <thead>
          <tr>
            <th>有効</th>
            <th>コメント</th>
            <?php if (!empty($_SESSION['media_enable'])): ?><th>メディア</th><?php endif; ?>
            <th>時間帯</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody>
          <?php while ($row = $result_post->fetch_assoc()): ?>
          <tr>
            <td><?= $row['enable'] ? '〇' : '×' ?></td>
            <td><?= htmlspecialchars($row['comment']) ?></td>
            <?php if (!empty($_SESSION['media_enable'])): ?>
              <td><?= $row['movie_enable'] ? '動画' : ($row['photo_enable'] ? '画像' : 'なし') ?></td>
            <?php endif; ?>
            <td>
              <?php
                echo match((int)$row['reserve_mode']) {
                  1 => '時間帯1',
                  2 => '時間帯2',
                  3 => '時間帯3',
                  4 => '時間帯4',
                  default => 'なし',
                };
              ?>
            </td>
            <td>
              <button class="btn" onclick="editComment(<?= $row['id'] ?>)">編集</button>
              <form method="POST" action="?" style="display:inline;">
                <input type="hidden" name="type" value="comment_del">
                <input type="hidden" name="id" value="<?= $row['id'] ?>">
                <input type="hidden" name="account_id" value="<?= $account_id ?>">
                <button type="submit" class="btn" onclick="return confirm('削除しますか？')">削除</button>
              </form>
            </td>
          </tr>
          <?php endwhile; ?>
        </tbody>
      </table>
    </div>
  </div>
  <script>
    function editComment(id) {
      location.href = './comment_edit.php?id=' + id;
    }
  </script>
</body>
</html>
