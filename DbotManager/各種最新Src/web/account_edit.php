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

    $ai_free_prompt          = $edit_account['ai_free_prompt']          ?? '';        

    $ai_uraaka_prompt_rep          = $edit_account['ai_uraaka_prompt_rep']          ?? '';        
    $ai_uraaka_past_rep          = $edit_account['ai_uraaka_past_rep']          ?? '';        
    $ai_free_prompt_rep          = $edit_account['ai_free_prompt_rep']          ?? '';        
    $ai_free_past_rep          = $edit_account['ai_free_past_rep']          ?? '';        

//    $ai_photo_enable = $_POST['ai_photo_enable'] ?? '';
//    $ai_movie_enable = $_POST['ai_movie_enable'] ?? '';
//    $ai_media_selection_rate = $_POST['ai_media_selection_rate'] ?? '';
    $ai_photo_enable = isset($_POST['ai_photo_enable']) ? 1 : 0;
    $ai_movie_enable = isset($_POST['ai_movie_enable']) ? 1 : 0;
    $ai_media_selection_rate = $_POST['ai_media_selection_rate'];

    {
        $ai_prompt_textbox = trim($_POST['ai_prompt'] ?? '');
        $ai_past_tweet_textbox = trim($_POST['ai_past_tweet'] ?? '');

        $ai_prompt_rep_textbox = trim($_POST['ai_reply_prompt'] ?? '');
        $ai_past_rep_textbox = trim($_POST['ai_past_reply'] ?? '');

        // --- ラジオボタンに応じて上書き ---
        switch ($ai_mode) {
            case '1': // 裏垢女子
                if ($ai_prompt_textbox !== '') {
                    $ai_uraaka_prompt = $ai_prompt_textbox;
                }
                if ($ai_past_tweet_textbox !== '') {
                    $ai_uraaka_past_tweet = $ai_past_tweet_textbox;
                }
                if ($ai_prompt_rep_textbox !== '') {
                    $ai_uraaka_prompt_rep = $ai_prompt_rep_textbox;
                }
                if ($ai_past_rep_textbox !== '') {
                    $ai_uraaka_past_rep = $ai_past_rep_textbox;
                }
                break;
            case '2': // Yahooトレンド
                if ($ai_prompt_textbox !== '') {
                    $ai_trend_prompt_yahoo = $ai_prompt_textbox;
                }
                if ($ai_prompt_rep_textbox !== '') {
                    $ai_free_prompt_rep = $ai_prompt_rep_textbox;
                }

                if ($ai_past_rep_textbox !== '') {
                    $ai_free_past_rep = $ai_past_rep_textbox;
                }
                break;
            case '6': // Xトレンド
                if ($ai_prompt_textbox !== '') {
                    $ai_trend_prompt_x = $ai_prompt_textbox;
                }
                if ($ai_prompt_rep_textbox !== '') {
                    $ai_free_prompt_rep = $ai_prompt_rep_textbox;
                }
                if ($ai_past_rep_textbox !== '') {
                    $ai_free_past_rep = $ai_past_rep_textbox;
                }
                break;
            case '3': // BTC為替
                if ($ai_prompt_textbox !== '') {
                    $ai_btc_prompt = $ai_prompt_textbox;
                }
                if ($ai_prompt_rep_textbox !== '') {
                    $ai_free_prompt_rep = $ai_prompt_rep_textbox;
                }
                if ($ai_past_rep_textbox !== '') {
                    $ai_free_past_rep = $ai_past_rep_textbox;
                }
                break;
            case '9': // 自由ﾓｰﾄﾞ
                if ($ai_prompt_textbox !== '') {
                    $ai_free_prompt = $ai_prompt_textbox;
                }
                if ($ai_prompt_rep_textbox !== '') {
                    $ai_free_prompt_rep = $ai_prompt_rep_textbox;
                }
                if ($ai_past_rep_textbox !== '') {
                    $ai_free_past_rep = $ai_past_rep_textbox;
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

            ,ai_free_prompt = ?
            ,ai_uraaka_prompt_rep = ?
            ,ai_uraaka_past_rep = ?
            ,ai_free_prompt_rep = ?
            ,ai_free_past_rep = ?

            ,ai_photo_enable = ?
            ,ai_movie_enable = ?
            ,ai_media_selection_rate = ?

        WHERE id = ?
    ");

//    "sssssssssssiiiiiiiiiiiiiiiiiiiiiiiiii", // 型指定
    $stmt->bind_param(
        "sssssssiiiiiiiiiiiiiiiiiiiiiiiiiiiiisiisiiissssisssssssssssssss", // 型指定
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

        ,$ai_free_prompt 
        ,$ai_uraaka_prompt_rep 
        ,$ai_uraaka_past_rep 
        ,$ai_free_prompt_rep 
        ,$ai_free_past_rep 

        ,$ai_photo_enable
        ,$ai_movie_enable
        ,$ai_media_selection_rate


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

          <?php
            $hide = !empty($edit_account['id'])
                && isset($_SESSION['hide_sensitive_fields'])
                && (int)$_SESSION['hide_sensitive_fields'] === 1;

            $sensitive_labels = [
                'client_id'      => 'Client ID',
                'client_secret'  => 'Client Secret',
                'api_key'        => 'API Key',
                'api_key_secret' => 'API Key Secret',
            ];
            foreach ($sensitive_labels as $field => $label): ?>
            <?php if (!$hide): ?>
                <label><?= $label ?></label>
                <input type="text" name="<?= $field ?>"
                    value="<?= htmlspecialchars($edit_account[$field] ?? '') ?>">
            <?php else: ?>
                <input type="hidden" name="<?= $field ?>"
                    value="<?= htmlspecialchars($edit_account[$field] ?? '') ?>">
            <?php endif; ?>
            <?php endforeach; ?>

          <label>DMM ID</label>
          <input type="text" name="dmm_id" value="<?= htmlspecialchars($edit_account['dmm_id'] ?? '') ?>">

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

          <?php if (!$hide): ?>
          <label>プロキシ使用 <input type="checkbox" name="proxy_enable" value="1" <?= !empty($edit_account['proxy_enable']) ? 'checked' : '' ?>></label>
          <label>プロキシURL</label>
          <input type="text" name="proxy_url" value="<?= htmlspecialchars($edit_account['proxy_url'] ?? '') ?>">
          <?php else: ?>
          <input type="hidden" name="proxy_enable" value="<?= !empty($edit_account['proxy_enable']) ? 1 : 0 ?>">
          <input type="hidden" name="proxy_url" value="<?= htmlspecialchars($edit_account['proxy_url'] ?? '') ?>">
          <?php endif; ?>

          <label>有料アカウント <input type="checkbox" name="paid" value="1" <?= !empty($edit_account['paid']) ? 'checked' : '' ?>></label>
          <label>有料API（いいね） <input type="checkbox" name="paid_like" value="1" <?= !empty($edit_account['paid_like']) ? 'checked' : '' ?>></label>
          <label>有料API（ブックマーク） <input type="checkbox" name="paid_bookmark" value="1" <?= !empty($edit_account['paid_bookmark']) ? 'checked' : '' ?>></label>

          <h3>ポスト予約設定</h3>
          <label>時間帯1</label><br>
          <input type="checkbox" name="reserve1_enable" value="1" <?= !empty($edit_account['reserve1_enable']) ? 'checked' : '' ?>>
          <input type="text" name="reserve1_start_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve1_start_hour'] ?? '') ?>"> ～
          <input type="text" name="reserve1_end_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve1_end_hour'] ?? '') ?>"> 時　
          <input type="text" name="reserve1_count" class="short" value="<?= htmlspecialchars($edit_account['reserve1_count'] ?? '') ?>"> 回
          <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
              <input type="checkbox" name="reserve1_ai" value="1" <?= !empty($edit_account['reserve1_ai']) ? 'checked' : '' ?>>AIｺﾒﾝﾄ
          <?php endif; ?>

          <label>時間帯2</label><br>
          <input type="checkbox" name="reserve2_enable" value="1" <?= !empty($edit_account['reserve2_enable']) ? 'checked' : '' ?>>
          <input type="text" name="reserve2_start_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve2_start_hour'] ?? '') ?>"> ～
          <input type="text" name="reserve2_end_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve2_end_hour'] ?? '') ?>"> 時　
          <input type="text" name="reserve2_count" class="short" value="<?= htmlspecialchars($edit_account['reserve2_count'] ?? '') ?>"> 回
          <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
              <input type="checkbox" name="reserve2_ai" value="1" <?= !empty($edit_account['reserve2_ai']) ? 'checked' : '' ?>>AIｺﾒﾝﾄ
          <?php endif; ?>

          <label>時間帯3</label><br>
          <input type="checkbox" name="reserve3_enable" value="1" <?= !empty($edit_account['reserve3_enable']) ? 'checked' : '' ?>>
          <input type="text" name="reserve3_start_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve3_start_hour'] ?? '') ?>"> ～
          <input type="text" name="reserve3_end_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve3_end_hour'] ?? '') ?>"> 時　
          <input type="text" name="reserve3_count" class="short" value="<?= htmlspecialchars($edit_account['reserve3_count'] ?? '') ?>"> 回
          <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
              <input type="checkbox" name="reserve3_ai" value="1" <?= !empty($edit_account['reserve3_ai']) ? 'checked' : '' ?>>AIｺﾒﾝﾄ
          <?php endif; ?>


          <label>時間帯4</label><br>
          <input type="checkbox" name="reserve4_enable" value="4" <?= !empty($edit_account['reserve4_enable']) ? 'checked' : '' ?>>
          <input type="text" name="reserve4_start_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve4_start_hour'] ?? '') ?>"> ～
          <input type="text" name="reserve4_end_hour" class="short" value="<?= htmlspecialchars($edit_account['reserve4_end_hour'] ?? '') ?>"> 時　
          <input type="text" name="reserve4_count" class="short" value="<?= htmlspecialchars($edit_account['reserve4_count'] ?? '') ?>"> 回       
          <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
            <input type="checkbox" name="reserve4_ai" value="1" <?= !empty($edit_account['reserve4_ai']) ? 'checked' : '' ?>>AIｺﾒﾝﾄ
          <?php endif; ?>

          <br>
          <label>AIポストモード</label>
          <label><input type="radio" name="ai_mode" value="0" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 0 ? 'checked' : '' ?>>なし</label>
          <label><input type="radio" name="ai_mode" value="1" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 1 ? 'checked' : '' ?>>裏垢女子</label>
          <label><input type="radio" name="ai_mode" value="2" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 2 ? 'checked' : '' ?>>yahooトレンド</label>
          <label><input type="radio" name="ai_mode" value="6" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 6 ? 'checked' : '' ?>>Xトレンド</label>
          <label><input type="radio" name="ai_mode" value="3" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 3 ? 'checked' : '' ?>>BTC為替</label>
          <label><input type="radio" name="ai_mode" value="9" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 9 ? 'checked' : '' ?>>自由ﾓｰﾄﾞ</label>

          <input type="checkbox" name="ai_photo_enable" value="1" <?= !empty($edit_account['ai_photo_enable']) ? 'checked' : '' ?>>画像
          <input type="checkbox" name="ai_movie_enable" value="1" <?= !empty($edit_account['ai_movie_enable']) == 0 ? 'checked' : '' ?>>動画
          <input type="number" id="ai_media_selection_rate" name="ai_media_selection_rate" class="short" placeholder="ﾒﾃﾞｨｱ選択率" min="1" max="100" step="1" value="<?= htmlspecialchars($edit_account['ai_media_selection_rate'] ?? '') ?>"> ％

          <!--
          <label><input type="radio" name="ai_mode" value="4" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 4 ? 'checked' : '' ?>>GOLD為替</label>
          <label><input type="radio" name="ai_mode" value="5" onclick="filterPresets()" <?= ($edit_account['ai_mode'] ?? '') == 5 ? 'checked' : '' ?>>他通貨為替</label>
          -->

          <label>AIポスト プロンプト/ポスト例文(裏垢女子のみ)<input type="checkbox" name="ai_post_enable" value="1" <?= !empty($edit_account['ai_post_enable']) ? 'checked' : '' ?>></label>
          <textarea id="ai_prompt" name="ai_prompt" cols="80" rows="5" 
          style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>
          <textarea id="ai_past_tweet" name="ai_past_tweet" cols="80" rows="5" 
          style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>
          <br>

          <label>AIリプライ プロンプト/リプライ例文<input type="checkbox" name="ai_reply_enable" value="1" <?= !empty($edit_account['ai_reply_enable']) ? 'checked' : '' ?>></label>
          <textarea id="ai_reply_prompt" name="ai_reply_prompt" cols="80" rows="5" 
          style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>
          <textarea id="ai_past_reply" name="ai_past_reply" cols="80" rows="5" 
          style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>
          <br>

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