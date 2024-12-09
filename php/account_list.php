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
            <input type="text" name="new_client_id" placeholder="ClientID" required>
        </div>
        <div class="input-group">
            <input type="text" name="new_client_secret" placeholder="ClientSecret" required>
        </div>
        <div class="input-group">
            <input type="text" name="new_api_key" placeholder="ApiKey" required>
        </div>
        <div class="input-group">
            <input type="text" name="new_api_key_secret" placeholder="ApiKeySecret" required>
        </div>

        <!--
        <div class="input-group">
            <input type="text" id="new_access_token" name="new_access_token" placeholder="AccessToken">
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
    -->

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
                <th>RefreshToken</th>
                -->
                <th>AccessToken</th>
                <th>BearerToken</th>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result->fetch_assoc()): ?>
            <tr>
                <td><?php echo htmlspecialchars($row['name']); ?></td>
                <td><?php echo htmlspecialchars($row['login_id']); ?></td>
                <!--
                <td><?php echo !empty($row['login_password']) ? '〇' : '×'; ?></td>
                <td><?php echo !empty($row['client_id']) ? '〇' : '×'; ?></td>
                <td><?php echo !empty($row['client_secret']) ? '〇' : '×'; ?></td>
                <td><?php echo !empty($row['api_key']) ? '〇' : '×'; ?></td>
                <td><?php echo !empty($row['api_key_secret']) ? '〇' : '×'; ?></td>
                <td><?php echo !empty($row['access_token']) ? '〇' : '×'; ?></td>
                <td><?php echo !empty($row['access_token_secret']) ? '〇' : '×'; ?></td>
                <td><?php echo !empty($row['bearer_token']) ? '〇' : '×'; ?></td>
                <td><?php echo !empty($row['refresh_token']) ? '〇' : '×'; ?></td>
                -->

                <td><?php echo (!empty($row['access_token']) && !empty($row['access_token_secret']))  ? '〇' : '×'; ?></td>
                <td><?php echo !empty($row['bearer_token']) ? '〇' : '×'; ?></td>

                <td>
                    <button onclick="editAccountMaster(<?php echo $row['id']; ?>)">編集</button>
                    <button onclick="editAccessToken(<?php echo $row['id']; ?>)">AccessToken取得</button>

                    <input type="hidden" name="api_key" value="<?php echo htmlspecialchars($row['api_key']); ?>">
                    <input type="hidden" name="api_key_secret" value="<?php echo htmlspecialchars($row['api_key_secret']); ?>">
                    <button onclick="getBearerToken(<?php echo $row['id']; ?>)">BearerToken取得</button>


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


    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function editAccountMaster(id) {
            window.location.href = './account_edit.php?id='+id;
        }

        function editAccessToken(id) {
            window.location.href = './access_token_edit.php?id='+id;
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
        async function getBearerToken(id) {

            if (!id) {
               alert('IDが指定されていません');
               return;
            }

            // フォームから値を取得
            const apiKey = document.querySelector('input[name="api_key"]').value;
            const apiKeySecret = document.querySelector('input[name="api_key_secret"]').value;            

            if (!apiKey || !apiKeySecret) {
                alert('APIキーまたはAPIキーシークレットが未入力です。');
                return;
            }

            // データをURLエンコード形式で構築
            const params = new URLSearchParams({
                api_key: apiKey,
                api_key_secret: apiKeySecret,
            });

//            alert('エラーが発生しました。認証URLを取得できませんでした。');
  //          const form = document.getElementById('authForm');
    //        const formData = new FormData(form);

            const response = await fetch('generate_bearer_token.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded', // フォームデータ形式
                    },
                    body: params.toString(), // 文字列に変換して送信
                });

                if (response.ok) {
                    const bearer_token = await response.text();

                    // authUrl をDBに保存する
                    const saveResponse = await fetch('save_auth_url.php', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/x-www-form-urlencoded',
                        },
                        body: new URLSearchParams({ id , bearer_token }).toString(),
                    });

                    if (saveResponse.ok) {
                        console.log('authUrl がDBに保存されました');
                        alert('BearerTokenを更新しました');
                        // 成功したらリダイレクト
                        window.location.href = 'account_list.php'; // リダイレクト先を指定
                    } else {
                        console.error('authUrl 保存エラー:', saveResponse.status);
                        alert(saveResponse.status);
                    }

                } else {
                    console.error('HTTPエラー:', response.status);
                    alert(response.status);
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
