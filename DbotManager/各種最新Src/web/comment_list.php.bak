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
$post_comments = $stmt->get_result();

$stmt = $conn->prepare("SELECT * FROM comment_master WHERE account_id = ? and mode = 'reply'");
$stmt->bind_param("i", $account_id);
$stmt->execute();
$reply_comments = $stmt->get_result();

$stmt = $conn->prepare("SELECT * FROM comment_master WHERE account_id = ? and mode = 'replytoreply'");
$stmt->bind_param("i", $account_id);
$stmt->execute();
$reply_to_reply_comments = $stmt->get_result();

?>

<!DOCTYPE html>
<html lang="ja">

<head>
    <meta charset="UTF-8">
    <title>コメント一覧</title>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="./css/admin-dashboard.css" />

</head>
<body>
  <div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
    
    <div class="main">

      <h2>ポスト一覧</h2>
      <table>
        <tr>
          <th>有効</th>
          <th>コメント</th>
          <?php if (!empty($_SESSION['media_enable'])) echo '<th>動画/画像</th>'; ?>
          <th>時間帯</th>
          <th>操作</th>
        </tr>
        <?php if ($post_comments && $post_comments instanceof mysqli_result): ?>
          <?php while ($row = $post_comments->fetch_assoc()): ?>
          <tr>
            <td><?= $row['enable'] ? '〇' : '×' ?></td>
            <td><?= htmlspecialchars($row['comment']) ?></td>
            <?php if (!empty($_SESSION['media_enable'])): ?>
              <td>
                <?= !empty($row['movie_enable']) ? '動画' : (!empty($row['photo_enable']) ? '画像' : 'なし') ?>
              </td>
            <?php endif; ?>
            <td><?= '時間帯'.$row['reserve_mode'] ?></td>
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
        <?php endif; ?>
      </table>

      <h2>リプライ一覧</h2>
      <table>
        <tr>
          <th>有効</th>
          <th>コメント</th>
          <?php if (!empty($_SESSION['media_enable'])) echo '<th>動画/画像</th>'; ?>
          <th>操作</th>
        </tr>
        <?php if ($reply_comments && $reply_comments instanceof mysqli_result): ?>
          <?php while ($row = $reply_comments->fetch_assoc()): ?>
          <tr>
            <td><?= $row['enable'] ? '〇' : '×' ?></td>
            <td><?= htmlspecialchars($row['comment']) ?></td>
            <?php if (!empty($_SESSION['media_enable'])): ?>
              <td>
                <?= !empty($row['movie_enable']) ? '動画' : (!empty($row['photo_enable']) ? '画像' : 'なし') ?>
              </td>
            <?php endif; ?>
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
        <?php endif; ?>
      </table>

      <h2>リプtoリプ一覧</h2>
      <table>
        <tr>
          <th>有効</th>
          <th>コメント</th>
          <?php if (!empty($_SESSION['media_enable'])) echo '<th>動画/画像</th>'; ?>
          <th>操作</th>
        </tr>
        <?php if ($reply_to_reply_comments && $reply_to_reply_comments instanceof mysqli_result): ?>
          <?php while ($row = $reply_to_reply_comments->fetch_assoc()): ?>
          <tr>
            <td><?= $row['enable'] ? '〇' : '×' ?></td>
            <td><?= htmlspecialchars($row['comment']) ?></td>
            <?php if (!empty($_SESSION['media_enable'])): ?>
              <td>
                <?= !empty($row['movie_enable']) ? '動画' : (!empty($row['photo_enable']) ? '画像' : 'なし') ?>
              </td>
            <?php endif; ?>
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
        <?php endif; ?>
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
