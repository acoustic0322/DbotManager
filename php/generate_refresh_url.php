<?php

// POSTデータを受け取る
// 必要なデータの取得
$api_key = $_POST['api_key'] ?? null;
$api_key_secret = $_POST['api_key_secret'] ?? null;
$client_id = $_POST['client_id'] ?? null;
$redirect_uri = 'https://script.google.com/macros/s/AKfycbzVkmUti3NUc5T1MxSfX586zn8Iv4i1l-fMSlMb99gIl5Wlius5Sf-CkQP4zenPlpl_AQ/exec';

if (!$api_key || !$api_key_secret) {
    http_response_code(400);
//    echo 'API KeyまたはAPI Key Secretが指定されていません。';
    exit;
}


$url = "https://twitter.com/i/oauth2/authorize?response_type=code&client_id={$client_id}&redirect_uri={$redirect_uri}&scope=tweet.read%20users.read%20offline.access&state=state123&code_challenge=challenge123&code_challenge_method=plain";

echo $url
//echo 'test'
?>
