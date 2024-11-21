<?php


$config = [
    'servername' => 'localhost',
    'username' => 'root',
    'password' => 'abcd1234', // 実際のパスワードをここに記入
    'dbname' => 'd_bot'
];

define('MAIN_DIR',__DIR__);
define('PARTS_DIR',MAIN_DIR.'/parts');
define('CONTENTS_DIR',MAIN_DIR.'/contents');

$current_user = null;
function current_user($conn){
    global $current_user;
    $current_user = null;

    $user = get_user($conn , $_SESSION['user_id']);

    $re = false;
    if ($user != null) {
        $current_user = $user;
        $_SESSION['username'] = $user['username'];
        $_SESSION['admin'] = $user['admin'];
        $re = true;
    }

    return $re;
}

function get_user($conn,$id){
    $stmt = $conn->prepare("SELECT id,username,admin,password FROM user_master WHERE id = ?");
    $stmt->bind_param("i",$id);
    $stmt->execute();
    $stmt->store_result();
    $stmt->bind_result($user_id,$username, $admin,$password);
    $stmt->fetch();

    if ($stmt->num_rows > 0) {
        return [
            'id' => $user_id,
            'username' => $username,
            'admin' => $admin,
            'password' => $password,
        ];
    }

    $stmt->close();

    return null;
}
