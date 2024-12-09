<?php
require __DIR__.'/_lib/config.php';
session_start(); // セッションを開始する
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    header("Location: login.php");
    exit;
}

$max_count = 6;

$type = $_GET['type']??'m';
$title = '動画';
$file_prefix = 'm';
$file_type_name = 'movie';
if ($type == 'p') {
    $title = '画像';
    $file_prefix = 'p';
    $file_type_name = 'photo';
}else{
    $type = 'm';
}

$xuser_id = $_GET['xuser']??'';
$xuser_id = filter_var($xuser_id, FILTER_VALIDATE_INT);
if ($xuser_id === false) {
    $xuser_id = '';
}
// アカウントリストを取得
$current_userid = $_SESSION['user_id'];

$stmt = $conn->prepare("SELECT * FROM account_master WHERE user_id = ?");
$stmt->bind_param("s", $current_userid);
$stmt->execute();
$result = $stmt->get_result();
$stmt->close();

$xusers = [];
$xuser = null;
while ($row = $result->fetch_assoc()){
    $xusers[] = $row;
    if ((string)$row['id'] === (string)$xuser_id) {
        $xuser = $row;
    }
}

/*
if (!isset($_SESSION['admin']) && $_SESSION['admin'] == 1){
    echo '権限が足りません';
    exit;
}
    */


// サポートされる動画フォーマットを定義
$allowed_mime_types = [
    'video/mp4',
    'video/avi',
    'video/mpeg',
    'video/webm',
    'video/x-matroska',
    'video/quicktime',
    'video/x-ms-wmv',
    'video/x-flv',
    'video/ogg',
    'video/3gpp',
    'video/3gpp2',
    'video/hevc',
    'video/x-m4v'
];
$allowed_extensions = ['mp4', 'avi', 'mpeg', 'webm', 'mkv', 'mov', 'wmv', 'flv', 'ogg', '3gp', '3g2', 'hevc', 'm4v'];
if ($type == 'p') {
    $allowed_mime_types = [
        'image/jpeg',
        'image/png',
        'image/gif',
        'image/webp',
        'image/bmp',
        'image/heic',
        'image/heif',
        'image/tiff',
        'image/vnd.radiance',
        'image/x-exr',
        'image/jp2'
    ];
    $allowed_extensions = ['jpg', 'jpeg', 'png', 'gif' , 'webp' , 'bmp' , 'heic' , 'heif' , 'tiff', 'tif', 'hdr' , 'exr' , 'jp2', 'j2k'];
}

$media_count = 0;
if ( !is_null($xuser) ) {
    $stmt = $conn->prepare("SELECT * FROM media_master WHERE user_id = ? AND account_id = ? AND media_type = ?");
    $stmt->bind_param("iis", $current_userid , $xuser['id'] , $file_type_name );
    $stmt->execute();
    $result2 = $stmt->get_result();
    $stmt->close();
    $media_count = $result2->num_rows;
}

// アップロード先ディレクトリ
$upload_dir = UPLOAD_DIR.'/';

