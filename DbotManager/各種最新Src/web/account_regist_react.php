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

$system_prompts = [];
$result = $conn->query("SELECT `key`, `value` FROM system_master");

while ($row = $result->fetch_assoc()) {
    $system_prompts[$row['key']] = [
        'value' => $row['value']
    ];
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
//        $new_login_pass = $_POST['new_login_pass'];
        $new_client_id = isset($_POST['new_client_id']) ? $_POST['new_client_id'] : "";//$_POST['new_client_id'];
        $new_client_secret = isset($_POST['new_client_secret']) ? $_POST['new_client_secret'] : "";//$_POST['new_client_secret'];
        $new_api_key = "dummy";//$_POST['new_api_key'];
        $new_api_key_secret = "dummy";//$_POST['new_api_key_secret'];

        $new_access_token = '';
        $new_access_token_secret = '';
        /*
        $new_access_token = $_POST['new_access_token'];
        $new_access_token_secret = $_POST['new_access_token_secret'];
        $new_bearer_token = $_POST['new_bearer_token'];
        $new_refresh_token = $_POST['new_refresh_token'];
        */

        $new_enable = isset($_POST['new_enable']) ? 1 : 0;

        $new_like_enable = 1;//isset($_POST['new_like_enable']) ? 1 : 0;
        $new_reply_enable = 0;//isset($_POST['new_reply_enable']) ? 1 : 0;
        $new_bookmark_enable = 1;//isset($_POST['new_bookmark_enable']) ? 1 : 0;
        $new_repost_enable = 1;//isset($_POST['new_repost_enable']) ? 1 : 0;
        $new_post_enable = 0;//isset($_POST['new_post_enable']) ? 1 : 0;
        $new_paid = 1;//isset($_POST['new_paid']) ? 1 : 0;
        $new_paid_like = 1;//isset($_POST['new_paid_like']) ? 1 : 0;
        $new_paid_bookmark = 1;//isset($_POST['new_paid_bookmark']) ? 1 : 0;

        // 予約の処理（Reserve1-4）
        $reserve1_enable = 0;//isset($_POST['reserve1_enable']) ? 1 : 0;
        $reserve1_start_hour = 8;//$_POST['reserve1_start_hour'] ?? 0;
        $reserve1_end_hour = 17;//$_POST['reserve1_end_hour'] ?? 0;
        $reserve1_count = 0;//$_POST['reserve1_count'] ?? 0;

        $reserve2_enable = 0;//isset($_POST['reserve2_enable']) ? 1 : 0;
        $reserve2_start_hour = 8;//$_POST['reserve2_start_hour'] ?? 0;
        $reserve2_end_hour = 17;//$_POST['reserve2_end_hour'] ?? 0;
        $reserve2_count = 0;//$_POST['reserve2_count'] ?? 0;

        $reserve3_enable = 0;//isset($_POST['reserve3_enable']) ? 1 : 0;
        $reserve3_start_hour = 8;//$_POST['reserve3_start_hour'] ?? 0;
        $reserve3_end_hour = 17;//$_POST['reserve3_end_hour'] ?? 0;
        $reserve3_count = 0;//$_POST['reserve3_count'] ?? 0;

        $reserve4_enable = 0;//isset($_POST['reserve4_enable']) ? 1 : 0;
        $reserve4_start_hour = 8;//$_POST['reserve4_start_hour'] ?? 0;
        $reserve4_end_hour = 17;//$_POST['reserve4_end_hour'] ?? 0;
        $reserve4_count = 0;//$_POST['reserve4_count'] ?? 0;

        $reserve1_ai = 0;//isset($_POST['reserve1_ai']) ? 1 : 0;
        $reserve2_ai = 0;//isset($_POST['reserve2_ai']) ? 1 : 0;
        $reserve3_ai = 0;//isset($_POST['reserve3_ai']) ? 1 : 0;
        $reserve4_ai = 0;//isset($_POST['reserve4_ai']) ? 1 : 0;

        $new_dmm_id = "";//$_POST['new_dmm_id'];

        $new_search_enable = 0;//isset($_POST['new_search_enable']) ? 1 : 0;
        $new_check_interval = 60;//$_POST['check_interval'] ?? 60;

        $new_proxy_enable = isset($_POST['new_proxy_enable']) ? 1 : 0;
        $new_proxy_url = $_POST['new_proxy_url'];

        $new_use_admin_api = 0;//isset($_POST['new_use_admin_api']) ? 1 : 0;
        $new_api_master_id = 0;//$_SESSION['api_master_id'];

        $ai_post_enable = 0;//isset($_POST['ai_post_enable']) ? 1 : 0;
        $ai_reply_enable = 0;//isset($_POST['ai_reply_enable']) ? 1 : 0;

        $ai_photo_enable = 0;//isset($_POST['ai_photo_enable']) ? 1 : 0;
        $ai_movie_enable = 0;//isset($_POST['ai_movie_enable']) ? 1 : 0;
        $ai_media_selection_rate = 50;//$_POST['ai_media_selection_rate'];


//        $ai_post_prompt = $_POST['ai_post_prompt'] ?? '';
//        $ai_trend_prompt = $_POST['ai_trend_prompt'] ?? '';
//        $ai_reply_prompt = $_POST['ai_reply_prompt'] ?? '';
//        $ai_post_example = $_POST['ai_post_example'] ?? '';
//        $ai_reply_example = $_POST['ai_reply_example'] ?? '';

        $ai_post_prompt = "";
        $ai_reply_prompt = "";
        $ai_post_example = "";
        $ai_reply_example = "";
        $ai_trend_prompt = "";


        $ai_mode = '';//$_POST['ai_mode'] ?? '';

        // 2025.10.25 AIプロンプト関連の列追加
        $ai_uraaka_prompt       = '';//$system_prompts['ai_uraaka_prompt']['value']       ?? '';
        $ai_uraaka_past_tweet   = '';//$system_prompts['ai_uraaka_past_tweet']['value']   ?? '';
        $ai_trend_prompt_yahoo  = '';//$system_prompts['ai_trend_prompt_yahoo']['value']  ?? '';
        $ai_trend_prompt_x      = '';//$system_prompts['ai_trend_prompt_x']['value']      ?? '';
        $ai_btc_prompt          = '';//$system_prompts['ai_btc_prompt']['value']          ?? '';      
        $ai_free_prompt          = '';//$system_prompts['ai_free_prompt']['value']          ?? '';      

        $ai_free_prompt_rep     = '';//$system_prompts['ai_free_prompt_rep']['value']          ?? '';      
        $ai_free_past_rep     = '';//$system_prompts['ai_free_past_rep']['value']          ?? '';      
        $ai_uraaka_prompt_rep     = '';//$system_prompts['ai_free_prompt_rep']['value']          ?? '';      
        $ai_uraaka_past_rep   = '';//$system_prompts['ai_uraaka_past_rep']['value']   ?? '';

        $ai_prompt_textbox = '';//trim($_POST['ai_prompt'] ?? '');
        $ai_past_tweet_textbox = '';//trim($_POST['ai_past_tweet'] ?? '');

        $ai_prompt_rep_textbox = '';//trim($_POST['ai_reply_prompt'] ?? '');
        $ai_past_rep_textbox = '';//trim($_POST['ai_past_reply'] ?? '');

        $regist_type = "react";

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
                ,ai_uraaka_prompt 
                ,ai_uraaka_past_tweet 
                ,ai_trend_prompt_yahoo 
                ,ai_trend_prompt_x 
                ,ai_btc_prompt 
                ,ai_free_prompt
                ,ai_uraaka_prompt_rep
                ,ai_uraaka_past_rep
                ,ai_free_prompt_rep                
                ,ai_free_past_rep                
                ,ai_photo_enable
                ,ai_movie_enable
                ,ai_media_selection_rate
                ,regist_type
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)");
            
            $stmt->bind_param(
                "sssssssiiiiiiiiiiiiiiiiiiiiiiiiiiiiisiisiiiiissssisssssssssssssss",
                $current_userid,    //s
                $new_name,          //s
                $new_login_id,      //s
//                $new_login_pass,    //s
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
                ,$regist_type
            );

            $stmt->execute();

            // 追加：INSERTしたID取得
            $insert_id = $conn->insert_id;

            $stmt->close();
            $conn->close();

            // 登録後にリダイレクト
