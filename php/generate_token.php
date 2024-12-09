<?php
header('Content-Type: application/json');

try {
    // POSTデータを取得
    $input = file_get_contents('php://input');
    $data = json_decode($input, true);

    if (!isset($data['account_id']) || !isset($data['mode'])) {
        throw new Exception('Invalid parameters. Required: account_id and mode.');
    }

    // パラメータを取得
    $account_id = intval($data['account_id']);
    $mode = escapeshellarg($data['mode']); // 安全性のためにエスケープ

    // Pythonスクリプトのパス
    $scriptPath = escapeshellcmd('../python/tweet.py'); // Pythonスクリプトへの相対パス
    $command = "python $scriptPath account_id=$account_id mode=$mode";

    // Pythonスクリプトを実行
    exec($command, $output, $return_var);

    if ($return_var !== 0) {
        throw new Exception("Python script execution failed. Exit code: $return_var");
    }

    // 実行結果をJSONとして返す
    $response = [
        'status' => 'success',
        'data' => $output
    ];
} catch (Exception $e) {
    // エラー時の処理
    $response = [
        'status' => 'error',
        'message' => $e->getMessage()
    ];
}

// JSONをクライアントに返す
echo json_encode($response);
