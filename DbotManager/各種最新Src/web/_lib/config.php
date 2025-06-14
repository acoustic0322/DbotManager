<?php

require __DIR__.'/twitteroauth/vendor/autoload.php';

//define('OAUTH_CALLBACK' , 'http://localhost:8000/callback.php');
define('OAUTH_CALLBACK' , 'https://d-bot.happywinds.net/d-bot/callback.php');
//define('OAUTH_CALLBACK' , 'https://d-bot.happywinds.net/callback.php');
//define('MANAGER_PATH' , 'C:\\Users\\winserverroot\\Desktop\\DbotManager\\DbotManager\\bin\\Debug\\DbotManager.exe');

define('CERT_FILE_PATH' , 'C:/pem/d-bot.pem');


define('MANAGER_PATH' , 'C:\\DbotManager\\DbotManager.exe');
define('WORK_FOLDER' , 'C:\\DbotManager');
//define('MANAGER_PATH' , 'Debug\\DbotManager.exe');
//define('WORK_FOLDER' , 'Debug');

define('MAIN_DIR',__DIR__);
define('PARTS_DIR',MAIN_DIR.'/parts');
define('CONTENTS_DIR',MAIN_DIR.'/contents');

define('UPLOAD_DIR',__DIR__.'/../upload');
//define('MEDIA_URL', __DIR__.'/../upload');
//define('MEDIA_URL', '/upload');

//define('MEDIA_URL', '/upload');
define('MEDIA_URL', '/d-bot/upload');
define('DB_HOST', '203.137.53.205');


define('MAX_MOVIE_COUNT', 200);
define('MAX_PHOTO_COUNT', 200);

$config = [
    'servername' => DB_HOST,
    'username' => 'root',
    'password' => 'abcd1234', // 実際のパスワードをここに記入
    'dbname' => 'd_bot'
];

function return_bytes($val) {
    $val = trim($val);
    $last = strtolower(substr($val, -1));
    $val = (int)$val;
    switch($last) {
        case 'g':
            $val *= 1024;
        case 'm':
            $val *= 1024;
        case 'k':
            $val *= 1024;
    }
    return $val;
}

$current_user = null;
function current_user($conn){
    global $current_user;
    $current_user = null;

    // is_logged_in未定義(ログイン処理が行われていない)場合はゲストモード起動
    if (!isset($_SESSION['is_logged_in'])) {
        $_SESSION['user_id'] = '0';
        $_SESSION['username'] = 'guest';
        $_SESSION['admin'] = '0';
        $_SESSION['enable'] = '0';
        $_SESSION['memo'] = '';
        $_SESSION['like_enable'] = '0';
        $_SESSION['bookmark_enable'] = '0';
        $_SESSION['reply_enable'] = '0';
        $_SESSION['repost_enable'] = '0';
        $_SESSION['sensyuken_mode'] = '0';
        $_SESSION['japanese_mode'] = '1';
        $_SESSION['post_enable'] = '0';
        $_SESSION['reserve_enable'] = '0';
        $_SESSION['media_enable'] = '0';
        $_SESSION['check_enable'] = '0';
        $_SESSION['api_master_id'] = '0';
        $_SESSION['searchrep_enable'] = '0';
        $_SESSION['GROQ_API_KEY'] = '';
        $_SESSION['OPENAI_API_KEY'] = '';
        $_SESSION['ai_enable'] = '0';
        $_SESSION['follow_enable'] = '0';
        $_SESSION['sensyuken_like_limit'] = 0;
        $_SESSION['sensyuken_bookmark_limit'] = 0;
        
        $_SESSION['is_guest'] = true;
        $_SESSION['is_logged_in'] = false;
        
        return true;
    }

    $user = get_user($conn , $_SESSION['user_id']);

    $re = false;
    if ($user != null) {
        $current_user = $user;
        $_SESSION['username'] = $user['username'];
        $_SESSION['admin'] = $user['admin'];
        $_SESSION['enable'] = $user['enable'];
        $_SESSION['memo'] = $user['memo'];
        $_SESSION['like_enable'] = $user['like_enable'];
        $_SESSION['bookmark_enable'] = $user['bookmark_enable'];
        $_SESSION['reply_enable'] = $user['reply_enable'];
        $_SESSION['repost_enable'] = $user['repost_enable'];
        $_SESSION['sensyuken_mode'] = $user['sensyuken_mode'];
        $_SESSION['japanese_mode'] = $user['japanese_mode'];
        $_SESSION['post_enable'] = $user['post_enable'];
        $_SESSION['reserve_enable'] = $user['reserve_enable'];
        $_SESSION['media_enable'] = $user['media_enable'];
        $_SESSION['check_enable'] = $user['check_enable'];
        $_SESSION['api_master_id'] = $user['api_master_id'];
        $_SESSION['searchrep_enable'] = $user['searchrep_enable'];
        $_SESSION['GROQ_API_KEY'] = $user['GROQ_API_KEY'];
        $_SESSION['OPENAI_API_KEY'] = $user['OPENAI_API_KEY'];
        $_SESSION['ai_enable'] = $user['ai_enable'];
        $_SESSION['follow_enable'] = $user['follow_enable'];
        $_SESSION['sensyuken_like_limit'] = $user['sensyuken_like_limit'];
        $_SESSION['sensyuken_bookmark_limit'] = $user['sensyuken_bookmark_limit'];


        $re = true;
    }

    return $re;
}

