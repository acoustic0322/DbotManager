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

    <?php require __DIR__ . '/_lib/config.php';?>

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

                <form action="generate_access_token.php" class="button_form" method="POST">
                    <input type="hidden" name="type" value="get_access_token">
                    <input type="hidden" name="id" value="<?php echo htmlspecialchars($row['id']) ?>">
                    <button type="button" onclick="openAuthTab()">認証開始</button> 
                </form>            
                <button type="submit">認証開始</button>
                <button type="submit">AccessToken発行</button>
                <button type="button" onclick="window.location.href='account_list.php';">戻る</button>
            </div>
        </form>
    </div>

    <script>
        async function openAuthTab() {
            // フォーム送信後、PHPスクリプトから認証URLを取得
            const response = await fetch('generate_access_token.php', {
                method: 'POST'
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

</body>
</html>
