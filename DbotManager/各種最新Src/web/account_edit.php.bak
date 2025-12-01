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

    // その他のフィールドの処理（オプションの場合はチェック）
    $login_password = trim($_POST['login_password'] ?? '');
    $client_id = trim($_POST['client_id'] ?? '');
    $client_secret = trim($_POST['client_secret'] ?? '');

    $api_key = trim($_POST['api_key'] ?? '');
    $api_key_secret = trim($_POST['api_key_secret'] ?? '');

    /*
    $access_token = trim($_POST['access_token'] ?? '');
    $access_token_secret = trim($_POST['access_token_secret'] ?? '');
    $bearer_token = trim($_POST['bearer_token'] ?? '');
    $refresh_token = trim($_POST['refresh_token'] ?? '');
    */

    // チェックボックスの値をバインド
    $enable = isset($_POST['enable']) ? 1 : 0;
    $like_enable = isset($_POST['like_enable']) ? 1 : 0;
    $bookmark_enable = isset($_POST['bookmark_enable']) ? 1 : 0;
    $reply_enable = isset($_POST['reply_enable']) ? 1 : 0;
    $paid = isset($_POST['paid']) ? 1 : 0;
    $paid_like = isset($_POST['paid_like']) ? 1 : 0;
    $paid_bookmark = isset($_POST['paid_bookmark']) ? 1 : 0;
    $repost_enable = isset($_POST['repost_enable']) ? 1 : 0;
    $post_enable = isset($_POST['post_enable']) ? 1 : 0;

    // 予約の処理（Reserve1-4）
    $reserve1_enable = isset($_POST['reserve1_enable']) ? 1 : 0;
    $reserve1_start_hour = $_POST['reserve1_start_hour'] ?? 0;
    $reserve1_end_hour = $_POST['reserve1_end_hour'] ?? 0;
    $reserve1_count = $_POST['reserve1_count'] ?? 0;

    $reserve2_enable = isset($_POST['reserve2_enable']) ? 1 : 0;
    $reserve2_start_hour = $_POST['reserve2_start_hour'] ?? 0;
    $reserve2_end_hour = $_POST['reserve2_end_hour'] ?? 0;
    $reserve2_count = $_POST['reserve2_count'] ?? 0;

    $reserve3_enable = isset($_POST['reserve3_enable']) ? 1 : 0;
    $reserve3_start_hour = $_POST['reserve3_start_hour'] ?? 0;
    $reserve3_end_hour = $_POST['reserve3_end_hour'] ?? 0;
    $reserve3_count = $_POST['reserve3_count'] ?? 0;

    $reserve4_enable = isset($_POST['reserve4_enable']) ? 1 : 0;
    $reserve4_start_hour = $_POST['reserve4_start_hour'] ?? 0;
    $reserve4_end_hour = $_POST['reserve4_end_hour'] ?? 0;
    $reserve4_count = $_POST['reserve4_count'] ?? 0;

    $reserve1_ai = isset($_POST['reserve1_ai']) ? 1 : 0;
    $reserve2_ai = isset($_POST['reserve2_ai']) ? 1 : 0;
    $reserve3_ai = isset($_POST['reserve3_ai']) ? 1 : 0;
    $reserve4_ai = isset($_POST['reserve4_ai']) ? 1 : 0;

    $dmm_id = $_POST['dmm_id'];

    $search_enable = isset($_POST['search_enable']) ? 1 : 0;
    $proxy_enable = isset($_POST['proxy_enable']) ? 1 : 0;
    $proxy_url = $_POST['proxy_url'];
    $check_interval = $_POST['check_interval'];

    $ai_post_enable = isset($_POST['ai_post_enable']) ? 1 : 0;
    $ai_reply_enable = isset($_POST['ai_reply_enable']) ? 1 : 0;

