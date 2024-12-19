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


// IDの確認
$id = $_POST['id'] ?? $_GET['id'] ?? null;

if (empty($id)) {
    echo 'IDを指定してください。';
    exit;
}


$edit_account = get_account($conn, $id);
if (!$edit_account || !is_array($edit_account)) {
    echo 'アカウント情報が見つかりません。';
    exit;
}

$edit_account = get_account($conn, $id);
if (!$edit_account || !is_array($edit_account)) {
    echo 'アカウント情報が見つかりません。';
    exit;
}

if ($_SERVER["REQUEST_METHOD"] === "POST") {
    if (isset($_POST['action'])) {
        if ($_POST['action'] === 'get_auth_url') {

            $client_id = $_POST['client_id'];
            $client_secret = $_POST['client_secret'];

//            echo "python get_refresh_token.py get_url {$client_id} {$client_secret} dummy";
        
            // Pythonスクリプトを呼び出して認証URLを生成
            $command = escapeshellcmd("python get_refresh_token.py get_url {$client_id} {$client_secret} ");
            $output = shell_exec($command);
        
            // JavaScriptで認証URLを新しいタブで開く

//            echo "
//                <script type='text/javascript'>
//                    alert('認証URLが生成されました。新しいタブで開きます。');
//                </script>
//            ";


            // 結果をJSONとしてデコード
            $response = json_decode($output, true);

            // JSONの中身を表示
            /*
            echo "取得したURL: " . $response['url'] . "<br>";
            echo "code_verifier: " . $response['code_verifier'] . "<br>";
            echo "code_challenge: " . $response['code_challenge'] . "<br>";
            */

            // デコードに失敗した場合
            if ($response === null) {
                echo "JSONのデコードに失敗しました。";
            } else {
                // HTMLのラベルに値を埋め込む
                $url = htmlspecialchars($response['url']);
                $code_verifier = htmlspecialchars($response['code_verifier']);
                $code_challenge = htmlspecialchars($response['code_challenge']);
                $client_credentials = htmlspecialchars($response['client_credentials']);
            }

            /*
            echo "
                <script type='text/javascript'>
                    setTimeout(function() {
                        window.open('{$auth_url}', '_blank');
                    }, 1000); // 100ms後に新しいタブを開く
                </script>
            ";
            */

//            echo "認証URLを生成しました: <a href='{$auth_url}' target='_blank'>{$auth_url}</a>";

}
        elseif ($_POST['action'] === 'fetch_refresh_token') {

            $client_id = $_POST['client_id'];
            $client_secret = $_POST['client_secret'];
            $auth_code = $_POST['auth_code'];
            $code_verifier = $_POST['code_verifier'];
            $code_challenge = $_POST['code_challenge'];
            $client_credentials = $_POST['client_credentials'];

            // URLのクエリ部分を解析
            $parsed_url = parse_url($auth_code);

            parse_str($parsed_url['query'], $query_params);
            // 'code' パラメータの値を取得
            $auth_code = $query_params['code'];

            // code_verifier と code_challenge が空でないか確認
            if (empty($code_verifier) || empty($code_challenge)) {
                echo "code_verifier または code_challenge が空です。";
                exit;
            }

            echo "python get_refresh_token.py fetch_tokens \"{$client_id}\" \"{$client_secret}\" \"{$auth_code}\" \"{$code_verifier}\" \"{$code_challenge}\" \"{$client_credentials}\"";

            // Pythonスクリプトを呼び出してトークンを取得
            $command = escapeshellcmd("python get_refresh_token.py fetch_tokens \"{$client_id}\" \"{$client_secret}\" \"{$auth_code}\" \"{$code_verifier}\" \"{$code_challenge}\" \"{$client_credentials}\"");
            $tokens = shell_exec($command);
        
            echo "取得したトークン: <pre>{$tokens}</pre>";

        }
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
        <h1>RefreshToken設定</h1>
        <form method="POST" action="?" class="registration-form">
            <div class="form-group">
                <label for="url_label">認証URL: ※このURLにアクセスしてください</label>
                <input type="text" id="url_label" value="<?php echo $url; ?>" disabled>

                <label for="code_verifier">code_verifier:</label>
                <input type="text" id="code_verifier" name="code_verifier" value="<?php echo $code_verifier; ?>" >

                <label for="code_challenge">code_challenge:</label>
                <input type="text" id="code_challenge" name="code_challenge" value="<?php echo $code_challenge; ?>" >

                <label for="client_credentials">client_credentials:</label>
                <input type="text" id="client_credentials" name="client_credentials" value="<?php echo $client_credentials; ?>" >

                <label for="url">This URL</label>
                <input type="text" id="auth_code" name="auth_code" placeholder="認証画面のThis URLをペーストしてください">
                
            </div>
            <div class="button-group">

                <form action="generate_access_token.php" class="button_form" method="POST" id="authForm">
                    <input type="hidden" name="type" value="get_access_token">
                    <input type="hidden" name="id" value="<?php echo htmlspecialchars($id) ?>">
                    <input type="hidden" name="api_key" value="<?php echo htmlspecialchars($edit_account['api_key']); ?>">
                    <input type="hidden" name="api_key_secret" value="<?php echo htmlspecialchars($edit_account['api_key_secret']); ?>">
                    <button type="button" onclick="openAuthTab2()">認証開始</button> 
                <div class="button-group">        
                    <input type="hidden" name="client_id" value="<?php echo htmlspecialchars($edit_account['client_id']); ?>">
                    <input type="hidden" name="client_secret" value="<?php echo htmlspecialchars($edit_account['client_secret']); ?>">
                    <button type="submit" name="action" value="get_auth_url">認証URL生成</button> 
                    <button type="submit" name="action" value="fetch_refresh_token">RefreshToken発行</button> 
                    <button type="button" onclick="window.location.href='account_list.php';">戻る</button>
                </div>
                </form>    
            </div>
        </form>
    </div>

    <script>
        async function openAuthTab2() {
//            alert('getBearerToken');


            // フォームから値を取得
            const apiKey = document.querySelector('input[name="api_key"]').value;
            const apiKeySecret = document.querySelector('input[name="api_key_secret"]').value; 
            const clientId = document.querySelector('input[name="client_id"]').value;            
            const id = document.querySelector('input[name="id"]').value;            
            if (!id) {
               alert('IDが指定されていません');
               return;
            }

            if (!apiKey || !apiKeySecret) {
                alert('APIキーまたはAPIキーシークレットが未入力です。');
                return;
            }

//            alert('getBearerToken2');
            // データをURLエンコード形式で構築
            const params = new URLSearchParams({
                api_key: apiKey,
                api_key_secret: apiKeySecret,
                client_id: clientId
            });

//            alert('エラーが発生しました。認証URLを取得できませんでした。');
  //          const form = document.getElementById('authForm');
    //        const formData = new FormData(form);


//            alert('getBearerToken3');
            const response = await fetch('generate_refresh_url.php', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded', // フォームデータ形式
                    },
                    body: params.toString(), // 文字列に変換して送信
                });

                if (response.ok) {
//                    alert('ok');

                    const authUrl = await response.text();
                    alert(authUrl);
                    // 別タブで認証URLを開く
                    window.open(authUrl, '_blank');
                } else {
//                    alert('ng');
                    console.error('HTTPエラー:', response.status);
                    alert(response.status);
                }
            }

    </script>


</body>
</html>
