<?php

require __DIR__ . '/_lib/config.php';
session_start(); // セッションを開始する

// データベース接続
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

header('Content-Type: application/json');

// POSTデータを取得
$data = json_decode(file_get_contents('php://input'), true);

// 必須データを検証
if (!isset($data['command'], $data['action1'], $data['action2'], $data['selected_ids'], $data['form_account_id'])) {
    echo json_encode(['message' => '必要なデータがありません。']);
    exit;
}

$command = $data['command'];
$action1 = $data['action1'];
$action2 = $data['action2'];
$selectedIds = $data['selected_ids'];
$form_account_id = $data['form_account_id'];

if ($command == 'comment') 
{
    // 処理の分岐
    if ($action1 == 'duplicate') { // 複製処理
       foreach ($selectedIds as $id) {   
            try {
                $conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);
                $message = duplicateData_comment($conn, $id, $form_account_id);
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
                $message = deleteData_comment($conn, $id, $form_account_id);
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
        echo json_encode(['message' => '複製処理を完了しました。']);
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
