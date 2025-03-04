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
            header("Location: account_list_search.php");
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
        header("Location: account_list_search.php");
        exit;        
    }
    else{

        $new_name = $_POST['new_name'];
        $new_login_id = $_POST['new_login_id'];
        $new_login_pass = $_POST['new_login_pass'];
        $new_client_id = $_POST['new_client_id'];
        $new_client_secret = $_POST['new_client_secret'];
        $new_api_key = '';//$_POST['new_api_key'];
        $new_api_key_secret = '';//$_POST['new_api_key_secret'];

        $new_access_token = '';
        $new_access_token_secret = '';
        /*
        $new_access_token = $_POST['new_access_token'];
        $new_access_token_secret = $_POST['new_access_token_secret'];
        $new_bearer_token = $_POST['new_bearer_token'];
        $new_refresh_token = $_POST['new_refresh_token'];
        */

        $new_enable = isset($_POST['new_enable']) ? 1 : 0;

        $new_like_enable = 0;//isset($_POST['new_like_enable']) ? 1 : 0;
        $new_reply_enable = 0;//isset($_POST['new_reply_enable']) ? 1 : 0;
        $new_bookmark_enable = 0;//isset($_POST['new_bookmark_enable']) ? 1 : 0;
        $new_repost_enable = 0;//isset($_POST['new_repost_enable']) ? 1 : 0;
        $new_post_enable = 0;//isset($_POST['new_post_enable']) ? 1 : 0;
        $new_paid = isset($_POST['new_paid']) ? 1 : 0;
        $new_paid_like = 0;//isset($_POST['new_paid_like']) ? 1 : 0;
        $new_paid_bookmark = 0;//isset($_POST['new_paid_bookmark']) ? 1 : 0;

        // 予約の処理（Reserve1-4）
        $reserve1_enable = 0;//isset($_POST['reserve1_enable']) ? 1 : 0;
        $reserve1_start_hour = 0;//$_POST['reserve1_start_hour'] ?? 0;
        $reserve1_end_hour = 0;//$_POST['reserve1_end_hour'] ?? 0;
        $reserve1_count = 0;//$_POST['reserve1_count'] ?? 0;

        $reserve2_enable = 0;//isset($_POST['reserve2_enable']) ? 1 : 0;
        $reserve2_start_hour = 0;//$_POST['reserve2_start_hour'] ?? 0;
        $reserve2_end_hour = 0;//$_POST['reserve2_end_hour'] ?? 0;
        $reserve2_count = 0;//$_POST['reserve2_count'] ?? 0;

        $reserve3_enable = 0;//isset($_POST['reserve3_enable']) ? 1 : 0;
        $reserve3_start_hour = 0;//$_POST['reserve3_start_hour'] ?? 0;
        $reserve3_end_hour = 0;//$_POST['reserve3_end_hour'] ?? 0;
        $reserve3_count = 0;//$_POST['reserve3_count'] ?? 0;

        $reserve4_enable = 0;//isset($_POST['reserve4_enable']) ? 1 : 0;
        $reserve4_start_hour = 0;//$_POST['reserve4_start_hour'] ?? 0;
        $reserve4_end_hour = 0;//$_POST['reserve4_end_hour'] ?? 0;
        $reserve4_count = 0;//$_POST['reserve4_count'] ?? 0;


        $new_dmm_id = '';//$_POST['new_dmm_id'];

        $new_search_enable = 1; //isset($_POST['new_search_enable']) ? 1 : 0;
        $new_proxy_enable = '';//isset($_POST['new_proxy_enable']) ? 1 : 0;
        $new_proxy_url = '';//$_POST['new_proxy_url'];

        $new_use_admin_api = 0;//isset($_POST['new_use_admin_api']) ? 1 : 0;
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
                use_admin_api
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? , ?, ?, ?, ?, ?, ?)");
            
            $stmt->bind_param(
                "ssssssssiiiiiiiiisiiiiiiiiiiiiiiiiiisii",
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
                $new_use_admin_api
                );

            $stmt->execute();
            $stmt->close();
            $conn->close();
            // 登録後にリダイレクト
            header("Location: account_list_search.php");
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
FROM account_master am WHERE am.user_id = ? and am.use_admin_api = 0");
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
   <h2>新規Xアカウント登録</h2>
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

        <div class="input-group">
            <input type="text" name="new_client_id" placeholder="ClientID" required>
        </div>
        <div class="input-group">
            <input type="text" name="new_client_secret" placeholder="ClientSecret" required>
        </div>

        <div class="input-group" checkbox-group">
            <label>
                <input type="checkbox" name="new_enable" value="1" checked>有効
            </label><br>

        <!--

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
            -->

            <?php if (isset($_SESSION['check_enable']) && $_SESSION['check_enable'] == 1): ?>
            <label>
                <input type="checkbox" name="new_search_enable" value="0">監視実施
            </label><br>
            <?php endif; ?>

            <!--
            <label>
                <input type="checkbox" name="new_proxy_enable" value="0">プロキシ
            </label><br>
            <input type="text" name="new_proxy_url" placeholder="プロキシURL">
            <br>
            -->

        </div>

        <div class="input-group">
            <?php if ((isset($_SESSION['like_enable']) && $_SESSION['like_enable'] == 1) || 
              (isset($_SESSION['bookmark_enable']) && $_SESSION['bookmark_enable'] == 1)): ?>
                <label>
                    <input type="checkbox" name="new_paid" value="1" checked>有料アカウント
                </label><br>
            <?php endif; ?>

            <!--
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
            -->
        </div>

        <!--
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
            -->



        <div class="input-group">
            <button type="submit">登録</button>
        </div>
    </form>



    <h2>Xアカウント一覧</h2>
    <form method="GET" style="margin-bottom: 20px;">
        <input type="text" name="search" placeholder="ユーザー名で絞り込み" value="<?php echo isset($_GET['search']) ? htmlspecialchars($_GET['search']) : ''; ?>">
        <button type="submit">検索</button>
    </form>

    <div style="display: flex; align-items: center; gap: 10px;">
    <span>チェックONのアカウントに対し</span>

    <form method="GET" action="?" style="margin: 0; display: inline-block;">
       
        <select id="command_option" name="command" onchange="toggleCommandSource()">