//            header("Location: account_list.php");

            // 修正：リダイレクト先変更
            header("Location: ./redirect.php?id=".$insert_id."&type=2_react");

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
  <title>Xアカウント登録</title>
  <link rel="stylesheet" href="./css/admin-dashboard.css" />
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;700&display=swap" rel="stylesheet">
</head>
<body>
<div class="layout">
    <?php require PARTS_DIR.'/sidebar.php'; ?>
<!--    <div class="main"> -->
   <div class="content" id="content">

    <h2 class="tx-white">Xアカウント クイック登録</h2>
   <form method="POST" action="?">

    <div class="input-group">
        <input type="text" id="new_name" name="new_name" placeholder="名前" required>
    </div>
    <div class="input-group">
        <input type="text" id="new_login_id" name="new_login_id" placeholder="XアカウントID" required>
    </div>
    <div class="input-group" checkbox-group">
        <label>
            <input type="checkbox" name="new_proxy_enable" value="0">プロキシ
        </label><br>
        <input type="text" name="new_proxy_url" placeholder="プロキシURL">
        <br>
    </div>

    <button type="submit">登録</button>
    </div>
    </form>
</form>
</div>    
</div>

<script>
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
const systemPrompts = <?= json_encode($system_prompts, JSON_UNESCAPED_UNICODE); ?>;
</script>

<script>
// AIモードが変更された時に実行される関数
function filterPresets() {
}

// ページが読み込まれたときにフィルタリングを実行
window.onload = function() {
    filterPresets(); // 画面が起動したときにフィルタリングを呼び出す
};

function editXLogin2(id) {
    window.location.href = './redirect.php?id='+id+'&type=2';
}
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