$errors = [];
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $post_type = $_POST['type']??'';
    if ($post_type == 'file_del') {
        $media_id = $_POST['media_id']??'';

        if (empty($media_id)) {
            echo 'idを指定してください';
            exit;
        }else if (is_null($xuser)) {
            echo 'Xユーザーが存在しません';
            exit;
        }

        $upload_dir .= $xuser['id'].'/';

        // SQLを準備して実行
        $stmt = $conn->prepare("SELECT * FROM media_master WHERE media_id = ? AND user_id = ? AND account_id = ? AND media_type = ?");
        $stmt->bind_param("iiis", $media_id, $current_userid, $xuser['id'], $file_type_name);
        $stmt->execute();
        $result = $stmt->get_result();

        if ($result->num_rows > 0) {
            $row = $result->fetch_assoc();
            $file = $upload_dir . $file_prefix. $row['media_id'] . '.'.$row['ext'];
            if (file_exists($file)) {
                @unlink($file);
            }
        }

        // SQLを準備して実行
        $delete_stmt = $conn->prepare("DELETE FROM media_master WHERE media_id = ? AND user_id = ? AND account_id = ? AND media_type = ?");
        $delete_stmt->bind_param("iiis",$media_id, $current_userid , $xuser['id'] , $file_type_name );

        if ($delete_stmt->execute()) {
            /* 更新成功 */
        } else {
            /* 更新失敗 */
        }

        $stmt->close();
        $delete_stmt->close();
        $conn->close();        

        header("Location: upload.php?type=".$type.'&xuser='.$xuser['id']);
        exit;        
    }else{

        if ($media_count <  $max_count) {

            // ディレクトリが存在しない場合は作成
            if (!is_dir($upload_dir)) {
                mkdir($upload_dir, 0755, true);
            }

            // ファイルがアップロードされたか確認
            if (isset($_FILES['upload']) && $_FILES['upload']['error'] === UPLOAD_ERR_OK) {
                if (is_null($xuser)) {
                    $errors[] = 'Xユーザーが存在しません';
                }else{

                    $upload_dir .= $xuser['id'].'/';
                    // ディレクトリが存在しない場合は作成
                    if (!is_dir($upload_dir)) {
                        mkdir($upload_dir, 0755, true);
                    }

                    $file = $_FILES['upload'];

                    // ファイル情報
                    $file_name = basename($file['name']); // 元のファイル名
                    $file_tmp = $file['tmp_name'];       // 一時保存先
                    $file_size = $file['size'];          // ファイルサイズ
                    $file_error = $file['error'];        // エラーコード
                    $file_type = mime_content_type($file_tmp); // MIMEタイプを確認
                    $file_extension = pathinfo($file_name, PATHINFO_EXTENSION);
                    $file_extension = strtolower($file_extension);

                    $duration = 0;

                    // ファイルタイプをチェック
                    if (!in_array($file_extension, $allowed_extensions , true) || !in_array($file_type, $allowed_mime_types , true)) {
                        $errors[] = "サポートされていない".$title."形式です";
                    }

                    // ファイルサイズ制限 (例: 500MB)
                    $max_size = 500 * 1024 * 1024;
                    if ($file_size > $max_size) {
                        $errors[] = "ファイルサイズが大きすぎます (最大: 500MB)。";
                    }

                    if (count($errors) == 0) {
                        
                        if ($type == 'm') {
                            try {
                                // FFmpegコマンドで動画の長さを取得
                                $cmd = "ffmpeg -i " . escapeshellarg($file_tmp) . " 2>&1";
                                $output = shell_exec($cmd);

                                // 動画の長さを抽出 (例: Duration: 00:02:20.45)
                                if (preg_match('/Duration: (\d{2}):(\d{2}):(\d{2})\.\d+/', $output, $matches)) {
                                    $hours = (int)$matches[1];
                                    $minutes = (int)$matches[2];
                                    $seconds = (int)$matches[3];
                                    $duration = ($hours * 3600) + ($minutes * 60) + $seconds;

                                    // 140秒を超えている場合はエラー
                                    if ($duration > 140) {
                                        $errors[] = "動画の長さが制限を超えています (最大: 140秒)。";
                                    }
                                } else {
                                    throw new Exception("動画の長さを取得できませんでした。");
                                }
                            } catch (Exception $e) {
                                throw new Exception("動画の長さを取得できませんでした。");
                            }
                        }
                    }

                    if (count($errors)) {

                    }else{

                        // トランザクション開始
                        $conn->begin_transaction();

                        try {
                            $ext = 'mp4';
                            if ($type == 'p') {
                                $ext = $file_extension;
                                if ( !($file_extension == 'jpg' || $file_extension == 'jpeg' || $file_extension == 'png' || $file_extension == 'gif') ) {
                                    $ext = 'png';
                                }
                            }

                            // データベースに登録
                            $stmt = $conn->prepare("INSERT INTO media_master (user_id, account_id, name, register_date ,media_type , ext , duration ) VALUES (?, ?, ?, CURRENT_TIMESTAMP, ? , ? , ?)");
                            $stmt->bind_param("iisssi", $current_userid, $xuser['id'] ,$file_name,$file_type_name ,$ext , $duration);
                            $stmt->execute();

                            // 挿入IDを取得
                            $insert_id = $conn->insert_id;

                            // ステートメントを閉じる
                            $stmt->close();

                            if ($file_extension == $ext) {
                                // 保存先ファイルパス
                                $destination = $upload_dir . $file_prefix.$insert_id . '.'.$file_extension;

                                // ファイルを移動して保存
                                if (!move_uploaded_file($file_tmp, $destination)) {
                                    throw new Exception("ファイルを保存できませんでした。");
                                }
                            }else{

                                if ($type == 'p') {
                                    $converted_file = $upload_dir . $file_prefix.$insert_id . ".png";
                                    try {
                                        $imagick = new Imagick($file_tmp);
                                        $imagick->setImageFormat('png');
                                        $imagick->writeImage($converted_file);
                                        $imagick->clear();
                                        $imagick->destroy();
                                    } catch (Exception $e) {
                                        throw new Exception("ファイル変換に失敗して、ファイルを保存できませんでした。");
                                    }
                                }else{
                                    // MP4に変換
                                    $converted_file = $upload_dir . $file_prefix.$insert_id . ".mp4";
                                    $ffmpeg_cmd = "ffmpeg -i " . escapeshellarg($file_tmp) . " -c:v libx264 -preset fast -crf 23 -c:a aac " . escapeshellarg($converted_file);

                                    exec($ffmpeg_cmd, $output, $return_var);
                                    if ($return_var !== 0) {
                                        throw new Exception("ファイル変換に失敗して、ファイルを保存できませんでした。");
                                    }
                                }

                            }

                            // 問題がなければコミット
                            $conn->commit();

                        } catch (Exception $e) {
                            // エラーが発生した場合はロールバック
                            $conn->rollback();

                            // エラーメッセージを表示
                            $errors[] = "ファイルを保存できませんでした。";
                        }

                        if (count($errors)) {

                        }else{
                            $conn->close();

                            header("Location: upload.php?type=".$type.'&xuser='.$xuser['id']);
                            exit;     
                        }

                    }
                }

            } else {
                $post_max_size = return_bytes(ini_get('post_max_size'));
                $content_length = isset($_SERVER['CONTENT_LENGTH']) ? (int)$_SERVER['CONTENT_LENGTH'] : 0;

                if (isset($_FILES['upload'])) {
                    $errors[] = $title."が正常にアップロードされませんでした。エラーコード: " . $_FILES['upload']['error'];
                }else if ($content_length > $post_max_size) {
                   $errors[] = '送信されたデータが許可された最大サイズを超えています。';
                }else{
                    $errors[] = $title."が選択されていません ";
                }
            }
            
        }else{
           $errors[] = "アップロード可能数は".$max_count.'件までです。';
        }
    }
}


