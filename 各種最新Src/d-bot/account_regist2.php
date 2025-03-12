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
, (select count(*)  from comment_master cm1 where cm1.account_id = am.id and mode='post')  as post_comment_count
, (select count(*)  from comment_master cm1 where cm1.account_id = am.id and mode='reply') as reply_comment_count 
, (select count(*)  from search_list sl where sl.post_account_id = am.id) as search_list_count 
FROM account_master am WHERE am.user_id = ?");

$stmt->bind_param("s", $current_userid);
$stmt->execute();
$result = $stmt->get_result();
$stmt->close();

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
        $new_login_pass = $_POST['new_login_pass'];
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


        $new_dmm_id = $_POST['new_dmm_id'];

        $new_search_enable = 0;//isset($_POST['new_search_enable']) ? 1 : 0;
        $new_check_interval = 60;//$_POST['check_interval'] ?? 60;

        $new_proxy_enable = isset($_POST['new_proxy_enable']) ? 1 : 0;
        $new_proxy_url = $_POST['new_proxy_url'];

        $new_use_admin_api = 1;//isset($_POST['new_use_admin_api']) ? 1 : 0;
        $new_api_master_id = $_SESSION['api_master_id'];


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
                login_password,
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
                dmm_id ,
                search_enable ,
                proxy_enable ,
                proxy_url ,
                api_master_id ,
                use_admin_api ,
                check_interval
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?)");
            
            $stmt->bind_param(
                "ssssssssiiiiiiiiisiiiiiiiiiiiiiiiiiisiii",
                $current_userid,
                $new_name,
                $new_login_id,
                $new_login_pass,
                $new_client_id,
                $new_client_secret,
                $new_api_key,
                $new_api_key_secret,
                $new_enable,
                $new_like_enable,
                $new_reply_enable,
                $new_bookmark_enable, 
                $new_repost_enable,
                $new_post_enable,
                $new_paid,
                $new_paid_like,
                $new_paid_bookmark,
                $reserve1_enable , 
                $reserve1_start_hour , 
                $reserve1_end_hour , 
                $reserve1_count , 
                $reserve2_enable , 
                $reserve2_start_hour , 
                $reserve2_end_hour , 
                $reserve2_count , 
                $reserve3_enable , 
                $reserve3_start_hour , 
                $reserve3_end_hour , 
                $reserve3_count , 
                $reserve4_enable , 
                $reserve4_start_hour , 
                $reserve4_end_hour , 
                $reserve4_count ,
                $new_dmm_id,
                $new_search_enable,
                $new_proxy_enable,
                $new_proxy_url,
                $new_api_master_id,
                $new_use_admin_api,
                $new_check_interval
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
, (select count(*)  from comment_master cm1 where cm1.account_id = am.id and mode='post')  as post_comment_count
, (select count(*)  from comment_master cm1 where cm1.account_id = am.id and mode='reply') as reply_comment_count 
, (select count(*)  from search_list sl where sl.post_account_id = am.id) as search_list_count 
FROM account_master am WHERE am.user_id = ?");
$stmt->bind_param("s", $current_userid);
$stmt->execute();
$result = $stmt->get_result();
?>

<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>Xアカウント一覧</title>
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

   <!-- コンテンツエリア -->
   <div class="content" id="content">
   <h2>新規Xアカウント登録(貸出)</h2>
   <form method="POST" action="?">

    <div class="input-group">
        <input type="text" id="new_name" name="new_name" placeholder="名前" required>
    </div>
    <div class="input-group">
        <input type="text" id="new_login_id" name="new_login_id" placeholder="ログインID" required>
    </div>
    <div class="input-group">
        <input type="text" id="new_login_pass" name="new_login_pass" placeholder="ログインパス">
    </div>

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
        <input type="number" id="check_interval" name="check_interval" min="5" max="6000" step="1" value="60" style="width: 50px;">
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
            <input type="checkbox" name="reserve1_enable" value="1" checked>時間帯１
            <input type="text" id="reserve1_start_hour" name="reserve1_start_hour" class="short" placeholder="開始" > ～
            <input type="text" id="reserve1_end_hour" name="reserve1_end_hour" class="short" placeholder="終了" > 時　
            <input type="text" id="reserve1_count" name="reserve1_count" class="short" placeholder="" > 回
        </label><br>
        <label>
            <input type="checkbox" name="reserve2_enable" value="1" checked>時間帯２
            <input type="text" id="reserve2_start_hour" name="reserve2_start_hour" class="short" placeholder="開始" > ～
            <input type="text" id="reserve2_end_hour" name="reserve2_end_hour" class="short" placeholder="終了" > 時　
            <input type="text" id="reserve2_count" name="reserve2_count" class="short" placeholder="" > 回
        </label><br>
        <label>
            <input type="checkbox" name="reserve3_enable" value="1" checked>時間帯３
            <input type="text" id="reserve3_start_hour" name="reserve3_start_hour" class="short" placeholder="開始" > ～
            <input type="text" id="reserve3_end_hour" name="reserve3_end_hour" class="short" placeholder="終了" > 時　
            <input type="text" id="reserve3_count" name="reserve3_count" class="short" placeholder="" > 回
        </label><br>
        <label>
            <input type="checkbox" name="reserve4_enable" value="1" checked>時間帯４
            <input type="text" id="reserve4_start_hour" name="reserve4_start_hour" class="short" placeholder="開始" > ～
            <input type="text" id="reserve4_end_hour" name="reserve4_end_hour" class="short" placeholder="終了" > 時　
            <input type="text" id="reserve4_count" name="reserve4_count" class="short" placeholder="" > 回
        </label><br>
        <br>

        <div class="input-group">
            <button type="submit">登録</button>
        </div>
    </form>
</form>
</div>    

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


<style>
    /* テキストボックスの幅を80%に設定 */
    .input-group input[type="text"] {
        width: 80%; /* 幅を80%に設定 */
        padding: 8px; /* パディングを追加 */
        font-size: 12px; /* フォントサイズを調整 */
        margin-bottom: 5px; /* ボックス間のスペース */
        box-sizing: border-box; /* パディングを含めた幅を計算 */
    }
</style> 

<style>
    /* テキストボックスの幅を短く設定 */
    input[type="text"].short {
        width: 40px; /* 必要に応じて調整 */
    }
</style>

</body>
</html>