<!--            <option value="comment">コメント設定</option>-->

            <?php if (isset($_SESSION['check_enable']) && $_SESSION['check_enable'] == 1): ?>
<!--            <option value="search">監視リプ,モノマネ</option> -->
            <option value="searchFrom">監視実施</option> 
            <?php endif; ?>
            
        </select>
    </form>

    <span>を</span>

    <div id="action1_source" style="margin-left: 10px;">
    <form method="GET" action="?" style="margin: 0; display: inline-block;">
    <select id="action1_option" name="action1" onchange="toggleDuplicateSource()">
        <option value="duplicate">複製する</option>
        <option value="delete">削除する</option>
    </select>
    </div>

    <div id="action2_source" style="display: none; margin-left: 10px;">
    <form method="GET" action="?" style="margin: 0; display: inline-block;">
    <select id="action2_option" name="action2" >
        <option value="on">ONにする</option>
        <option value="off">OFFにする</option>
    </select>
    </div>

</form>

    <div id="duplicate_source" style="display: none; margin-left: 10px;">
    <span>(複製元：</span>
    <select id="form_account_id" name="xuser">
        <option value="">未選択</option>
        <?php foreach ($xusers as $k => $row) { ?>
            <option value="<?php echo e($row['id']) ?>" <?php echo ( (string)$row['id'] === (string)$xuser_id ? 'selected' : '' ); ?>><?php echo e($row['name']) ?></option>
        <?php } ?>
    </select>
    <span>)</span>
    </div>

    <!-- 実行ボタン -->
    <button type="submit" onclick="executeAction()" style="margin-left: 10px;">実行</button>

    <script>
    function toggleDuplicateSource() {
        const actionOption = document.getElementById('action1_option');
        const duplicateSource = document.getElementById('duplicate_source');
        if (actionOption.value === "duplicate") {
            // 複製するが選択された場合
            duplicateSource.style.display = "inline-block";
        } else {
            // その他の場合
            duplicateSource.style.display = "none";
        }
    }

    function toggleCommandSource() {
        const commandOption = document.getElementById('command_option');
        const action1Source = document.getElementById('action1_source');
        const action2Source = document.getElementById('action2_source');
        if (commandOption.value === "searchFrom") {
            // 監視実施が選択された場合
            action1Source.style.display = "none";
            action2Source.style.display = "inline-block";
        } else {
            // その他の場合
            action1Source.style.display = "inline-block";
            action2Source.style.display = "none";
        }

        toggleDuplicateSource();
    }
    function executeAction() {
        // フォームの要素を取得
        const command = document.getElementById('command_option').value;
        const action1 = document.getElementById('action1_option').value;
        const action2 = document.getElementById('action2_option').value;
        const form_account_id = document.getElementById('form_account_id').value;

        // チェックされたIDを取得
        const selectedIds = Array.from(document.querySelectorAll('input[name="selected_ids[]"]:checked'))
            .map(checkbox => checkbox.value);

        if (selectedIds.length === 0) {
            alert("チェックされたアカウントがありません。");
            return;
        }

//        alert(command);
//        alert(action1);
//        alert(action2);
//        alert(selectedIds);
//        alert(form_account_id);

        // 必要なデータを送信
        fetch('account_process.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                command: command,
                action1: action1,
                action2: action2,
                selected_ids: selectedIds,
                form_account_id : form_account_id,
            }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // サーバーからのメッセージを表示
            window.location.reload(); // ページをリロード
        })        
        .catch(error => {
            console.error('エラー:', error);
        });
    }    

    // ページロード時に初期状態をチェック
    document.addEventListener('DOMContentLoaded', toggleDuplicateSource);
    </script>    



</div>    