?><!DOCTYPE html>
<html lang="ja">
<head>
    <meta charset="UTF-8">
    <title><?php echo e( $title ) ?>アップロード</title>
    <script src="
    https://cdn.jsdelivr.net/npm/choices.js@11.0.2/public/assets/scripts/choices.min.js
    "></script>
    <link href="
    https://cdn.jsdelivr.net/npm/choices.js@11.0.2/public/assets/styles/choices.min.css
    " rel="stylesheet">

    <link rel="stylesheet" type="text/css" href="./main.css">
    <style>
        .registration-form {
            margin-top: 10px;
            margin-bottom: 20px;
        }
        .registration-form input {
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
        div#content img,
        div#content video{
            max-width: 200px;
            height: auto;
        }
    </style>
</head>
<body>

    <?php require PARTS_DIR.'/sidebar.php'; ?>

    <!-- コンテンツエリア -->
    <div class="content" id="content">
   <h2>Xアカウント選択</h2>
   <form method="GET" action="?">
      <input type="hidden" name="type" value="<?php echo e($type) ?>">
      <select id="form_xuser" name="xuser">
        <option value="">未選択</option>
        <?php foreach ($xusers as $k => $row) { ?>
            <option value="<?php echo e($row['id']) ?>" <?php echo ( (string)$row['id'] === (string)$xuser_id ? 'selected' : '' ); ?>><?php echo e($row['name']) ?></option>
        <?php } ?>
      </select>
   </form>

   <?php if ( !is_null($xuser) ) { ?>

    <?php if ($media_count <  $max_count) { ?>
    <form method="POST" enctype="multipart/form-data" class="registration-form">
    <div class="input-group">
        <label for="upload"><?php echo e($title) ?>を選択:</label>
        <input type="file" name="upload" accept="<?php echo implode(',', $allowed_mime_types) ?>" required>
    </div>
        <button type="submit">アップロード</button>
        <?php if (count($errors)) { ?>
            <div class="errors">
                <?php foreach ($errors as $k => $v) { ?>
                    <div><?php echo e($v) ?></div>
                <?php } ?>
            </div>
        <?php } ?>
    </form>
    <?php }else{ ?>
    <div>アップロード可能数は<?php echo e($max_count) ?>件までです。</div>
    <?php } ?>

    <h2>アップロード一覧</h2>

    <table>
        <thead>
            <tr>
                <th>サムネイル</th>
                <th>名前</th>
                <?php if ($type == 'm') { ?>
                <th>長さ</th>
                <?php } ?>
                <th>操作</th>
            </tr>
        </thead>
        <tbody>
            <?php while ($row = $result2->fetch_assoc()): ?>
            <tr>
                <td>
                <?php if ($row['media_type'] == 'movie') { ?>
                <a href="<?php echo e(MEDIA_URL.'/'.$row['account_id'].'/m'.$row['media_id'].'.mp4') ?>" target="_blank"><video src="<?php echo e(MEDIA_URL.'/'.$row['account_id'].'/m'.$row['media_id'].'.mp4') ?>" loading="lazy"></video></a>
                <?php }else{ ?>
                <a href="<?php echo e(MEDIA_URL.'/'.$row['account_id'].'/p'.$row['media_id'].'.'.$row['ext']) ?>" target="_blank"><img src="<?php echo e(MEDIA_URL.'/'.$row['account_id'].'/p'.$row['media_id'].'.'.$row['ext']) ?>" loading="lazy"></a>
                <?php } ?>
                </td>
                <td><?php echo e($row['name']); ?></td>
                <?php if ($type == 'm') { ?>
                <td><?php
                   $duration = $row['duration']??0;
                   $formatted_duration = sprintf('%02d:%02d:%02d', floor($duration / 3600), floor(($duration % 3600) / 60), $duration % 60);
                   echo $formatted_duration;
                 ?></td>
                <?php } ?>
                <td>
                    <form class="button_form" method="POST">
                    <input type="hidden" name="type" value="file_del">
                    <input type="hidden" name="media_id" value="<?php echo htmlspecialchars($row['media_id']) ?>">
                    <button type="button" onclick="deleteFile(this,<?php echo e($row['media_id']) ?>)">削除</button>
                    </form>
                </td>
            </tr>
            <?php endwhile; ?>
        </tbody>
    </table>
    </div>

    <?php } ?>

    <script>

    function deleteFile(button,id) {
        if (confirm( "<?php echo e($title) ?> ID " + id + " を削除します。")) {
            button.form.submit();
        }
    }

    (function(){
        document.addEventListener('DOMContentLoaded',function(){
            const xuserEl = document.getElementById('form_xuser')
            xuserEl.addEventListener('change',function(){
                xuserEl.closest('form').submit();
            });

            const choices = new Choices('#form_xuser', {
                searchEnabled: true,
                itemSelectText: '',
            });

        });
    })();
    </script>
 
</body>
</html>
