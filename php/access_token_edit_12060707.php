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

echo "<script>alert({$id});</script>";

if (empty($id)) {
    echo 'IDを指定してください';
    exit;
}

$edit_account = get_account($conn, $id);
if ($edit_account === null) {
    echo 'アカウントが存在しません';
    exit;
}

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $id = filter_input(INPUT_POST, 'id', FILTER_SANITIZE_STRING);

    if (!$id) {
        echo 'IDが無効です。';
        exit;
    }

    // Pythonスクリプトのパス
    $scriptPath = '../python/tweet.py';
    $command = escapeshellcmd("python3 $scriptPath account_id=$id mode=get_access_token");

    // Pythonスクリプトを実行
    exec($command, $output, $return_var);

    if ($return_var === 0) {
        echo '<h3>AccessToken取得成功</h3>';
        echo '<pre>' . implode("\n", $output) . '</pre>';
    } else {
        echo '<h3>エラーが発生しました</h3>';
        echo '<pre>' . implode("\n", $output) . '</pre>';
    }
}
?>


<!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title>AccessToken設定</title>
    <link rel="stylesheet" type="text/css" href="./main.css">
    <style>
        .form-group {
            margin-bottom: 20px;
        }
        .form-group label {
            display: block;
            margin-bottom: 5px;
        }
        .form-group input {
            width: 100%;
            padding: 8px;
            font-size: 16px;
        }
        .button-group {
            display: flex;
            gap: 10px;
        }
        .button-group button {
            padding: 10px 20px;
            font-size: 16px;
            cursor: pointer;
        }
    </style>
</head>
<body>


    <!-- コンテンツエリア -->
    <div class="content" id="content">
        <h1>AccessToken設定</h1>
        <form method="POST" action="?" class="registration-form">
            <div class="form-group">
                <label for="oauth_token">OAuth Token</label>
                <input type="text" id="oauth_token" name="oauth_token" placeholder="OAuth Tokenを入力してください">
            </div>
            <div class="form-group">
                <label for="oauth_verifier">OAuth Verifier</label>
                <input type="text" id="oauth_verifier" name="oauth_verifier" placeholder="OAuth Verifierを入力してください">
            </div>
            <div class="button-group">

                <form action="generate_access_token.php" class="button_form" method="POST" id="authForm">
                    <input type="hidden" name="type" value="get_access_token">
                    <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                    <input type="hidden" name="api_key" value="<?php echo htmlspecialchars($edit_account['api_key']); ?>">
                    <input type="hidden" name="api_key_secret" value="<?php echo htmlspecialchars($edit_account['api_key_secret']); ?>">
                    <button type="button" onclick="openAuthTab()">認証開始</button> 
                </form>            
<!--                <button type="button" onclick="updateAccessToken()">AccessToken発行</button>  -->
                <button type="submit">AccessToken発行</button>
                <button type="button" onclick="window.location.href='account_list.php';">戻る</button>
            </div>
        </form>
    </div>

    <script>
        async function openAuthTab() {

            // フォームから値を取得
            const apiKey = document.querySelector('input[name="api_key"]').value;
            const apiKeySecret = document.querySelector('input[name="api_key_secret"]').value;            

            alert(apiKey);

            // データをURLエンコード形式で構築
            const params = new URLSearchParams({
                api_key: apiKey,
                api_key_secret: apiKeySecret,
            });

//            alert('エラーが発生しました。認証URLを取得できませんでした。');
  //          const form = document.getElementById('authForm');
    //        const formData = new FormData(form);

            const response = await fetch('generate_access_token.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded', // フォームデータ形式
                    },
                    body: params.toString(), // 文字列に変換して送信
                });

            if (response.ok) {
                const authUrl = await response.text();
                // 別タブで認証URLを開く
                window.open(authUrl, '_blank');
            } else {
                alert('エラーが発生しました。認証URLを取得できませんでした。');
            }
        }
    </script>

<script>
        async function updateAccessToken() {
            <!--
//            $id = $_POST['id'];
/*
            echo "<script>alert('アクセストークンを取得します');</script>";

            // Pythonスクリプトのパス
            $scriptPath = escapeshellcmd('../python/tweet.py'); // Pythonスクリプトへの相対パス
            //        $scriptPath = escapeshellcmd('tweet.py'); // Pythonスクリプトへの相対パス
            $command = "python $scriptPath account_id=$id mode=get_access_token";

            // Pythonスクリプトを実行
            exec($command, $output, $return_var);
            */
           -->
        }
    </script>    

</body>
</html>