function get_user($conn,$id){
    $re = null;

    $stmt = $conn->prepare(
        "SELECT 
        id,
        username,
        admin,
        password,
        enable,
        memo,
        like_enable,
        bookmark_enable,
        reply_enable,
        repost_enable,
        sensyuken_mode,
        japanese_mode,
        post_enable,
        reserve_enable,
        media_enable,
        check_enable,
        api_master_id,
        searchrep_enable,
        GROQ_API_KEY,
        OPENAI_API_KEY,
        ai_enable,
        follow_enable
        ,sensyuken_like_limit
        ,sensyuken_bookmark_limit
     FROM user_master WHERE id = ?"
     );

    if ($stmt) {
        $stmt->bind_param("i",$id);
        $stmt->execute();
        $stmt->store_result();
        $stmt->bind_result(
            $user_id,
            $username, 
            $admin,
            $password,
            $enable,
            $memo,
            $like_enable,
            $bookmark_enable,
            $reply_enable,
            $repost_enable,
            $sensyuken_mode,
            $japanese_mode,
            $post_enable,
            $reserve_enable,
            $media_enable,
            $check_enable,
            $api_master_id,
            $seachrep_enable,
            $GROQ_API_KEY,
            $OPENAI_API_KEY,
            $ai_enable,
            $follow_enable
            ,$sensyuken_like_limit
            ,$sensyuken_bookmark_limit
        );
        $stmt->fetch();

        if ($stmt->num_rows > 0) {
            $re = [
                'id' => $user_id,
                'username' => $username,
                'admin' => $admin,
                'password' => $password,
                'enable' => $enable,
                'memo' => $memo,
                'like_enable' => $like_enable,
                'bookmark_enable' => $bookmark_enable,
                'reply_enable' => $reply_enable,
                'repost_enable' => $repost_enable,
                'sensyuken_mode' => $sensyuken_mode,
                'japanese_mode' => $japanese_mode,
                'post_enable' => $post_enable,
                'reserve_enable' => $reserve_enable,
                'media_enable' => $media_enable,
                'check_enable' => $check_enable,
                'api_master_id' => $api_master_id,
                'searchrep_enable' => $seachrep_enable,
                'GROQ_API_KEY' => $GROQ_API_KEY,
                'OPENAI_API_KEY' => $OPENAI_API_KEY,
                'ai_enable' => $ai_enable ,
                'follow_enable' => $follow_enable ,
                'sensyuken_like_limit' => $sensyuken_like_limit ,
                'sensyuken_bookmark_limit' => $sensyuken_bookmark_limit ,
                ];
        }

        $stmt->close();
    }

    return $re;
}