//    $ai_post_prompt = $_POST['ai_post_prompt'];
//    $ai_reply_prompt = $_POST['ai_reply_prompt'];
//    $ai_post_example = $_POST['ai_post_example'];
//    $ai_reply_example = $_POST['ai_reply_example'];
//    $ai_trend_prompt = $_POST['ai_trend_prompt'];

    $ai_post_prompt = "";
    $ai_reply_prompt = "";
    $ai_post_example = "";
    $ai_reply_example = "";
    $ai_trend_prompt = "";

    //    $ai_mode = isset($_POST['ai_mode']) ? $_POST['ai_mode'] : null;
    $ai_mode = $_POST['ai_mode'];

    // 2025.10.25 AIプロンプト関連の列追加
    $ai_uraaka_prompt       = $edit_account['ai_uraaka_prompt']       ?? '';
    $ai_uraaka_past_tweet   = $edit_account['ai_uraaka_past_tweet']   ?? '';
    $ai_trend_prompt_yahoo  = $edit_account['ai_trend_prompt_yahoo']  ?? '';
    $ai_trend_prompt_x      = $edit_account['ai_trend_prompt_x']      ?? '';
    $ai_btc_prompt          = $edit_account['ai_btc_prompt']          ?? '';        
    
    {
        $ai_prompt_textbox = trim($_POST['ai_prompt'] ?? '');
        $ai_past_tweet_textbox = trim($_POST['ai_past_tweet'] ?? '');

        // --- ラジオボタンに応じて上書き ---
        switch ($ai_mode) {
            case '1': // 裏垢女子
                if ($ai_prompt_textbox !== '') {
                    $ai_uraaka_prompt = $ai_prompt_textbox;
                }
                if ($ai_past_tweet_textbox !== '') {
                    $ai_uraaka_past_tweet = $ai_past_tweet_textbox;
                }
                break;
            case '2': // Yahooトレンド
                if ($ai_prompt_textbox !== '') {
                    $ai_trend_prompt_yahoo = $ai_prompt_textbox;
                }
                break;
            case '6': // Xトレンド
                if ($ai_prompt_textbox !== '') {
                    $ai_trend_prompt_x = $ai_prompt_textbox;
                }
                break;
            case '3': // BTC為替
                if ($ai_prompt_textbox !== '') {
                    $ai_btc_prompt = $ai_prompt_textbox;
                }
                break;
        }    
      }


    // api_master_id が 0 以外なら client_id を空にする
    if (isset($edit_account['api_master_id']) && $edit_account['api_master_id'] != 0) {
        $client_id = '';
        $paid = 1;
        $paid_like = 1;
        $paid_bookmark = 1;
        $search_enable = 0;
        $check_interval = '';
    }    

    // 入力値のバリデーション
//    if (empty($name) || empty($login_id) || empty($login_password)) {
    if (empty($name) || empty($login_id)) {
            echo '必須項目を全て入力してください';
        exit;
    }

