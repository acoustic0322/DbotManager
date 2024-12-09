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

// アカウントリストを取得
$current_userid = $_SESSION['user_id'];

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
    else if ($type == 'get_access_token') {
        $id = $_POST['id'];

        echo "<script>alert('アクセストークンを取得します');</script>";

        // Pythonスクリプトのパス
        $scriptPath = escapeshellcmd('../python/tweet.py'); // Pythonスクリプトへの相対パス
//        $scriptPath = escapeshellcmd('tweet.py'); // Pythonスクリプトへの相対パス
        $command = "python $scriptPath account_id=$id mode=get_access_token";

        // Pythonスクリプトを実行
        exec($command, $output, $return_var);

        /*
        // Pythonスクリプトの実行
        $pythonScript = escapeshellcmd('/python/tweet.py');
        $command = "python $pythonScript account_id=$id mode=get_access_token";
        $output = shell_exec($command);
        */

        // Pythonスクリプトを実行
//        $pythonScriptPath = __DIR__ . '/python/tweet.py'; // tweet.pyのパスを指定
/*
        $pythonScriptPath = 'python/tweet.py'; // tweet.pyのパスを指定
        echo "<script>alert('{$pythonScriptPath}');</script>";
        $pythonPath = 'C:\\Users\\winserverroot\\AppData\\Local\\Programs\\Python\\Python38\\python.exe'; // Pythonの実行パスを指定（環境によって変更する必要があるかも）
        $command = escapeshellcmd("$pythonPath $pythonScriptPath"); // コマンドを作成
        $output = shell_exec($command); // Pythonスクリプトを実行し、その出力を取得
        if ($output === null) {
            echo "<script>alert('Pythonスクリプトの実行に失敗しました');</script>";
        } else {
            echo "<script>alert('Pythonスクリプトの実行結果: $output');</script>";
        }
*/
        /*
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
        } else {
        }

        $stmt->close();
        $conn->close();

        // 登録後にリダイレクト
        header("Location: account_list.php");
        exit;        
        */
    }    
    else{

        $new_name = $_POST['new_name'];
        $new_login_id = $_POST['new_login_id'];
        $new_login_pass = $_POST['new_login_pass'];
        $new_client_id = $_POST['new_client_id'];
        $new_client_secret = $_POST['new_client_secret'];
        $new_api_key = $_POST['new_api_key'];
        $new_api_key_secret = $_POST['new_api_key_secret'];
        $new_access_token = $_POST['new_access_token'];
        $new_access_token_secret = $_POST['new_access_token_secret'];
        $new_bearer_token = $_POST['new_bearer_token'];
        $new_refresh_token = $_POST['new_refresh_token'];

        $new_enable = isset($_POST['new_enable']) ? 1 : 0;
        $new_like_enable = isset($_POST['new_like_enable']) ? 1 : 0;
        $new_reply_enable = isset($_POST['new_reply_enable']) ? 1 : 0;
        $new_bookmark_enable = isset($_POST['new_bookmark_enable']) ? 1 : 0;
        $new_repost_enable = isset($_POST['new_repost_enable']) ? 1 : 0;
        $new_post_enable = isset($_POST['new_post_enable']) ? 1 : 0;
        $new_paid = isset($_POST['new_paid']) ? 1 : 0;
        $new_paid_like = isset($_POST['new_paid_like']) ? 1 : 0;
        $new_paid_bookmark = isset($_POST['new_paid_bookmark']) ? 1 : 0;

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
                access_token,
                access_token_secret, 
                bearer_token,
                refresh_token,
                enable,
                like_enable,
                reply_enable,
                bookmark_enable, 
                repost_enable,
                post_enable,
                paid,
                paid_like,
                paid_bookmark
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ? )");
            
            $stmt->bind_param(
                "ssssssssssssiiiiiiiii",
                $current_userid,
                $new_name,
                $new_login_id,
                $new_login_pass,
                $new_client_id,
                $new_client_secret,
                $new_api_key,
                $new_api_key_secret,
                $new_access_token,
                $new_access_token_secret, 
                $new_bearer_token,
                $new_refresh_token,
                $new_enable,
                $new_like_enable,
                $new_reply_enable,
                $new_bookmark_enable, 
                $new_repost_enable,
                $new_post_enable,
                $new_paid,
                $new_paid_like,
                $new_paid_bookmark
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



$stmt = $conn->prepare("SELECT * FROM account_master WHERE user_id = ?");
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
            width: 100%; /* 幅を調整 */
            margin-bottom: 5px; /* 各入力欄の間にスペースを設ける */
            padding: 8px;
            font-size: 16px;
        }
        .registration-form button {
            padding: 8px 12px;
            font-size: 16px;
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
   <form method="POST" action="?" class="registration-form">

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
            <input type="text" name="new_client_id" placeholder="ClientID">
        </div>
        <div class="input-group">
            <input type="text" name="new_client_secret" placeholder="ClientSecret">
        </div>
        <div class="input-group">
            <input type="text" name="new_api_key" placeholder="ApiKey">
        </div>
        <div class="input-group">
            <input type="text" name="new_api_key_secret" placeholder="ApiKeySecret">
        </div>

        <div class="input-group">
            <input type="text" id="new_access_token" name="new_access_token" placeholder="AccessToken">
            <button type="button" id="generate_token_btn" onclick="generateAccessToken()">自動発行</button>
        </div>        

        <div class="input-group">
            <input type="text" name="new_access_token_secret" placeholder="AccessSecret">
        </div>
        <div class="input-group">
            <input type="text" name="new_bearer_token" placeholder="BearerToken">
        </div>
        <div class="input-group">
            <input type="text" name="new_refresh_token" placeholder="RefreshToken">
        </div>

        <div class="input-group" checkbox-group">
            <label>
                <input type="checkbox" name="new_enable" value="1" checked>有効
            </label>
            <label>
                <input type="checkbox" name="new_post_enable" value="1" checked>ポスト機能
            </label>
            <label>
                <input type="checkbox" name="new_like_enable" value="1" checked>いいね機能
            </label>
            <label>
                <input type="checkbox" name="new_bookmark_enable" value="1" checked>ブックマーク機能
            </label>
            <label>
                <input type="checkbox" name="new_reply_enable" value="1"  checked>リプライ機能
            </label>
            <label>
                <input type="checkbox" name="new_repost_enable" value="1" checked>リポスト機能
            </label>
        </div>

        <div class="input-group">
            <label>
                <input type="checkbox" name="new_paid" value="1" checked>有料アカウント
            </label>
            <label>
                <input type="checkbox" name="new_paid_like" value="1" checked>有料API(いいね)
            </label>
            <label>
                <input type="checkbox" name="new_paid_bookmark" value="1" checked>有料API(ブックマーク)
            </label>
        </div>


    <div class="input-group">
            <button type="submit">登録</button>
        </div>
    </form>

    <h2>Xアカウント一覧</h2>
    <form method="GET" style="margin-bottom: 20px;">
        <input type="text" name="search" placeholder="ユーザー名で絞り込み" value="<?php echo isset($_GET['search']) ? htmlspecialchars($_GET['search']) : ''; ?>">
        <button type="submit">検索</button>
    </form>

    <table>
        <thead>
            <tr>
                <th>名前</th>
                <th>ログインID</th>
                <!--
                <th>ログインパス</th>
                <th>ClientID</th>
                <th>ClientSecret</th>
                <th>ApiKey</th>
                <th>ApiKeySecret</th>
                <th>AccessToken</th>
                <th>AccessTokenSecret</th>
                <th>BearerToken</th>
                <th>RefreshToken</th> -->
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result->fetch_assoc()): ?>
            <tr>
                <td><?php echo htmlspecialchars($row['name']); ?></td>
                <td><?php echo htmlspecialchars($row['login_id']); ?></td>
                <!--
                <td><?php echo htmlspecialchars($row['login_password']); ?></td>
                <td><?php echo htmlspecialchars($row['client_id']); ?></td>
                <td><?php echo htmlspecialchars($row['client_secret']); ?></td>
                <td><?php echo htmlspecialchars($row['api_key']); ?></td>
                <td><?php echo htmlspecialchars($row['api_key_secret']); ?></td>
                <td><?php echo htmlspecialchars($row['access_token']); ?></td>
                <td><?php echo htmlspecialchars($row['access_token_secret']); ?></td>
                <td><?php echo htmlspecialchars($row['bearer_token']); ?></td>
                <td><?php echo htmlspecialchars($row['refresh_token']); ?></td> 
            -->
                <td>
                    <button onclick="editUser(<?php echo $row['id']; ?>)">編集</button>
                    <form class="button_form" method="POST" action="?">
                        <input type="hidden" name="type" value="account_del">
                        <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                        <button type="button" onclick="deleteUser(this,<?php echo htmlspecialchars($row['id']) ?>)">削除</button>
                    </form>
                    <form action="generate_access_token.php" class="button_form" method="POST">
                        <input type="hidden" name="type" value="get_access_token">
                        <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                        <button type="submit">AccessToken取得</button>
<!--                        <button type="button" onclick="getAccessToken(this,<?php echo htmlspecialchars($row['id']) ?>)">AccessToken取得</button> -->
                    </form>
                </td>
            </tr>
            <?php endwhile; ?>
        </tbody>
    </table>
    </div>


    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function editUser(id) {
            // 編集機能の実装（必要に応じて）
//            alert("アカウント ID " + id + " を編集します。");
//            window.location.href = './user_edit.php?account_id='+id;
            window.location.href = './account_edit.php?id='+id;
        }

        function deleteUser(button,id) {
            if (confirm("ユーザー ID " + id + " を削除します。")) {
                button.form.submit();
            }
        }

        function getAccessToken(button,id) {
            if (confirm("ユーザー ID " + id + " のアクセストークンを取得します。")) {
                button.form.submit();
            }
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

<script>
    function generateAccessToken() {

        const url = "generate_token.php";
        const data = { account_id: 1, mode: "get_access_token" };

        fetch(url, {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            body: JSON.stringify(data),
        })
        .then(response => response.json())
        .then(result => console.log(result))
        .catch(error => console.error("Error:", error));

    }
</script>

 
</body>
</html>