function get_account($conn, $id)
{
    $re = null;

    $query = "
    SELECT 
        am.id,
        am.user_id,
        am.name,
        am.login_id,
        am.login_password,
        case when am.api_master_id != 0 then api.client_id else am.client_id end as client_id,
        case when am.api_master_id != 0 then api.client_secret else am.client_secret end as client_secret,
        am.api_key,
        am.api_key_secret,
        am.access_token,
        am.access_token_secret,
        am.bearer_token,
        am.refresh_token,
        am.enable,
        am.like_enable,
        am.reply_enable,
        am.bookmark_enable,
        am.repost_enable , 
        am.post_enable,
        am.paid,
        am.paid_like ,
        am.paid_bookmark ,
        am.reserve1_enable,
        am.reserve1_start_hour,
        am.reserve1_end_hour,
        am.reserve1_count,
        am.reserve2_enable,
        am.reserve2_start_hour,
        am.reserve2_end_hour,
        am.reserve2_count,
        am.reserve3_enable,
        am.reserve3_start_hour,
        am.reserve3_end_hour,
        am.reserve3_count,
        am.reserve4_enable,
        am.reserve4_start_hour,
        am.reserve4_end_hour,
        am.reserve4_count ,
        am.dmm_id ,
        am.search_enable ,
        am.proxy_enable ,
        am.proxy_url ,
        am.check_interval ,
        am.api_master_id ,
        am.use_admin_api ,
        am.reserve1_ai , 
        am.reserve2_ai , 
        am.reserve3_ai , 
        am.reserve4_ai , 
        am.ai_post_enable  ,
        am.ai_reply_enable  ,
        am.ai_post_prompt  ,
        am.ai_reply_prompt ,
        am.ai_trend_prompt  ,
        am.ai_post_example  ,
        am.ai_reply_example ,
        am.ai_mode 
    FROM account_master am
    LEFT JOIN api_master api ON api.id = am.api_master_id
    WHERE am.id = ?;
    ";

    $stmt = $conn->prepare($query);
    if ($stmt) {
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $stmt->store_result();


        // 結果をバインド
        $stmt->bind_result(
            $id,
            $user_id,
            $name,
            $login_id,
            $login_password,
            $client_id,
            $client_secret,
            $api_key,
            $api_key_secret,
            $access_token,
            $access_token_secret,
            $bearer_token,
            $refresh_token,
            $enable,
            $like_enable,
            $reply_enable,
            $bookmark_enable,
            $repost_enable,
            $post_enable,
            $paid,
            $paid_like,
            $paid_bookmark,
            $reserve1_enable,
            $reserve1_start_hour,
            $reserve1_end_hour,
            $reserve1_count,
            $reserve2_enable,
            $reserve2_start_hour,
            $reserve2_end_hour,
            $reserve2_count,
            $reserve3_enable,
            $reserve3_start_hour,
            $reserve3_end_hour,
            $reserve3_count,
            $reserve4_enable,
            $reserve4_start_hour,
            $reserve4_end_hour,
            $reserve4_count,
            $dmm_id,
            $search_enable,
            $proxy_enable,
            $proxy_url ,
            $check_interval,
            $api_master_id,
            $use_admin_api ,
            $reserve1_ai,
            $reserve2_ai,
            $reserve3_ai,
            $reserve4_ai,
            $ai_post_enable  ,
            $ai_reply_enable  ,
            $ai_post_prompt  ,
            $ai_reply_prompt ,
            $ai_trend_prompt ,
            $ai_post_example  ,
            $ai_reply_example ,
            $ai_mode     
        );

        if ($stmt->fetch()) {
            // データが取得できた場合
            $re = [
                'id' => $id,
                'user_id' => $user_id,
                'name' => $name,
                'login_id' => $login_id,
                'login_password' => $login_password,
                'client_id' => $client_id,
                'client_secret' => $client_secret,
                'api_key' => $api_key,
                'api_key_secret' => $api_key_secret,
                'access_token' => $access_token,
                'access_token_secret' => $access_token_secret,
                'bearer_token' => $bearer_token,
                'refresh_token' => $refresh_token,
                'enable' => $enable,
                'like_enable' => $like_enable,
                'bookmark_enable' => $bookmark_enable,
                'reply_enable' => $reply_enable,
                'repost_enable' => $repost_enable,
                'post_enable' => $post_enable,
                'paid' => $paid,
                'paid_like' => $paid_like,
                'paid_bookmark' => $paid_bookmark,
                'reserve1_enable' => $reserve1_enable,
                'reserve1_start_hour' => $reserve1_start_hour,
                'reserve1_end_hour' => $reserve1_end_hour,
                'reserve1_count' => $reserve1_count,
                'reserve2_enable' => $reserve2_enable,
                'reserve2_start_hour' => $reserve2_start_hour,
                'reserve2_end_hour' => $reserve2_end_hour,
                'reserve2_count' => $reserve2_count,
                'reserve3_enable' => $reserve3_enable,
                'reserve3_start_hour' => $reserve3_start_hour,
                'reserve3_end_hour' => $reserve3_end_hour,
                'reserve3_count' => $reserve3_count,
                'reserve4_enable' => $reserve4_enable,
                'reserve4_start_hour' => $reserve4_start_hour,
                'reserve4_end_hour' => $reserve4_end_hour,
                'reserve4_count' => $reserve4_count,
                'dmm_id' => $dmm_id,
                'search_enable' => $search_enable,
                'proxy_enable' => $proxy_enable,
                'proxy_url' => $proxy_url,
                'check_interval' => $check_interval,
                'api_master_id' => $api_master_id,
                'use_admin_api' => $use_admin_api,
                'reserve1_ai' => $reserve1_ai,
                'reserve2_ai' => $reserve2_ai,
                'reserve3_ai' =>$reserve3_ai,
                'reserve4_ai' =>$reserve4_ai,
                'ai_post_enable' => $ai_post_enable,
                'ai_reply_enable' => $ai_reply_enable,
                'ai_post_prompt' => $ai_post_prompt,
                'ai_reply_prompt' => $ai_reply_prompt ,
                'ai_trend_prompt' => $ai_trend_prompt ,
                'ai_post_example' => $ai_post_example,
                'ai_reply_example' => $ai_reply_example ,
                'ai_mode' => $ai_mode 
            ];
        }
    }



    $stmt->close();
    return $re; // データがない場合はnullを返す
}

