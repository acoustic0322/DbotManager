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

$edit_account = get_account($conn, $id);
if ($edit_account === null) {
    echo 'アカウントが存在しません';
    exit;
}

//echo $edit_account['ai_post_prompt'];

// プロンプトプリセットのリストを取得
$stmt = $conn->prepare("SELECT id, type, mode , name, prompt , example FROM prompt_master");
$stmt->execute();
$result = $stmt->get_result();
$stmt->close();

$presets = [];
while ($row = $result->fetch_assoc()) {
    $presets[] = $row;
}

// POSTリクエストの場合
if ($_SERVER['REQUEST_METHOD'] === 'POST') {

    // 必須フィールドのサニタイズ
    $name = htmlspecialchars(trim($_POST['name'] ?? ''));
    $login_id = htmlspecialchars(trim($_POST['login_id'] ?? ''));

    // チェックボックスの値をバインド
    $enable = isset($_POST['enable']) ? 1 : 0;
    $proxy_enable = isset($_POST['proxy_enable']) ? 1 : 0;
    $proxy_url = $_POST['proxy_url'];

    // 入力値のバリデーション
//    if (empty($name) || empty($login_id) || empty($login_password)) {
    if (empty($name) || empty($login_id)) {
            echo '必須項目を全て入力してください';
        exit;
    }

    // SQLクエリの準備
    $stmt = $conn->prepare("
        UPDATE account_master
        SET 
            name = ?, 
            login_id = ?, 
            proxy_enable = ? ,
            proxy_url = ? ,
        WHERE id = ?
    ");

    $stmt->bind_param(
        "sssss", // 型指定
        $name, 
        $login_id, 
        $proxy_enable ,
        $proxy_url ,
        $id
    );
    
    // SQLクエリ実行
    $stmt->execute();
    $stmt->close();

    // 登録後にリダイレクト
    header("Location: account_list.php");
    exit; 
}

?>

<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>Xアカウント編集</title>
  <link rel="stylesheet" href="./css/admin-dashboard.css" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
  <div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>

   <div class="content" id="content">
<!--      <div class="card"> -->
        <h2 class="tx-white">Xアカウント編集</h2>

    <?php
        $profile_image_path = "img/profile/" . htmlspecialchars($edit_account['id']) . ".jpg";
        $login_id = htmlspecialchars($edit_account['login_id']);
        $x_link = "https://x.com/" . urlencode($login_id);
        ?>
        <div style="display: flex; align-items: center; gap: 12px; margin-bottom: 20px;">
          <img src="<?= $profile_image_path ?>"
               alt="アイコン"
               onerror="this.onerror=null;this.src='img/profile/noimage/noimage.jpg';"
               style="width: 72px; height: 72px; border-radius: 50%; object-fit: cover; border: 2px solid #ccc;">

          <div style="font-size: 16px; font-style: italic;">
            <a href="<?= $x_link ?>"
               target="_blank"
               style="color: #d4af37; text-decoration: none;"
               onmouseover="this.style.textDecoration='underline'"
               onmouseout="this.style.textDecoration='none'">
              @<?= $login_id ?>
            </a>
          </div>
        </div>
        
        <form method="POST" action="?">
          <label>名前</label>
          <input type="text" name="name" value="<?= htmlspecialchars($edit_account['name'] ?? '') ?>">

          <label>XアカウントID</label>
          <input type="text" name="login_id" value="<?= htmlspecialchars($edit_account['login_id'] ?? '') ?>">


          <?php
            $hide = !empty($edit_account['id'])
                && isset($_SESSION['hide_sensitive_fields'])
                && (int)$_SESSION['hide_sensitive_fields'] === 1; ?>

          <?php if (!$hide): ?>
          <label>プロキシ使用 <input type="checkbox" name="proxy_enable" value="1" <?= !empty($edit_account['proxy_enable']) ? 'checked' : '' ?>></label>
          <label>プロキシURL</label>
          <input type="text" name="proxy_url" value="<?= htmlspecialchars($edit_account['proxy_url'] ?? '') ?>">
          <?php else: ?>
          <input type="hidden" name="proxy_enable" value="<?= !empty($edit_account['proxy_enable']) ? 1 : 0 ?>">
          <input type="hidden" name="proxy_url" value="<?= htmlspecialchars($edit_account['proxy_url'] ?? '') ?>">
          <?php endif; ?>

          <input type="hidden" name="id" value="<?= htmlspecialchars($id) ?>">
          <button class="btn" type="submit">更新</button>
        </form>
      </div>
<!--    </div> -->
  </div>
</body>
</html>


<script>
/**
 * AIモード切り替え時に、対応するsystem_masterのプロンプトを
 * ai_prompt / ai_past_tweet テキストエリアへ反映する
 */
// PHPで取得したアカウント情報をJavaScriptに渡す
const editAccount = <?= json_encode($edit_account ?? new stdClass(), JSON_UNESCAPED_UNICODE); ?>;

// --- 前回選択されたモードを保持する変数 ---
let previousMode = null;

function filterPresets() {

    const selectedMode = document.querySelector('input[name="ai_mode"]:checked')?.value;
    if (!selectedMode) return;

    const promptBox = document.getElementById("ai_prompt");
    const pastTweetBox = document.getElementById("ai_past_tweet");

    const promptReplyBox = document.getElementById("ai_reply_prompt");
    const pastReplyBox = document.getElementById("ai_past_reply");


    // --- 前回と同じモードならスキップ（必要に応じて処理を変える） ---
    if (previousMode === selectedMode) {
        console.log(`同じモード(${selectedMode})なので処理をスキップ`);
        return;
    }

    // --- 前回と異なるモードに切り替わった場合のみ処理 ---
    console.log(`モード変更: ${previousMode} → ${selectedMode}`);

    // 裏垢 → 裏垢以外
    if((previousMode == "1" || previousMode == null) && selectedMode != "1")
    {
        promptReplyBox.value = editAccount["ai_free_prompt_rep"] || "";
        pastReplyBox.value = editAccount["ai_free_past_rep"] || "";
    }
    // 裏垢以外 → 裏垢
    else if((previousMode != "1" || previousMode == null) && selectedMode == "1")
    {
        promptReplyBox.value = editAccount["ai_uraaka_prompt_rep"] || "";        
        pastReplyBox.value = editAccount["ai_uraaka_past_rep"] || "";
    }

    previousMode = selectedMode; // 新しいモードを記録

    // 一旦クリア
    promptBox.value = "";
    pastTweetBox.value = "";

    promptBox.style.display = 'block';
    promptReplyBox.style.display = 'block';
    pastReplyBox.style.display = 'block';

//    console.log("editAccount =", editAccount);
//    console.log("selectedMode =", selectedMode);

    switch (selectedMode) {
        case "1": // 裏垢女子
            promptBox.value = editAccount["ai_uraaka_prompt"] || "";
            pastTweetBox.value = editAccount["ai_uraaka_past_tweet"] || "";
            pastTweetBox.style.display = 'block';
            break;

        case "2": // Yahooトレンド
            promptBox.value = editAccount["ai_trend_prompt_yahoo"] || "";
            pastTweetBox.style.display = 'none';
            break;

        case "6": // Xトレンド
            promptBox.value = editAccount["ai_trend_prompt_x"] || "";
            pastTweetBox.style.display = 'none';
            break;

        case "3": // BTC為替
            promptBox.value = editAccount["ai_btc_prompt"] || "";
            pastTweetBox.style.display = 'none';
            break;

        case "9": // 自由ﾓｰﾄﾞ
            promptBox.value = editAccount["ai_free_prompt"] || "";
            pastTweetBox.style.display = 'none';
            break;

        default: // なし
            promptBox.value = "";
            pastTweetBox.value = "";
            promptBox.style.display = 'none';
            pastTweetBox.style.display = 'none';

            promptReplyBox.style.display = 'none';
            pastReplyBox.style.display = 'none';
            break;
    }

}

// ページ初期表示時にも反映（現在のai_modeに合わせて）
window.addEventListener('DOMContentLoaded', filterPresets);
</script>