<!--
    <form method="GET" action="?">
        <span>チェックONのアカウントに対し</span>

        <form method="GET" action="?">
        <select id="command_option" name="command">
          <option value="1">コメント設定</option>
          <option value="2">監視設定</option>
        </select>
        </form>


        <span>を</span>

        <form method="GET" action="?">
        <select id="action_option" name="action">
          <option value="1">複製する</option>
          <option value="2">削除する</option>
        </select>
        </form>
      
      <span>(複製元：</span>
      <select id="form_xuser" name="xuser">
        <option value="">未選択</option>
        <?php foreach ($xusers as $k => $row) { ?>
            <option value="<?php echo e($row['id']) ?>" <?php echo ( (string)$row['id'] === (string)$xuser_id ? 'selected' : '' ); ?>><?php echo e($row['name']) ?></option>
        <?php } ?>
      </select>
      <span>)</span>
   </form>    
        -->
    <table>
    <thead>
        <tr>
            <th><input type="checkbox" id="select_all" onclick="toggleSelectAll()"></th>
            <th>名前</th>
            <th>ログインID</th>
<!--            <th>ﾎﾟｽﾄｺﾒﾝﾄ</th> -->
<!--            <th>ﾘﾌﾟﾗｲﾄｺﾒﾝﾄ</th> -->
            <?php if (isset($_SESSION['check_enable']) && $_SESSION['check_enable'] == 1): ?>
<!--            <th>自動ﾘﾌﾟ,ﾓﾉﾏﾈ</th> -->
            <th>監視実施</th>
            <?php endif; ?>
            <th>通常認証</th>
<!--            <th>メディア認証</th> -->
            <th>操作</th>
        </tr>
    </thead>
    <tbody>
        <?php while ($row = $result->fetch_assoc()): ?>
            <tr>
            <td>
                <input type="checkbox" name="selected_ids[]" value="<?php echo htmlspecialchars($row['id']); ?>">
            </td>
            <td><?php echo htmlspecialchars($row['name']); ?></td>
            <td><?php echo htmlspecialchars($row['login_id']); ?></td>
<!--            <td><?php echo htmlspecialchars($row['post_comment_count']); ?>件</td> -->
<!--            <td><?php echo htmlspecialchars($row['reply_comment_count']); ?>件</td> -->

            <?php if (isset($_SESSION['check_enable']) && $_SESSION['check_enable'] == 1): ?>
<!--            <td><?php echo htmlspecialchars($row['search_list_count']); ?>件</td> -->
            <td><?php echo !empty($row['search_enable']) ? '〇' : '×'; ?></td> 
            <?php endif; ?>
            
            <td><?php echo (!empty($row['bearer_token']) && !empty($row['refresh_token']))  ? '〇' : '×'; ?></td>
<!--            <td><?php echo !empty($row['access_token']) ? '〇' : '×'; ?></td> -->
            <td>
                <button onclick="editAccountMaster(<?php echo $row['id']; ?>)">編集</button>
<!--                <button onclick="editComment(<?php echo $row['id']; ?>)">ｺﾒﾝﾄ一覧</button>-->
<!--                <button onclick="registComment(<?php echo $row['id']; ?>)">ｺﾒﾝﾄ登録</button>-->

                <?php if (isset($_SESSION['check_enable']) && $_SESSION['check_enable'] == 1): ?>
<!--                <button onclick="editCheckAccount(<?php echo $row['id']; ?>)">自動ﾘﾌﾟ,ﾓﾉﾏﾈ編集</button>-->
                <?php endif; ?>

                <button onclick="editXLogin2(<?php echo $row['id']; ?>)">通常認証</button>
<!--                <button onclick="editXLogin1(<?php echo $row['id']; ?>)">ﾒﾃﾞｨｱ認証</button> -->
                <form class="button_form" method="POST" action="?">
                    <input type="hidden" name="type" value="account_del">
                    <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                    <button type="button" onclick="deleteUser(this,<?php echo htmlspecialchars($row['id']) ?>)">削除</button>
                </form>
            </td>
        </tr>
        <?php endwhile; ?>
    </tbody>
</table>

    </div>

    <script>
    // 全選択/全解除機能
    function toggleSelectAll() {
        const checkboxes = document.querySelectorAll('input[name="selected_ids[]"]');
        const selectAllCheckbox = document.getElementById('select_all');
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAllCheckbox.checked;
        });
    }
</script>


    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function editAccountMaster(id) {
            window.location.href = './account_edit.php?id='+id;
        }

        function editXLogin1(id) {
            window.location.href = './redirect.php?id='+id+'&type=1';
        }

        function editXLogin2(id) {
            window.location.href = './redirect.php?id='+id+'&type=2';
        }
 

        function deleteUser(button,id) {
            if (confirm("ユーザー ID " + id + " を削除します。")) {
                button.form.submit();
            }
        }

        function editComment(id) {
            window.location.href = './comment_list.php?account_id='+id;
        }

        function registComment(id) {
            window.location.href = './comment_regist.php?account_id='+id;
        }

        function editCheckAccount(id) {
            window.location.href = './search_list.php?account_id='+id;
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