function get_comment($conn, $id)
{
    $re = null;

    $query = "
    SELECT 
        id,
        user_id,
        account_id,
        comment,
        enable,
        chatgpt,
        mode,
        movie_enable,
        photo_enable,
        reserve_mode
    FROM comment_master
    WHERE id = ?;
    ";

    $stmt = $conn->prepare($query);
    if ($stmt) {
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $stmt->store_result();


        // 結果をバインド
        $stmt->bind_result(
            $id,
            $user_id,
            $account_id,
            $comment,
            $enable,
            $chatgpt,
            $mode,
            $movie_enable,
            $photo_enable,
            $reserve_mode
        );

        if ($stmt->fetch()) {
            // データが取得できた場合
            $re = [
                'id' => $id,
                'use_id' => $user_id,
                'account_id' => $account_id,
                'comment' => $comment,
                'enable' => $enable,
                'chatgpt' => $chatgpt,
                'mode' => $mode,
                'movie_enable' => $movie_enable,
                'photo_enable' => $photo_enable,
                'reserve_mode' => $reserve_mode
            ];
        }
    }



    $stmt->close();
    return $re; // データがない場合はnullを返す
}

function get_check_account($conn, $id)
{
    $re = null;

    $query = "
    SELECT 
        id,
        account_id,
        enable,
        mode,
        target_account_name
    FROM check_account_list
    WHERE id = ?;
    ";

    $stmt = $conn->prepare($query);
    if ($stmt) {
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $stmt->store_result();


        // 結果をバインド
        $stmt->bind_result(
            $id,
            $account_id,
            $enable,
            $mode,
            $check_account
            );

        if ($stmt->fetch()) {
            // データが取得できた場合
            $re = [
                'id' => $id,
                'account_id' => $account_id,
                'enable' => $enable,
                'mode' => $mode,
                'target_account_name' => $check_account
            ];
        }
    }
    $stmt->close();
    return $re; // データがない場合はnullを返す
}

