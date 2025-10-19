<?php
require __DIR__.'/_lib/config.php';
session_start(); // セッションを開始する
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    header("Location: login.php");
    exit;
}

/*
if (!isset($_SESSION['admin']) && $_SESSION['admin'] == 1){
    echo '権限が足りません';
    exit;
}
    */

$xuser_id = $_GET['xuser']??'';
$xuser_id = filter_var($xuser_id, FILTER_VALIDATE_INT);
if ($xuser_id === false) {
    $xuser_id = '';
}

// アカウントリストを取得
$current_userid = $_SESSION['user_id'];
$api_master_id = isset($_SESSION['api_master_id']) ? $_SESSION['api_master_id'] : null;

// アカウントコンボボックスのレコード取得
//$stmt = $conn->prepare("SELECT * FROM account_master WHERE user_id = ?");
$stmt = $conn->prepare("
SELECT 
am.name as name
, am.login_id as login_id
, am.bearer_token as bearer_token
, am.refresh_token as refresh_token
, am.access_token as access_token
, am.id as id
, am.search_enable as search_enable
FROM account_master am WHERE am.user_id = ?");

$stmt->bind_param("s", $current_userid);
$stmt->execute();
$result = $stmt->get_result();
$stmt->close();

// プロンプトプリセットのリストを取得
$stmt = $conn->prepare("SELECT id, type, mode , name, prompt , example FROM prompt_master");
$stmt->execute();
$result = $stmt->get_result();
$stmt->close();

$presets = [];
while ($row = $result->fetch_assoc()) {
    $presets[] = $row;
}

$xusers = [];
$xuser = null;
while ($row = $result->fetch_assoc()){
    $xusers[] = $row;
    if ((string)$row['id'] === (string)$xuser_id) {
        $xuser = $row;
    }
}

// 新規ユーザー登録処理
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $type = $_POST['type']??'';
    if ($type == 'account_del') {
        $id = $_POST['id'];

        if (empty($id)) {
            echo "<script>alert('IDが指定されていません');</script>";
            header("Location: account_list.php");
            exit;
        }else if ((string)$id === (string)$_SESSION['user_id']) {
            echo '現在のユーザーは削除できません';
            exit;
        }

        // SQLを準備して実行
        $stmt = $conn->prepare("DELETE FROM account_master WHERE id = ?");
        $stmt->bind_param("i", $id);

        if ($stmt->execute()) {
            /* 更新成功 */
        } else {
            /* 更新失敗 */
        }

        $stmt->close();
        $conn->close();

        // 登録後にリダイレクト
        header("Location: account_list.php");
        exit;        
    }
    else{

        $new_name = $_POST['new_name'];
        $new_login_id = $_POST['new_login_id'];
        $new_client_id = ""; // 貸出モードは指定なし
        $new_client_secret = ""; 
        $new_api_key = $_POST['new_api_key'];
        $new_api_key_secret = $_POST['new_api_key_secret'];

        $new_access_token = '';
        $new_access_token_secret = '';
        /*
        $new_access_token = $_POST['new_access_token'];
        $new_access_token_secret = $_POST['new_access_token_secret'];
        $new_bearer_token = $_POST['new_bearer_token'];
        $new_refresh_token = $_POST['new_refresh_token'];
        */

        $new_enable = isset($_POST['new_enable']) ? 1 : 0;

        $new_like_enable = isset($_POST['new_like_enable']) ? 1 : 0;
        $new_reply_enable = isset($_POST['new_reply_enable']) ? 1 : 0;
        $new_bookmark_enable = isset($_POST['new_bookmark_enable']) ? 1 : 0;
        $new_repost_enable = isset($_POST['new_repost_enable']) ? 1 : 0;
        $new_post_enable = isset($_POST['new_post_enable']) ? 1 : 0;
        $new_paid = 1;//isset($_POST['new_paid']) ? 1 : 0;
        $new_paid_like = 1;//isset($_POST['new_paid_like']) ? 1 : 0;
        $new_paid_bookmark = 1;//isset($_POST['new_paid_bookmark']) ? 1 : 0;

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
        $new_dmm_id = $_POST['new_dmm_id'];

        $new_search_enable = 0;//isset($_POST['new_search_enable']) ? 1 : 0;
        $new_check_interval = 60;//$_POST['check_interval'] ?? 60;

        $new_proxy_enable = isset($_POST['new_proxy_enable']) ? 1 : 0;
        $new_proxy_url = $_POST['new_proxy_url'];

        $new_use_admin_api = 1;//isset($_POST['new_use_admin_api']) ? 1 : 0;
        $new_api_master_id = $_SESSION['api_master_id'];
        
        $ai_post_enable = isset($_POST['ai_post_enable']) ? 1 : 0;
        $ai_reply_enable = isset($_POST['ai_reply_enable']) ? 1 : 0;
        $ai_post_prompt = $_POST['ai_post_prompt'];
        $ai_trend_prompt = $_POST['ai_trend_prompt'];
        $ai_reply_prompt = $_POST['ai_reply_prompt'];
        $ai_post_example = $_POST['ai_post_example'];
        $ai_reply_example = $_POST['ai_reply_example'];
        $ai_mode = $_POST['ai_mode'];

        // 既存のユーザー名を確認
        $stmt = $conn->prepare("SELECT COUNT(*) FROM account_master WHERE user_id = ? and login_id = ?");
        $stmt->bind_param("ss", $current_userid, $new_login_id);
        $stmt->execute();
        $stmt->bind_result($count);
        $stmt->fetch();
        $stmt->close();

        // 重複している場合の処理
        if ($count > 0) {
            echo "<script>alert('このログインIDは既に存在します。別のログインIDを使用してください。');</script>";
        } else {

            // ユーザーをデータベースに登録
            $stmt = $conn->prepare("INSERT INTO account_master (
                user_id, 
                name,
                login_id,
                client_id,
                client_secret,
                api_key,
                api_key_secret,
                enable,
                like_enable,
                reply_enable,
                bookmark_enable, 
                repost_enable,
                post_enable,
                paid,
                paid_like,
                paid_bookmark,
                reserve1_enable , 
                reserve1_start_hour , 
                reserve1_end_hour , 
                reserve1_count , 
                reserve2_enable , 
                reserve2_start_hour , 
                reserve2_end_hour , 
                reserve2_count , 
                reserve3_enable , 
                reserve3_start_hour , 
                reserve3_end_hour , 
                reserve3_count , 
                reserve4_enable , 
                reserve4_start_hour , 
                reserve4_end_hour , 
                reserve4_count ,
                reserve1_ai , 
                reserve2_ai , 
                reserve3_ai , 
                reserve4_ai , 
                dmm_id ,
                search_enable ,
                proxy_enable ,
                proxy_url ,
                api_master_id ,
                use_admin_api ,
                check_interval,
                ai_post_enable  ,
                ai_reply_enable  ,
                ai_post_prompt  ,
                ai_reply_prompt ,
                ai_post_example  ,
                ai_reply_example ,
                ai_mode   ,
                ai_trend_prompt
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
            
            $stmt->bind_param(
                "sssssssiiiiiiiiiiiiiiiiiiiiiiiiiiiiisiisiiiiissssis",
                $current_userid,    //s
                $new_name,          //s
                $new_login_id,      //s
                $new_client_id,     //s
                $new_client_secret, //s
                $new_api_key,       //s
                $new_api_key_secret,//s
                $new_enable,        //i
                $new_like_enable,   //i
                $new_reply_enable,  //i
                $new_bookmark_enable,//i 
                $new_repost_enable, //i
                $new_post_enable,   //i
                $new_paid,          //i
                $new_paid_like,     //i
                $new_paid_bookmark, //i
                $reserve1_enable ,  //i
                $reserve1_start_hour , //i
                $reserve1_end_hour ,    //i
                $reserve1_count ,   //i
                $reserve2_enable ,  //i
                $reserve2_start_hour , //i
                $reserve2_end_hour , //i
                $reserve2_count ,   //i
                $reserve3_enable ,  //i
                $reserve3_start_hour , //i
                $reserve3_end_hour , //i
                $reserve3_count ,   //i
                $reserve4_enable ,  //i
                $reserve4_start_hour , //i
                $reserve4_end_hour , //i
                $reserve4_count ,   //i
                $reserve1_ai ,  //i
                $reserve2_ai ,  //i
                $reserve3_ai , //i
                $reserve4_ai , //i
                $new_dmm_id,    //s
                $new_search_enable, //i
                $new_proxy_enable,//i
                $new_proxy_url,//s
                $new_api_master_id,//i
                $new_use_admin_api,//i
                $new_check_interval,//i
                $ai_post_enable  ,
                $ai_reply_enable  ,
                $ai_post_prompt  ,
                $ai_reply_prompt ,         
                $ai_post_example  ,
                $ai_reply_example ,         
                $ai_mode ,
                $ai_trend_prompt  
                );

            $stmt->execute();
            $stmt->close();
            $conn->close();
            // 登録後にリダイレクト
            header("Location: account_list.php");
            exit;        
        }

    }
}



//$stmt = $conn->prepare("SELECT * FROM account_master WHERE user_id = ?");
$stmt = $conn->prepare("
SELECT 
am.name as name
, am.login_id as login_id
, am.bearer_token as bearer_token
, am.refresh_token as refresh_token
, am.access_token as access_token
, am.id as id
, am.search_enable as search_enable
FROM account_master am WHERE am.user_id = ?");
$stmt->bind_param("s", $current_userid);
$stmt->execute();
$result = $stmt->get_result();
?>

<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <title>Xアカウント登録(貸出API専用)</title>
  <link rel="stylesheet" href="./css/admin-dashboard.css" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
  </style>
</head>
<body>
<div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
   <div class="content" id="content">
   <h2 class="tx-white">Xアカウント登録(貸出API専用)</h2>
   <form method="POST" action="?">

    <div class="input-group">
        <input type="text" id="new_name" name="new_name" placeholder="名前" required>
    </div>
    <div class="input-group">
        <input type="text" id="new_login_id" name="new_login_id" placeholder="XアカウントID" required>
    </div>
    <!--
    <div class="input-group">
        <input type="text" id="new_login_pass" name="new_login_pass" placeholder="ログインパス">
    </div>
    -->

    <!-- チェックボックス (通常モード用) -->
     <!--
        <div class="input-group">
            <input type="text" name="new_client_id" placeholder="ClientID">
        </div>
        <div class="input-group">
            <input type="text" name="new_client_secret" placeholder="ClientSecret">
        </div>
    -->

    <!--
    <div class="input-group">
        <input type="text" name="new_bearer_token" placeholder="BearerToken">
    </div>
    <div class="input-group">
        <input type="text" name="new_refresh_token" placeholder="RefreshToken">
    </div>
    -->

    <div class="input-group" checkbox-group">
        <label>
            <input type="checkbox" name="new_enable" value="1" checked>有効
        </label><br>

        <?php if (isset($_SESSION['post_enable']) && $_SESSION['post_enable'] == 1): ?>
        <label>
            <input type="checkbox" name="new_post_enable" value="1" checked>ポスト機能
        </label><br>
        <?php endif; ?>

        <?php if (isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1): ?>
        <label>
            <input type="checkbox" name="new_like_enable" value="1" checked>いいね機能
        </label><br>
        <?php else: ?>
            <label>
            <input type="hidden" name="new_like_enable" value="1" checked>
        </label><br>
        <?php endif; ?>

        <?php if (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1): ?>
            <label>
            <input type="checkbox" name="new_bookmark_enable" value="1" checked>ブックマーク機能
            </label><br>
        <?php else: ?>
            <label>
            <input type="hidden" name="new_bookmark_enable" value="1" checked>
        </label><br>
        <?php endif; ?>

        <?php if (isset($_SESSION['reply_enable']) && $_SESSION['reply_enable'] == 1): ?>
            <label>
            <input type="checkbox" name="new_reply_enable" value="1"  checked>リプライ機能
        </label><br>
        <?php endif; ?>

        <?php if (isset($_SESSION['repost_enable']) && $_SESSION['repost_enable'] == 1): ?>
        <label>
            <input type="checkbox" name="new_repost_enable" value="1" checked>リポスト機能
        </label><br>
        <?php endif; ?>

        <!--
        <?php if (isset($_SESSION['check_enable']) && $_SESSION['check_enable'] == 1): ?>
        <label>
            <input type="checkbox" name="new_search_enable" value="0">監視実施
        </label><br>

        <div class="input-group">
        <label for="check_interval">監視周期(分):</label>
        <input type="number" id="check_interval" name="check_interval" class="short" min="5" max="6000" step="1" value="60">
        </div>  

        <?php endif; ?>
        -->

        <label>
            <input type="checkbox" name="new_proxy_enable" value="0">プロキシ
        </label><br>
        <input type="text" name="new_proxy_url" placeholder="プロキシURL">
        <br>
    </div>

    <!--
    <div class="input-group">
        <?php if ((isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1) || 
          (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1)): ?>
            <label>
            <input type="checkbox" name="new_paid" value="1" checked>有料アカウント
            </label><br>
        <?php endif; ?>

        <?php if (isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="new_paid_like" value="1" checked>有料API(いいね)
            </label><br>
        <?php endif; ?>

        <?php if (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="new_paid_bookmark" value="1" checked>有料API(ブックマーク)
            </label><br>
        <?php endif; ?>
    </div>
        -->

        <div class="input-group">
            <input type="text" id="new_dmm_id" name="new_dmm_id" placeholder="DMM ID">
        </div>

        <br>
        【メディアポスト関連】
        <br>
        <div class="input-group">
            <input type="text" name="new_api_key" placeholder="ApiKey">
        </div>
        <div class="input-group">
            <input type="text" name="new_api_key_secret" placeholder="ApiKeySecret">
        </div>

        <br>
        【ポスト予約設定】
        <br>
        <label>
            <input type="checkbox" name="reserve1_enable" value="1">時間帯１
            <input type="text" id="reserve1_start_hour" name="reserve1_start_hour" class="short" placeholder="開始" > ～
            <input type="text" id="reserve1_end_hour" name="reserve1_end_hour" class="short" placeholder="終了" > 時　
            <input type="text" id="reserve1_count" name="reserve1_count" class="short" placeholder="" > 回
            <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
                <input type="checkbox" name="reserve1_ai" value="1">AIｺﾒﾝﾄ
                <?php endif; ?>
            </label><br>
        <label>
            <input type="checkbox" name="reserve2_enable" value="1">時間帯２
            <input type="text" id="reserve2_start_hour" name="reserve2_start_hour" class="short" placeholder="開始" > ～
            <input type="text" id="reserve2_end_hour" name="reserve2_end_hour" class="short" placeholder="終了" > 時　
            <input type="text" id="reserve2_count" name="reserve2_count" class="short" placeholder="" > 回
            <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
                <input type="checkbox" name="reserve2_ai" value="1">AIｺﾒﾝﾄ
            <?php endif; ?>
        </label><br>
        <label>
            <input type="checkbox" name="reserve3_enable" value="1">時間帯３
            <input type="text" id="reserve3_start_hour" name="reserve3_start_hour" class="short" placeholder="開始" > ～
            <input type="text" id="reserve3_end_hour" name="reserve3_end_hour" class="short" placeholder="終了" > 時　
            <input type="text" id="reserve3_count" name="reserve3_count" class="short" placeholder="" > 回
            <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
                <input type="checkbox" name="reserve3_ai" value="1">AIｺﾒﾝﾄ
            <?php endif; ?>
        </label><br>
        <label>
            <input type="checkbox" name="reserve4_enable" value="1">時間帯４
            <input type="text" id="reserve4_start_hour" name="reserve4_start_hour" class="short" placeholder="開始" > ～
            <input type="text" id="reserve4_end_hour" name="reserve4_end_hour" class="short" placeholder="終了" > 時　
            <input type="text" id="reserve4_count" name="reserve4_count" class="short" placeholder="" > 回
            <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
                <input type="checkbox" name="reserve4_ai" value="1">AIｺﾒﾝﾄ
            <?php endif; ?>
        </label><br>
        <br>

        <?php if (isset($_SESSION['ai_enable']) && $_SESSION['ai_enable'] == 1): ?>
        <br>
        【AIコメント設定】
        <br>

        <label>
            <input type="radio" name="ai_mode" value="0" onclick="filterPresets()" checked> なし
        </label>
        <label>
            <input type="radio" name="ai_mode" value="1" onclick="filterPresets()" checked> 自由モード
        </label>
        <label>
            <input type="radio" name="ai_mode" value="2" onclick="filterPresets()"> 裏垢女子モード
        </label>
        <label>
            <input type="radio" name="ai_mode" value="3" onclick="filterPresets()"> トレンドモード
        </label>

        <br>
        <input type="checkbox" name="ai_post_enable" value="1">AIポスト<br>
        プロンプト設定      

        <select id="post_preset_select" onchange="loadPresetText_post()">
            <option value="">選択してください</option>  
            <?php foreach ($presets as $preset): ?>
                <?php if ($preset['mode'] === 'post'):  ?>
                <!-- モードが自由の場合、preset['type'] が '自由' のものだけ表示 -->
                    <option value="<?= htmlspecialchars($preset['prompt'], ENT_QUOTES, 'UTF-8') ?>" 
                    class="preset-option" 
                    data-type="<?= htmlspecialchars($preset['type'], ENT_QUOTES, 'UTF-8') ?>"
                    data-example="<?= htmlspecialchars($preset['example'], ENT_QUOTES, 'UTF-8') ?>">
                    <?= htmlspecialchars($preset['name'], ENT_QUOTES, 'UTF-8') ?>
                    </option>
                <?php endif; ?>
            <?php endforeach; ?>
        </select>

        <br>
        <textarea id="ai_post_prompt" name="ai_post_prompt" cols="80" rows="5" maxlength="1000" 
        style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>        
        <textarea id="ai_post_example" name="ai_post_example" cols="80" rows="5" maxlength="2000" 
        style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>    
        <textarea id="ai_trend_prompt" name="ai_trend_prompt" cols="80" rows="5" maxlength="1000" 
        style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>               
        <br>

        <input type="checkbox" name="ai_reply_enable" value="1">AIリプライ<br>
        プロンプト設定
        <select id="reply_preset_select" onchange="loadPresetText_reply()">
            <option value="">選択してください</option>  
            <?php foreach ($presets as $preset): ?>
                <?php if ($preset['mode'] === 'reply'):  ?>

                    <!-- モードが自由の場合、preset['type'] が '自由' のものだけ表示 -->
                    <option value="<?= htmlspecialchars($preset['prompt'], ENT_QUOTES, 'UTF-8') ?>" 
                    class="preset-option" 
                    data-type="<?= htmlspecialchars($preset['type'], ENT_QUOTES, 'UTF-8') ?>"
                    data-example="<?= htmlspecialchars($preset['example'], ENT_QUOTES, 'UTF-8') ?>">
                    <?= htmlspecialchars($preset['name'], ENT_QUOTES, 'UTF-8') ?>
                    </option>                    
                <?php endif; ?>
            <?php endforeach; ?>
        </select>        
        <br>
        <textarea id="ai_reply_prompt" name="ai_reply_prompt" cols="80" rows="5" maxlength="1000" 
        style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>        
        <textarea id="ai_reply_example" name="ai_reply_example" cols="80" rows="5" maxlength="2000" 
        style="width: 100%; height: 200px; resize: vertical; overflow-y: auto;"></textarea>        
        <br>
        <?php endif; ?>
        <button type="submit">登録</button>
        </div>
    </form>
</form>
</div>    
</div>

<script>
function loadPresetText_post() {
    var select = document.getElementById("post_preset_select");
    var selectedOption = select.options[select.selectedIndex]; // 選択されたオプション

    // ラジオボタン（ai_mode）の選択状態を取得
    var selectedMode = document.querySelector('input[name="ai_mode"]:checked').value;

    if(selectedMode === "3")
    {
        // 選択されたオプションの value を ai_trend_prompt に設定
        var promptTextArea = document.getElementById("ai_trend_prompt");
        promptTextArea.value = selectedOption.value;
    }
    else{
        // 選択されたオプションの value を ai_post_prompt に設定
        var promptTextArea = document.getElementById("ai_post_prompt");
        promptTextArea.value = selectedOption.value;

        // 選択されたオプションの data-example を ai_post_example に設定
        var exampleTextArea = document.getElementById("ai_post_example");
        exampleTextArea.value = selectedOption.dataset.example || "";    
    }

}

function loadPresetText_reply() {
    var select = document.getElementById("reply_preset_select");
    var selectedOption = select.options[select.selectedIndex]; // 選択されたオプション
    var promptTextArea = document.getElementById("ai_reply_prompt");
    var exampleTextArea = document.getElementById("ai_reply_example");

    // 選択されたオプションの value を ai_post_prompt に設定
    promptTextArea.value = selectedOption.value;

    // 選択されたオプションの data-example を ai_post_example に設定
    exampleTextArea.value = selectedOption.dataset.example || "";    

}

</script>

<script>
// AIモードが変更された時に実行される関数
function filterPresets() {
    const selectedMode = document.querySelector('input[name="ai_mode"]:checked').value;
    const options = document.querySelectorAll('.preset-option');

    // 各テキストエリア要素を取得
    const postPrompt = document.getElementById("ai_post_prompt");
    const postExample = document.getElementById("ai_post_example");
    const replyPrompt = document.getElementById("ai_reply_prompt");
    const replyExample = document.getElementById("ai_reply_example");
    const postPresetSelect = document.getElementById("post_preset_select");
    const replyPresetSelect = document.getElementById("reply_preset_select");

    const trendPrompt = document.getElementById("ai_trend_prompt");

    // 存在確認（エラー回避）
    if (!postPrompt || !postExample || !replyPrompt || !replyExample) {
        console.error("対象の要素が見つかりません");
        return;
    }

    // テキストエリアの値をクリア
    postPrompt.value = '';
    postExample.value = '';
    replyPrompt.value = '';
    replyExample.value = '';
    trendPrompt.value = '';

    // プリセットオプションの表示切り替え
    options.forEach(option => {
        const presetType = option.dataset.type;
        if (selectedMode === "1" && presetType === '自由') {
            option.style.display = 'block';
        } else if (selectedMode === "2" && presetType === '裏垢') {
            option.style.display = 'block';
        } else if (selectedMode === "3" && presetType === 'トレンド') {
            option.style.display = 'block';
        } else {
            option.style.display = 'none';
        }
    });

    // 最初の選択肢をリセット
    const postSelect = document.getElementById("post_preset_select");
    if (postSelect) postSelect.value = "";

    // "なし" を選んだ場合、すべて非表示
    if (selectedMode === "0") {
        postPrompt.style.display = 'none';
        postExample.style.display = 'none';
        replyPrompt.style.display = 'none';
        replyExample.style.display = 'none';
        postPresetSelect.style.display = 'none';
        replyPresetSelect.style.display = 'none';
        trendPrompt.style.display = 'none';
    }
    // "自由モード" の場合、ai_reply_prompt だけ非表示
    else if (selectedMode === "1") {
        postPrompt.style.display = 'block';
        postExample.style.display = 'none';
        replyPrompt.style.display = 'none';
        replyExample.style.display = 'none';
        postPresetSelect.style.display = 'block';
        replyPresetSelect.style.display = 'block';
        trendPrompt.style.display = 'none';
    }
    // "裏垢女子モード" の場合、すべて表示
    else if (selectedMode === "2") {
        postPrompt.style.display = 'block';
        postExample.style.display = 'block';
        replyPrompt.style.display = 'block';
        replyExample.style.display = 'block';
        postPresetSelect.style.display = 'block';
        replyPresetSelect.style.display = 'block';
        trendPrompt.style.display = 'none';
    }
    // "トレンドモード" の場合、トレンドプロンプトのみ表示
    else if (selectedMode === "3") {
        postPrompt.style.display = 'none';
        postExample.style.display = 'none';
        replyPrompt.style.display = 'none';
        replyExample.style.display = 'none';
        postPresetSelect.style.display = 'block';
        replyPresetSelect.style.display = 'none';
        trendPrompt.style.display = 'block';
    }
}

// ページが読み込まれたときにフィルタリングを実行
window.onload = function() {
    filterPresets(); // 画面が起動したときにフィルタリングを呼び出す
};
</script>

<script>
    $(document).ready(function() {
        $("input[name='new_username']").on("input", function() {
            var username = $(this).val();
            // ユーザー名が空でない場合にチェック
            if (username) {
                $.get("./ajax/check_username.php", { username: username }, function(data) {
                    var result = JSON.parse(data);
                    if (result.exists) {
                        alert("このユーザー名は既に存在します。別のユーザー名を使用してください。");
                    }
                });
            }
        });
    });
</script>
</body>
</html>