//    echo $login_password,

    // パスワードをハッシュ化
    $hashed_password = password_hash($login_password, PASSWORD_DEFAULT);

    // SQLクエリの準備
    $stmt = $conn->prepare("
        UPDATE account_master
        SET 
            name = ?, 
            login_id = ?, 
            login_password = ?, 
            client_id = ?, 
            client_secret = ?, 
            api_key = ?, 
            api_key_secret = ?, 
            enable = ?, 
            like_enable = ?, 
            bookmark_enable = ?, 
            reply_enable = ?, 
            paid = ?, 
            paid_like = ?, 
            paid_bookmark = ?, 
            repost_enable = ?, 
            post_enable = ?, 
            reserve1_enable = ?, 
            reserve1_start_hour = ?, 
            reserve1_end_hour = ?, 
            reserve1_count = ?, 
            reserve2_enable = ?, 
            reserve2_start_hour = ?, 
            reserve2_end_hour = ?, 
            reserve2_count = ?, 
            reserve3_enable = ?, 
            reserve3_start_hour = ?, 
            reserve3_end_hour = ?, 
            reserve3_count = ?, 
            reserve4_enable = ?, 
            reserve4_start_hour = ?, 
            reserve4_end_hour = ?, 
            reserve4_count = ?,
            reserve1_ai = ?, 
            reserve2_ai = ?, 
            reserve3_ai = ?, 
            reserve4_ai = ?, 
            dmm_id = ? ,
            search_enable = ? ,
            proxy_enable = ? ,
            proxy_url = ? ,
            check_interval = ? ,
            ai_post_enable = ? ,
            ai_reply_enable = ? ,
            ai_post_prompt = ? ,
            ai_reply_prompt = ? ,
            ai_post_example = ? ,
            ai_reply_example = ?,
            ai_mode   = ? ,
            ai_trend_prompt = ? 
            ,ai_uraaka_prompt = ?
            ,ai_uraaka_past_tweet = ?
            ,ai_trend_prompt_yahoo = ? 
            ,ai_trend_prompt_x = ? 
            ,ai_btc_prompt = ?
        WHERE id = ?
    ");

//    "sssssssssssiiiiiiiiiiiiiiiiiiiiiiiiii", // 型指定
    $stmt->bind_param(
        "sssssssiiiiiiiiiiiiiiiiiiiiiiiiiiiiisiisiiissssisssssss", // 型指定
        $name, 
        $login_id, 
#        $hashed_password, 
        $login_password,
        $client_id, 
        $client_secret, 
        $api_key, 
        $api_key_secret, 
        $enable, 
        $like_enable, 
        $bookmark_enable, 
        $reply_enable, 
        $paid, 
        $paid_like, 
        $paid_bookmark, 
        $repost_enable, 
        $post_enable, 
        $reserve1_enable, 
        $reserve1_start_hour, 
        $reserve1_end_hour, 
        $reserve1_count, 
        $reserve2_enable, 
        $reserve2_start_hour, 
        $reserve2_end_hour, 
        $reserve2_count, 
        $reserve3_enable, 
        $reserve3_start_hour, 
        $reserve3_end_hour, 
        $reserve3_count, 
        $reserve4_enable, 
        $reserve4_start_hour, 
        $reserve4_end_hour, 
        $reserve4_count,
        $reserve1_ai,
        $reserve2_ai,
        $reserve3_ai,
        $reserve4_ai,
        $dmm_id,
        $search_enable ,
        $proxy_enable ,
        $proxy_url ,
        $check_interval ,
        $ai_post_enable  ,
        $ai_reply_enable  ,
        $ai_post_prompt  ,
        $ai_reply_prompt , 
        $ai_post_example  ,
        $ai_reply_example , 
        $ai_mode   ,
        $ai_trend_prompt  

        ,$ai_uraaka_prompt 
        ,$ai_uraaka_past_tweet 
        ,$ai_trend_prompt_yahoo 
        ,$ai_trend_prompt_x 
        ,$ai_btc_prompt 
        ,$id
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

          <!--
          <label>ログインパス</label>
          <input type="text" name="login_password" value="<?= htmlspecialchars($edit_account['login_password'] ?? '') ?>">
          -->

          <label>Client ID</label>
          <input type="text" name="client_id" value="<?= htmlspecialchars($edit_account['client_id'] ?? '') ?>">

          <label>Client Secret</label>
          <input type="text" name="client_secret" value="<?= htmlspecialchars($edit_account['client_secret'] ?? '') ?>">

          <label>DMM ID</label>
          <input type="text" name="dmm_id" value="<?= htmlspecialchars($edit_account['dmm_id'] ?? '') ?>">

          <label>API Key</label>
          <input type="text" name="api_key" value="<?= htmlspecialchars($edit_account['api_key'] ?? '') ?>">

          <label>API Key Secret</label>
          <input type="text" name="api_key_secret" value="<?= htmlspecialchars($edit_account['api_key_secret'] ?? '') ?>">

          <div class="checkbox-group">
            <label><input type="checkbox" name="enable" value="1" <?= !empty($edit_account['enable']) ? 'checked' : '' ?>>有効</label>
            <label><input type="checkbox" name="post_enable" value="1" <?= !empty($edit_account['post_enable']) ? 'checked' : '' ?>>ポスト</label>
            <label><input type="checkbox" name="like_enable" value="1" <?= !empty($edit_account['like_enable']) ? 'checked' : '' ?>>いいね</label>
            <label><input type="checkbox" name="bookmark_enable" value="1" <?= !empty($edit_account['bookmark_enable']) ? 'checked' : '' ?>>ブックマーク</label>
            <label><input type="checkbox" name="reply_enable" value="1" <?= !empty($edit_account['reply_enable']) ? 'checked' : '' ?>>リプライ</label>
            <label><input type="checkbox" name="repost_enable" value="1" <?= !empty($edit_account['repost_enable']) ? 'checked' : '' ?>>リポスト</label>
          </div>

          <label>監視実施 <input type="checkbox" name="search_enable" value="1" <?= !empty($edit_account['search_enable']) ? 'checked' : '' ?>></label>
          <label>監視周期（分）</label>
          <input type="number" class="short"  name="check_interval" value="<?= htmlspecialchars($edit_account['check_interval'] ?? '') ?>">

          <label>プロキシ使用 <input type="checkbox" name="proxy_enable" value="1" <?= !empty($edit_account['proxy_enable']) ? 'checked' : '' ?>></label>
          <label>プロキシURL</label>
          <input type="text" name="proxy_url" value="<?= htmlspecialchars($edit_account['proxy_url'] ?? '') ?>">

          <label>有料アカウント <input type="checkbox" name="paid" value="1" <?= !empty($edit_account['paid']) ? 'checked' : '' ?>></label>
          <label>有料API（いいね） <input type="checkbox" name="paid_like" value="1" <?= !empty($edit_account['paid_like']) ? 'checked' : '' ?>></label>
          <label>有料API（ブックマーク） <input type="checkbox" name="paid_bookmark" value="1" <?= !empty($edit_account['paid_bookmark']) ? 'checked' : '' ?>></label>

          <h3>ポスト予約設定</h3>
          <label>時間帯1</label><br>
          <input type="checkbox" name="reserve1_enable" value="1" <?= !empty($edit_account['reserve1_enable']) ? 'checked' : '' ?>>
          <input type="text" name="reserve1_start_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve1_start_hour'] ?? '') ?>"> ～
          <input type="text" name="reserve1_end_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve1_end_hour'] ?? '') ?>"> 時　
          <input type="text" name="reserve1_count" class="short" value="<?= htmlspecialchars($edit_account['reserve1_count'] ?? '') ?>"> 回

          <label>時間帯2</label><br>
          <input type="checkbox" name="reserve2_enable" value="1" <?= !empty($edit_account['reserve2_enable']) ? 'checked' : '' ?>>
          <input type="text" name="reserve2_start_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve2_start_hour'] ?? '') ?>"> ～
          <input type="text" name="reserve2_end_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve2_end_hour'] ?? '') ?>"> 時　
          <input type="text" name="reserve2_count" class="short" value="<?= htmlspecialchars($edit_account['reserve2_count'] ?? '') ?>"> 回

          <label>時間帯3</label><br>
          <input type="checkbox" name="reserve3_enable" value="1" <?= !empty($edit_account['reserve3_enable']) ? 'checked' : '' ?>>
          <input type="text" name="reserve3_start_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve3_start_hour'] ?? '') ?>"> ～
          <input type="text" name="reserve3_end_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve3_end_hour'] ?? '') ?>"> 時　
          <input type="text" name="reserve3_count" class="short" value="<?= htmlspecialchars($edit_account['reserve3_count'] ?? '') ?>"> 回

          <label>時間帯4</label><br>
          <input type="checkbox" name="reserve4_enable" value="4" <?= !empty($edit_account['reserve4_enable']) ? 'checked' : '' ?>>
          <input type="text" name="reserve4_start_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve4_start_hour'] ?? '') ?>"> ～
          <input type="text" name="reserve4_end_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve4_end_hour'] ?? '') ?>"> 時　
          <input type="text" name="reserve4_count" class="short" value="<?= htmlspecialchars($edit_account['reserve4_count'] ?? '') ?>"> 回


          
          <label>AIコメントON <input type="checkbox" name="reserve1_ai" value="1" <?= !empty($edit_account['reserve1_ai']) ? 'checked' : '' ?>></label>

          <label>AIポスト <input type="checkbox" name="ai_post_enable" value="1" <?= !empty($edit_account['ai_post_enable']) ? 'checked' : '' ?>></label>
          <label><input type="radio" name="ai_mode" value="0" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 0 ? 'checked' : '' ?>>なし</label>
          <label><input type="radio" name="ai_mode" value="1" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 1 ? 'checked' : '' ?>>裏垢女子</label>
          <label><input type="radio" name="ai_mode" value="2" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 2 ? 'checked' : '' ?>>yhooトレンド</label>
          <label><input type="radio" name="ai_mode" value="6" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 6 ? 'checked' : '' ?>>Xトレンド</label>
          <label><input type="radio" name="ai_mode" value="3" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 3 ? 'checked' : '' ?>>BTC為替</label>

          <!--
          <label><input type="radio" name="ai_mode" value="4" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 4 ? 'checked' : '' ?>>GOLD為替</label>
          <label><input type="radio" name="ai_mode" value="5" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 5 ? 'checked' : '' ?>>他通貨為替</label>
          -->

          <label>プロンプト</label><br>
          <textarea id="ai_prompt" name="ai_prompt" cols="80" rows="5" 
          style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>

          <br>
          <label>ポスト例</label><br>
          <textarea id="ai_past_tweet" name="ai_past_tweet" cols="80" rows="5" 
          style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>
          <br>

          <label>AIリプライ <input type="checkbox" name="ai_reply_enable" value="1" <?= !empty($edit_account['ai_reply_enable']) ? 'checked' : '' ?>></label>

          <!--
          <label>ポスト用プロンプト</label>
          <textarea name="ai_post_prompt"><?= htmlspecialchars($edit_account['ai_post_prompt'] ?? '') ?></textarea>

          <label>ポスト例文</label>
          <textarea name="ai_post_example"><?= htmlspecialchars($edit_account['ai_post_example'] ?? '') ?></textarea>

          <label>リプ用プロンプト</label>
          <textarea name="ai_reply_prompt"><?= htmlspecialchars($edit_account['ai_reply_prompt'] ?? '') ?></textarea>

          <label>リプ例文</label>
          <textarea name="ai_reply_example"><?= htmlspecialchars($edit_account['ai_reply_example'] ?? '') ?></textarea>

          <label>トレンドプロンプト</label>
          <textarea name="ai_trend_prompt"><?= htmlspecialchars($edit_account['ai_trend_prompt'] ?? '') ?></textarea>
          -->

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

function filterPresets() {
    const selectedMode = document.querySelector('input[name="ai_mode"]:checked').value;
    const promptBox = document.getElementById("ai_prompt");
    const pastTweetBox = document.getElementById("ai_past_tweet");

    // 一旦クリア
    promptBox.value = "";
    pastTweetBox.value = "";


//    console.log("editAccount =", editAccount);
//    console.log("selectedMode =", selectedMode);

    switch (selectedMode) {
        case "1": // 裏垢女子
            promptBox.value = editAccount["ai_uraaka_prompt"] || "";
            pastTweetBox.value = editAccount["ai_uraaka_past_tweet"] || "";
            promptBox.style.display = 'block';
            pastTweetBox.style.display = 'block';
            break;

        case "2": // Yahooトレンド
            promptBox.value = editAccount["ai_trend_prompt_yahoo"] || "";
            promptBox.style.display = 'block';
            pastTweetBox.style.display = 'none';
            break;

        case "6": // Xトレンド
            promptBox.value = editAccount["ai_trend_prompt_x"] || "";
            promptBox.style.display = 'block';
            pastTweetBox.style.display = 'none';
            break;

        case "3": // BTC為替
            promptBox.value = editAccount["ai_btc_prompt"] || "";
            promptBox.style.display = 'block';
            pastTweetBox.style.display = 'none';
            break;

        default: // なし
            promptBox.value = "";
            pastTweetBox.value = "";
            promptBox.style.display = 'none';
            pastTweetBox.style.display = 'none';
            break;
    }

}

// ページ初期表示時にも反映（現在のai_modeに合わせて）
window.addEventListener('DOMContentLoaded', filterPresets);
</script>