function get_search_list_row($conn, $id)
{
    $re = null;

    $query = "
    SELECT 
        search_user_name, 
        enable, 
        post_enable , 
        reply_enable , 
        monomane_enable, 
        post_account_id , 
        reply_account_id , 
        monomane_account_id ,
        time_enable ,
        start_hour , 
        end_hour
    FROM search_list
    WHERE id = ?;
    ";

    $stmt = $conn->prepare($query);
    if ($stmt) {
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $stmt->store_result();


        // 結果をバインド
        $stmt->bind_result(
            $search_user_name, $enable, 
            $post_enable, $reply_enable, $monomane_enable,
            $post_account_id, $reply_account_id, $monomane_account_id ,
            $time_enable , $start_hour , $end_hour
            );

        if ($stmt->fetch()) {
            // データが取得できた場合
            $re = [
                'id' => $id,
                'search_user_name' => $search_user_name,
                'enable' => $enable,
                'post_enable' => $post_enable ,
                'reply_enable' => $reply_enable ,
                'monomane_enable' => $monomane_enable, 
                'post_account_id' => $post_account_id , 
                'reply_account_id' => $reply_account_id , 
                'monomane_account_id'  => $monomane_account_id ,
                'time_enable'  => $time_enable ,
                'start_hour'  => $start_hour ,
                'end_hour'  => $end_hour 
            ];
        }
    }
    $stmt->close();
    return $re; // データがない場合はnullを返す
}



function e($value, $doubleEncode = false){
    if (is_null($value)) {return '';}
    return htmlspecialchars($value, ENT_QUOTES, 'UTF-8', $doubleEncode);
}



