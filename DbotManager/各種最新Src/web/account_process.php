<?php

require __DIR__ . '/_lib/config.php';
session_start(); // セッションを開始する

// データベース接続
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

header('Content-Type: application/json');

// POSTデータを取得
$data = json_decode(file_get_contents('php://input'), true);

// 必須データを検証
if (!isset($data['command'])) {
    echo json_encode(['message' => '必要なデータがありません。']);
    exit;
}

$command = $data['command'];
$action1 = $data['action1'] ?? '';
$action2 = $data['action2'] ?? '';
$selectedIds = $data['selected_ids'] ?? [];
$form_account_id = $data['form_account_id'] ?? '';

//error_log("test");
//echo $command;
//alert($action1);

if ($command == 'refresh') {
    foreach ($selectedIds as $id) {
        $stmt = $conn->prepare("
            INSERT INTO refresh_queue (account_id, status, created_at, updated_at)
            VALUES (?, 'pending', NOW(), NOW())
        ");
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $stmt->close();
    }
    echo json_encode(['message' => 'トークン更新をキューに追加しました。']);
    exit;
}

if ($command == 'refresh_unlock') {
    foreach ($selectedIds as $id) {
        $stmt = $conn->prepare("
            INSERT INTO refresh_queue (account_id, status, created_at, updated_at)
            VALUES (?, 'pending', NOW(), NOW())
        ");
        $stmt->bind_param("i", $id);
        $stmt->execute();
        $stmt->close();

        // ② ロック解除
        $stmt2 = $conn->prepare("
            UPDATE account_master 
            SET is_locked = 0 
            WHERE id = ?
        ");
        $stmt2->bind_param("i", $id);
        $stmt2->execute();
        $stmt2->close();        
    }
    echo json_encode(['message' => 'トークン更新をキューに追加しました。']);
    exit;
}

if ($command == 'delete_frozen') {
    $stmt = $conn->prepare("
        DELETE am FROM account_master am
        INNER JOIN account_error_log ael ON ael.account_id = am.id
        WHERE ael.error_type = 'suspention'
        AND am.user_id = ?
    ");
    $stmt->bind_param("i", $_SESSION['user_id']);
    $stmt->execute();
    $count = $stmt->affected_rows;
    $stmt->close();
    echo json_encode(['message' => $count . '件の凍結アカウントを削除しました。']);
    exit;
}

if ($command == 'refresh_locked') {
    $stmt = $conn->prepare("
        INSERT INTO refresh_queue (account_id, status, created_at, updated_at)
        SELECT am.id, 'pending', NOW(), NOW()
        FROM account_master am
        INNER JOIN account_error_log ael ON ael.account_id = am.id
        WHERE ael.error_type IN ('lock', 'unauthorized', 'suspention')
        AND am.user_id = ?
    ");
    $stmt->bind_param("i", $_SESSION['user_id']);
    $stmt->execute();
    $count = $stmt->affected_rows;
    $stmt->close();
    echo json_encode(['message' => $count . '件のロック・再連携・凍結アカウントをキューに追加しました。']);
    exit;
}

if ($command == 'refresh_all_locked') {
    $stmt = $conn->prepare("
        INSERT INTO refresh_queue (account_id, status, created_at, updated_at)
        SELECT am.id, 'pending', NOW(), NOW()
        FROM account_master am
        INNER JOIN account_error_log ael ON ael.account_id = am.id
        WHERE ael.error_type IN ('lock', 'unauthorized', 'suspention')
    ");
    $stmt->execute();
    $count = $stmt->affected_rows;
    $stmt->close();
    echo json_encode(['message' => $count . '件をキューに追加しました。']);
    exit;
}

if ($command == 'get_user_summary') {
    $stmt = $conn->prepare("
    SELECT 
        um.username,
        COUNT(*) as total,
        SUM(CASE WHEN ael.error_type = 'lock' THEN 1 ELSE 0 END) as lock_count,
        SUM(CASE WHEN ael.error_type = 'suspention' THEN 1 ELSE 0 END) as suspention_count,
        SUM(CASE WHEN ael.error_type = 'unauthorized' THEN 1 ELSE 0 END) as unauthorized_count,
        SUM(CASE WHEN ael.error_type IS NULL THEN 1 ELSE 0 END) as normal_count
    FROM account_master am
    LEFT JOIN account_error_log ael ON ael.account_id = am.id
    JOIN user_master um ON um.id = am.user_id
    WHERE um.username NOT IN ('marumaru', 'next', 'r', 'rrr7', 'g','web')
    GROUP BY um.id, um.username
    ORDER BY um.username
");
    $stmt->execute();
    $result = $stmt->get_result();
    $rows = [];
    $grand_total = 0;
    $grand_normal = 0;
    $grand_lock = 0;
    $grand_suspention = 0;
    $grand_unauthorized = 0;
    while ($row = $result->fetch_assoc()) {
        $rows[] = $row;
        $grand_total += $row['total'];
        $grand_normal += $row['normal_count'];
        $grand_lock += $row['lock_count'];
        $grand_suspention += $row['suspention_count'];
        $grand_unauthorized += $row['unauthorized_count'];
    }
    $stmt->close();
    echo json_encode([
        'rows' => $rows,
        'grand_total' => $grand_total,
        'grand_normal' => $grand_normal,
        'grand_lock' => $grand_lock,
        'grand_suspention' => $grand_suspention,
        'grand_unauthorized' => $grand_unauthorized
    ]);
    exit;
}

if ($command == 'post' || $command == 'reply'|| $command == 'replytoreply')
{
//    alert($action1);

    // 処理の分岐
    if ($action1 == 'duplicate') { // 複製処理
       foreach ($selectedIds as $id) {   
            try {
                $conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);
                $message = duplicateData_comment($conn, $id, $form_account_id , $command);
                error_log("Duplicate comment successful for ID: $id");
            } catch (Exception $e) {
                error_log("Error duplicating data for ID $id: " . $e->getMessage());
                continue; // エラーが発生しても次のIDの処理を続行
            }        
        }
        echo json_encode(['message' => '複製処理を完了しました。']);
    } elseif ($action1 == 'delete') { // 削除処理
        foreach ($selectedIds as $id) {   
            try {
                $conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);
                $message = deleteData_comment($conn, $id, $command);
                error_log("Delete comment successful for ID: $id");
            } catch (Exception $e) {
                error_log("Error delete data for ID $id: " . $e->getMessage());
                continue; // エラーが発生しても次のIDの処理を続行
            }        
        }
        echo json_encode(['message' => '削除処理を完了しました。']);
    } else {
        echo json_encode(['message' => '不明なアクションです。']);
    }
}
elseif ($command == 'search')
{
    // 処理の分岐
    if ($action1 == 'duplicate') { // 複製処理
       foreach ($selectedIds as $id) {   
            try {
                $conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);
                $message = duplicateData_search($conn, $id, $form_account_id);
                error_log("Duplicate search successful for ID: $id");
            } catch (Exception $e) {
                error_log("Error duplicating data for ID $id: " . $e->getMessage());
                continue; // エラーが発生しても次のIDの処理を続行
            }        
        }
        echo json_encode(['message' => "監視,リプライ設定 複製処理を完了しました。"]);
    } elseif ($action1 == 'delete') { // 削除処理
        foreach ($selectedIds as $id) {   
            try {
                $conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);
                $message = deleteData_search($conn, $id, $form_account_id);
                error_log("Delete search successful for ID: $id");
            } catch (Exception $e) {
                error_log("Error delete data for ID $id: " . $e->getMessage());
                continue; // エラーが発生しても次のIDの処理を続行
            }        
        }
        echo json_encode(['message' => '削除処理を完了しました。']);
    } else {
        echo json_encode(['message' => '不明なアクションです。']);
    }
}
else{
    // 処理の分岐
    if ($action2 == 'on') { // 複製処理
        foreach ($selectedIds as $id) {   
             try {
                 $conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);
                 $message = updatesSearchEnable_AccountMaster($conn, $id, 1);
                 error_log("SearchEnable_AccountMaster ON search successful for ID: $id");
             } catch (Exception $e) {
                 error_log("Error SearchEnable_AccountMaster ON for ID $id: " . $e->getMessage());
                 continue; // エラーが発生しても次のIDの処理を続行
             }        
         }
         echo json_encode(['message' => '監視実施をONにしました。']);
     } elseif ($action2 == 'off') { // 削除処理
         foreach ($selectedIds as $id) {   
             try {
                 $conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);
                 $message = updatesSearchEnable_AccountMaster($conn, $id, 0);
                 error_log("Delete SearchEnable_AccountMaster OFF successful for ID: $id");
             } catch (Exception $e) {
                 error_log("Error SearchEnable_AccountMaster OFF for ID $id: " . $e->getMessage());
                 continue; // エラーが発生しても次のIDの処理を続行
             }        
         }
         echo json_encode(['message' => '監視実施をOFFにしました。']);
     } else {
         echo json_encode(['message' => '不明なアクションです。']);
     }    
}


exit;
