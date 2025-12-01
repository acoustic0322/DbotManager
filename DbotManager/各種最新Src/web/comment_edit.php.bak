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

$edit_account = get_comment($conn, $id);
if ($edit_account === null) {
    echo 'アカウントが存在しません';
    exit;
}

// POSTリクエストの場合
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // 必須フィールドのサニタイズ
    $comment = htmlspecialchars(trim($_POST['comment'] ?? ''));

    // チェックボックスの値をバインド
    $enable = isset($_POST['enable']) ? 1 : 0;
    $movie_enable = isset($_POST['movie_enable']) ? 1 : 0;
    $photo_enable = isset($_POST['photo_enable']) ? 1 : 0;
    $chatgpt = isset($_POST['chatgpt']) ? 1 : 0;

    /*
    // 判別処理
    if (!empty($_POST['mode'])) {
        if ($_POST['mode'] === 'tweet') {
            $mode = 'tweet';
        } elseif ($_POST['mode'] === 'retweet') {
            $mode = 'retweet';
        } else {
            $mode = null; // デフォルト値
        }
    } else {        
        $mode = null; // POSTに値が含まれていない場合
    }    
        */
    $mode = $_POST['mode'];

    if($_POST['new_mediatype'] == "")
    {
        $movie_enable = 0;
        $photo_enable = 0;
    }
    elseif($_POST['new_mediatype'] == "video")
    {
        $movie_enable = 1;
        $photo_enable = 0;
    }
    else{
        $movie_enable = 0;
        $photo_enable = 1;
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

    // 入力値のバリデーション
//    if (empty($name) || empty($login_id) || empty($login_password)) {
    if (empty($comment) || empty($mode)) {
            echo '必須項目を全て入力してください';
        exit;
    }

    // SQLクエリの準備
    $stmt = $conn->prepare("
        UPDATE comment_master
        SET 
            comment = ?,
            enable = ?, 
            chatgpt = ?, 
            mode = ?, 
            movie_enable = ?, 
            photo_enable = ?,
            reserve_mode = ?
        WHERE id = ?
    ");

    $stmt->bind_param(
        "siisiiii", // 型指定
        $comment,
        $enable , 
        $chatgpt, 
        $mode, 
        $movie_enable, 
        $photo_enable,
        $reserve_mode,
        $id
    );
    
//    echo "<script>alert('{$id}');</script>";

    // SQLクエリ実行
    $stmt->execute();
    $stmt->close();

//    echo "<script>alert('test1');</script>";


    // 登録後にリダイレクト
    header("Location: comment_list.php?account_id={$edit_account['account_id']}");
    exit; 
}

?>

<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>コメント編集</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./css/admin-dashboard.css" /></head>
<body>
  <div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
    <div class="main">
      <h2>コメント編集</h2>
      <form method="POST" action="?">
        <input type="hidden" name="id" value="<?= htmlspecialchars($id) ?>">

        <label><input type="checkbox" name="enable" value="1" <?= !empty($edit_account['enable']) ? 'checked' : '' ?>>有効</label>

        <label>モード:</label>
        <label><input type="radio" name="mode" value="post" <?= $edit_account['mode'] === 'post' ? 'checked' : '' ?>>ポスト</label>
        <label><input type="radio" name="mode" value="reply" <?= $edit_account['mode'] === 'reply' ? 'checked' : '' ?>>リプライ</label>
        <label><input type="radio" name="mode" value="replytoreply" <?= $edit_account['mode'] === 'replytoreply' ? 'checked' : '' ?>>リプライtoリプライ</label>

        <?php if (!empty($_SESSION['media_enable'])): ?>
        <label>動画/画像:</label>
        <label><input type="radio" name="new_mediatype" value="" <?= ($edit_account['movie_enable'] === 0 && $edit_account['photo_enable'] === 0) ? 'checked' : '' ?>>なし</label>
        <label><input type="radio" name="new_mediatype" value="video" <?= $edit_account['movie_enable'] === 1 ? 'checked' : '' ?>>動画</label>
        <label><input type="radio" name="new_mediatype" value="photo" <?= $edit_account['photo_enable'] === 1 ? 'checked' : '' ?>>画像</label>
        <?php endif; ?>

        <label for="comment">コメント:</label>
        <input type="text" id="comment" name="comment" placeholder="コメント" value="<?= htmlspecialchars($edit_account['comment'] ?? '') ?>" required>

        <label for="time_zone_setting">時間帯設定:</label>
        <select name="time_zone_setting" id="time_zone_setting">
          <option value="" <?= $edit_account['reserve_mode'] == 0 ? 'selected' : '' ?>>なし</option>
          <option value="time_zone_1" <?= $edit_account['reserve_mode'] == 1 ? 'selected' : '' ?>>時間帯1</option>
          <option value="time_zone_2" <?= $edit_account['reserve_mode'] == 2 ? 'selected' : '' ?>>時間帯2</option>
          <option value="time_zone_3" <?= $edit_account['reserve_mode'] == 3 ? 'selected' : '' ?>>時間帯3</option>
          <option value="time_zone_4" <?= $edit_account['reserve_mode'] == 4 ? 'selected' : '' ?>>時間帯4</option>
        </select>

        <button class="btn" type="submit">更新</button>
      </form>
    </div>
  </div>
</body>
</html>