function duplicateData_comment($conn, $accountId, $formAccountId , $mode) {
    // 取得するデータ
    $query = "
    SELECT 
        user_id, 
        comment, 
        enable, 
        chatgpt, 
        mode, 
        movie_enable, 
        photo_enable, 
        reserve_mode  
    FROM comment_master
    WHERE account_id = ?
    AND mode = ?
    ";

    $stmt = $conn->prepare($query);
    if (!$stmt) {
        return ['success' => false, 'message' => "クエリ準備失敗: " . $conn->error];
    }

    $stmt->bind_param("is", $formAccountId , $mode);
    $stmt->execute();

    $result = $stmt->get_result();
    if ($result->num_rows === 0) {
        $stmt->close();
        $conn->close();
        return ['success' => false, 'message' => "ID $formAccountId に該当するデータが見つかりません。"];
    }

    // 全レコードを取得
    $rows = $result->fetch_all(MYSQLI_ASSOC);
    $stmt->close();

    // 挿入処理
    $query = "
    INSERT INTO comment_master (
        user_id, 
        account_id, 
        comment, 
        enable, 
        chatgpt, 
        mode, 
        movie_enable, 
        photo_enable, 
        reserve_mode
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";

    $stmt = $conn->prepare($query);
    if (!$stmt) {
        return ['success' => false, 'message' => "挿入クエリ準備失敗: " . $conn->error];
    }

    // 挿入結果をまとめる
    $successCount = 0;
    $errors = [];

    foreach ($rows as $row) {
        $stmt->bind_param(
            "sssssssss",
            $row['user_id'], 
            $accountId, // 新しい account_id を使用
            $row['comment'], 
            $row['enable'], 
            $row['chatgpt'], 
            $row['mode'], 
            $row['movie_enable'], 
            $row['photo_enable'], 
            $row['reserve_mode']
        );

        if ($stmt->execute()) {
            $successCount++;
        } else {
            $errors[] = "挿入失敗 (ユーザーID: {$row['user_id']}): " . $stmt->error;
        }
    }

    $stmt->close();
    $conn->close();

    return [
        'success' => true,
        'message' => "$successCount 件のレコードを複製しました。",
        'errors' => $errors
    ];
}


function duplicateData_search($conn, $accountId, $formAccountId) {
    // 取得するデータ
    $query = "
    SELECT 
        id,
        search_user_name,
        search_user_id,
        enable,
        post_account_id,
        post_enable,
        reply_account_id,
        reply_enable,
        monomane_account_id,
        monomane_enable
    FROM search_list
    WHERE post_account_id = ?;
    ";

    $stmt = $conn->prepare($query);
    if (!$stmt) {
        return ['success' => false, 'message' => "クエリ準備失敗: " . $conn->error];
    }

    $stmt->bind_param("i", $formAccountId);
    $stmt->execute();

    $result = $stmt->get_result();
    if ($result->num_rows === 0) {
        $stmt->close();
        $conn->close();
        return ['success' => false, 'message' => "ID $formAccountId に該当するデータが見つかりません。"];
    }

    // 全レコードを取得
    $rows = $result->fetch_all(MYSQLI_ASSOC);
    $stmt->close();

    // 挿入処理
    $query = "
    INSERT INTO search_list (
        search_user_name,
        search_user_id,
        enable,
        post_account_id,
        post_enable,
        reply_account_id,
        reply_enable,
        monomane_account_id,
        monomane_enable
    )
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)";

    $stmt = $conn->prepare($query);
    if (!$stmt) {
        return ['success' => false, 'message' => "挿入クエリ準備失敗: " . $conn->error];
    }

    // 挿入結果をまとめる
    $successCount = 0;
    $errors = [];

    foreach ($rows as $row) {
        $stmt->bind_param(
//            "ssssssssss",
            "ssiiiiiii",
            $row['search_user_name'],
            $row['search_user_id'],
//            $row['search_account_id'],
//            $accountId,
            $row['enable'],
            $accountId,
            $row['post_enable'],
            $accountId,
            $row['reply_enable'],
            $accountId,
            $row['monomane_enable']
        );

        if ($stmt->execute()) {
            $successCount++;
        } else {
            $errors[] = "挿入失敗 (ユーザーID: {$row['id']}): " . $stmt->error;
        }
    }

    $stmt->close();
    $conn->close();

    return [
        'success' => true,
        'message' => "$successCount 件のレコードを複製しました。",
        'errors' => $errors
    ];
}

function deleteData_comment($conn, $accountId , $mode) {
    // 取得するデータ
    $query = "
    DELETE FROM comment_master
    WHERE account_id = ?
    AND mode = ?;
    ";


    $stmt = $conn->prepare($query);
    if (!$stmt) {
        return ['success' => false, 'message' => "クエリ準備失敗: " . $conn->error];
    }

    $stmt->bind_param("is", $accountId , $mode);    
    $stmt->execute();
    $stmt->close();
    $conn->close();

    return [
        'success' => true,
        'message' => "レコードを削除しました。",
        'errors' => ''
    ];
}


function deleteData_search($conn, $accountId) {
    // 取得するデータ
    $query = "
    DELETE FROM search_list
    WHERE post_account_id = ?;
    ";

    $stmt = $conn->prepare($query);
    if (!$stmt) {
        return ['success' => false, 'message' => "クエリ準備失敗: " . $conn->error];
    }

    $stmt->bind_param("i", $accountId);
    $stmt->execute();
    $stmt->close();
    $conn->close();

    return [
        'success' => true,
        'message' => "レコードを削除しました。",
        'errors' => ''
    ];
}

function updatesSearchEnable_AccountMaster($conn, $accountId , $value) {
    // 取得するデータ
    $query = "
    UPDATE account_master 
    SET search_enable = ?
    WHERE id = ?;
    ";

    $stmt = $conn->prepare($query);
    if (!$stmt) {
        return ['success' => false, 'message' => "クエリ準備失敗: " . $conn->error];
    }

    $stmt->bind_param("ii", $value, $accountId);
    $stmt->execute();
    $stmt->close();
    $conn->close();

    return [
        'success' => true,
        'message' => "監視実施設定を更新しました",
        'errors' => ''
    ];
}
