<?php
require __DIR__.'/_lib/config.php';
session_start(); // セッションを開始する
$conn = new mysqli($config['servername'], $config['username'], $config['password'], $config['dbname']);

if (!current_user($conn)) {
    header("Location: login.php");
    exit;
}

/*
if (!isset($_SESSION['admin']) && $_SESSION['admin'] == 1){
    echo '権限が足りません';
    exit;
}
    */

$xuser_id = $_GET['xuser']??'';
$xuser_id = filter_var($xuser_id, FILTER_VALIDATE_INT);
if ($xuser_id === false) {
    $xuser_id = '';
}

// アカウントリストを取得
$current_userid = $_SESSION['user_id'];
$api_master_id = isset($_SESSION['api_master_id']) ? $_SESSION['api_master_id'] : null;

// アカウントコンボボックスのレコード取得
//$stmt = $conn->prepare("SELECT * FROM account_master WHERE user_id = ?");
$stmt = $conn->prepare("
SELECT 
am.name as name
, am.login_id as login_id
, am.bearer_token as bearer_token
, am.refresh_token as refresh_token
, am.access_token as access_token
, am.id as id
, am.search_enable as search_enable
FROM account_master am WHERE am.user_id = ?");

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

if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $type = $_POST['type']??'';
    if ($type == 'account_del') {
        $id = $_POST['id'];

        if (empty($id)) {
            echo "<script>alert('IDが指定されていません');</script>";
            header("Location: account_list.php");
            exit;
        }else if ((string)$id === (string)$_SESSION['user_id']) {
            echo '現在のユーザーは削除できません';
            exit;
        }

        // SQLを準備して実行
        $stmt = $conn->prepare("DELETE FROM account_master WHERE id = ?");
        $stmt->bind_param("i", $id);

        if ($stmt->execute()) {
            /* 更新成功 */
        } else {
            /* 更新失敗 */
        }

        $stmt->close();
        $conn->close();

        // 登録後にリダイレクト
        header("Location: account_list.php");
        exit;        
    }
}



//$stmt = $conn->prepare("SELECT * FROM account_master WHERE user_id = ?");
$stmt = $conn->prepare("
SELECT 
am.name as name
, am.id as id
, am.login_id as login_id
, am.bearer_token as bearer_token
, am.refresh_token as refresh_token
, am.access_token as access_token
, am.id as id
, am.search_enable as search_enable
, am.use_admin_api as use_admin_api
, am.ai_mode as ai_mode
FROM account_master am WHERE am.user_id = ?");
$stmt->bind_param("s", $current_userid);
$stmt->execute();
$result = $stmt->get_result();
?>


<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Xアカウント一覧</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./css/admin-dashboard.css" />
</head>
<body>
    <div class="layout">
  <?php require PARTS_DIR.'/sidebar.php'; ?>


   <!-- コンテンツエリア -->
   <div class="content" id="content">

    <h2>Xアカウント一覧</h2>
    <form method="GET" style="margin-bottom: 20px;">
        <input type="text" name="search" placeholder="ユーザー名で絞り込み" value="<?php echo isset($_GET['search']) ? htmlspecialchars($_GET['search']) : ''; ?>">
        <button type="submit">検索</button>
    </form>

    <div style="display: flex; align-items: center; gap: 10px;">
    <span>チェックONのアカウントに対し</span>

    <form method="GET" action="?" style="margin: 0; display: inline-block;">
       
        <select id="command_option" name="command" onchange="toggleCommandSource()">
            <option value="post">ﾎﾟｽﾄｺﾒﾝﾄ</option>
            <option value="reply">ﾘﾌﾟﾗｲｺﾒﾝﾄ</option>
            <option value="replytoreply">ﾘﾌﾟtoﾘﾌﾟｺﾒﾝﾄ</option>

            <?php if (isset($_SESSION['check_enable']) && $_SESSION['check_enable'] == 1): ?>
            <option value="search">監視リプ,モノマネ</option>

            <!-- 貸出アカウントへの一括切り替えができてしまうため保留 -->
<!--            <option value="searchFrom">監視実施</option>  -->

            <?php endif; ?>
            
        </select>
    </form>

    <span>を</span>

    <div id="action1_source" style="margin-left: 10px;">
    <form method="GET" action="?" style="margin: 0; display: inline-block;">
    <select id="action1_option" name="action1" onchange="toggleDuplicateSource()">
        <option value="duplicate">複製する</option>
        <option value="delete">削除する</option>
    </select>
    </div>

    <div id="action2_source" style="display: none; margin-left: 10px;">
    <form method="GET" action="?" style="margin: 0; display: inline-block;">
    <select id="action2_option" name="action2" >
        <option value="on">ONにする</option>
        <option value="off">OFFにする</option>
    </select>
    </div>

</form>

    <div id="duplicate_source" style="display: none; margin-left: 10px; display: inline-flex; align-items: center; gap: 12px; white-space: nowrap;">
    <span>(複製元：</span>
    <select id="form_account_id" name="xuser" style="min-width: 120px;">
        <option value="">未選択</option>
        <?php foreach ($xusers as $k => $row) { ?>
            <option value="<?php echo e($row['id']) ?>" 
            	<?php echo ( (string)$row['id'] === (string)$xuser_id ? 'selected' : '' ); ?>>
            	<?php echo e($row['name']) ?>
            </option>
        <?php } ?>
    </select>
    <span>)</span>
    </div>

    <!-- 実行ボタン -->
    <button type="submit" onclick="executeAction()" style="margin-left: 10px;">実行</button>

    <script>
    function toggleDuplicateSource() {
        const actionOption = document.getElementById('action1_option');
        const duplicateSource = document.getElementById('duplicate_source');
        if (actionOption.value === "duplicate") {
            // 複製するが選択された場合
            duplicateSource.style.display = "inline-flex";
        } else {
            // その他の場合
            duplicateSource.style.display = "none";
        }
    }

    function toggleCommandSource() {
        const commandOption = document.getElementById('command_option');
        const action1Source = document.getElementById('action1_source');
        const action2Source = document.getElementById('action2_source');
        if (commandOption.value === "searchFrom") {
            // 監視実施が選択された場合
            action1Source.style.display = "none";
            action2Source.style.display = "inline-block";
        } else {
            // その他の場合
            action1Source.style.display = "inline-block";
            action2Source.style.display = "none";
        }

        toggleDuplicateSource();
    }
    function executeAction() {
        // フォームの要素を取得
        const command = document.getElementById('command_option').value;
        const action1 = document.getElementById('action1_option').value;
        const action2 = document.getElementById('action2_option').value;
        const form_account_id = document.getElementById('form_account_id').value;

        // チェックされたIDを取得
        const selectedIds = Array.from(document.querySelectorAll('input[name="selected_ids[]"]:checked'))
            .map(checkbox => checkbox.value);

    // 監視実施モードのチェック
    if (command === "searchFrom") {
        const hasInvalidId = selectedIds.some(id => {
            alert("エラー: 1");
            const option = document.querySelector(`#form_account_id option[value="${id}"]`);
            alert("エラー: 2");
            return option && option.dataset.useAdminApi !== "0"; // use_admin_api が 0 じゃないものがあるか
        });

        if (hasInvalidId) {
            alert(hasInvalidId)
            alert('エラー: 監視実施モードは、use_admin_api=0 のアカウントのみ実行できます。');
            return;
        }
//        alert("エラー: 監視実施モードは選択できません。");
  //      return;
    }

    if (selectedIds.length === 0) {
        alert("チェックされたアカウントがありません。");
        return;
    }

//        alert(command);
//        alert(action1);
//        alert(action2);
//        alert(selectedIds);
//        alert(form_account_id);

        // 必要なデータを送信
        fetch('account_process.php', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                command: command,
                action1: action1,
                action2: action2,
                selected_ids: selectedIds,
                form_account_id : form_account_id,
            }),
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message); // サーバーからのメッセージを表示
            window.location.reload(); // ページをリロード
        })
        .catch(error => {
            console.error('エラー:', error);
        });
    }

    // ページロード時に初期状態をチェック
    document.addEventListener('DOMContentLoaded', toggleDuplicateSource);
    </script>

<script>

document.addEventListener("DOMContentLoaded", function () {
    toggleUseAdminApi();
});

function toggleUseAdminApi() {


    const searchOptions = document.getElementById('search-options');
    const processOptions = document.getElementById('process-options');
    const selectedMode = document.querySelector('input[name="new_use_admin_api"]:checked').value;

    if (selectedMode === "search") {
        searchOptions.style.display = "block";
        processOptions.style.display = "none";
    } else {
        searchOptions.style.display = "none";
        processOptions.style.display = "block";
    }

//    if (isset($_SESSION['api_master_id']) && $_SESSION['api_master_id'] === 0)

    // PHPから取得したセッション変数をJavaScriptに渡す
    const apiMasterId = <?php echo json_encode($api_master_id); ?>;
    if (apiMasterId === 0)
    {
//        searchOptions.style.display = "block";
//        processOptions.style.display = "block";
    }

}

function toggleMenu(menuEl) {
  // 他のメニューを閉じる
  document.querySelectorAll('.dropdown-menu').forEach(el => {
    if (el !== menuEl) {
      el.classList.remove('show');
      el.classList.remove('show-above');
    }
  });

  // 表示トグル
  const isVisible = menuEl.classList.contains('show');
  if (isVisible) {
    menuEl.classList.remove('show');
    menuEl.classList.remove('show-above');
    return;
  }

  // 一時表示して高さを計測
  menuEl.classList.add('show');
  const rect = menuEl.getBoundingClientRect();
  const spaceBelow = window.innerHeight - rect.bottom;
  const spaceAbove = rect.top;

  if (spaceBelow < rect.height && spaceAbove > rect.height) {
    menuEl.classList.add('show-above');
  } else {
    menuEl.classList.remove('show-above');
  }
}


</script>

</div>

<!--
    <form method="GET" action="?">
        <span>チェックONのアカウントに対し</span>

        <form method="GET" action="?">
        <select id="command_option" name="command">
          <option value="1">コメント設定</option>
          <option value="2">監視設定</option>
        </select>
        </form>


        <span>を</span>

        <form method="GET" action="?">
        <select id="action_option" name="action">
          <option value="1">複製する</option>
          <option value="2">削除する</option>
        </select>
        </form>

      <span>(複製元：</span>
      <select id="form_xuser" name="xuser">
        <option value="">未選択</option>
        <?php foreach ($xusers as $k => $row) { ?>
            <option value="<?php echo e($row['id']) ?>" <?php echo ( (string)$row['id'] === (string)$xuser_id ? 'selected' : '' ); ?>><?php echo e($row['name']) ?></option>
        <?php } ?>
      </select>
      <span>)</span>
   </form>
        -->

<div style="margin-top: 20px; font-size: 14px; color: #fff;">
  <strong>アイコン凡例：</strong>
  ✅=通常認証 / 🎞️=メディア認証 / 🔍=監視 / 🏷️=API貸出 / 🤖=AI（自由） / 👩=AI（裏垢） / 📈=AI（トレンド）
</div>
    <table>
<thead>
  <tr>
    <th class="checkbox-col"><input type="checkbox" id="select_all" onclick="toggleSelectAll()"></th>
    <th class="id-col"></th>
    <th class="name-col">アカウント</th>
    <th>ステータス</th>
    <th>操作</th>
  </tr>
</thead>
<tbody>
  <?php while ($row = $result->fetch_assoc()): ?>
  <tr>
    <td class="checkbox-col"><input type="checkbox" name="selected_ids[]" value="<?php echo htmlspecialchars($row['id']); ?>"></td>
    <td class="id-col">
      <img src="img/profile/<?php echo htmlspecialchars($row['id']); ?>.jpg"
         alt="icon"
         onerror="this.onerror=null;this.src='img/profile/noimage/noimage.jpg';"
         style="width: 42px; height: 42px; border-radius: 50%; object-fit: cover; border: 1px solid #ccc;">
    </td>  
    <td class="name-col">
      <div>
        <div>
          <?php echo htmlspecialchars($row['name']); ?> 
          <span style="color: #888; font-size: 12px;">[ID=<?php echo htmlspecialchars($row['id']); ?>]</span>
        </div>
        <div style="font-size: 12px; font-style: italic;">
          <a href="https://x.com/<?php echo urlencode($row['login_id']); ?>"
             target="_blank"
             style="color: #d4af37; text-decoration: none;"
             onmouseover="this.style.textDecoration='underline'"
             onmouseout="this.style.textDecoration='none'">
            @<?php echo htmlspecialchars($row['login_id']); ?>
          </a>
        </div>
      </div>
    </td>
<td>
  <?php if (!empty($row['bearer_token']) && !empty($row['refresh_token'])): ?>
    <span title="通常認証済み">✅</span>
  <?php endif; ?>
  <?php if (!empty($row['access_token'])): ?>
    <span title="メディア認証済み">🎞️</span>
  <?php endif; ?>
  <?php if (!empty($row['search_enable'])): ?>
    <span title="監視実施">🔍</span>
  <?php endif; ?>
  <?php if (isset($row['use_admin_api']) && $row['use_admin_api'] == 1): ?>
    <span title="貸出アカウント">🏷️</span>
  <?php endif; ?>
  <?php
    switch ($row['ai_mode'] ?? 0) {
      case 1: echo '<span title="AIモード：自由">🤖</span>'; break;
      case 2: echo '<span title="AIモード：裏垢女子">👩</span>'; break;
      case 3: echo '<span title="AIモード：トレンド">📈</span>'; break;
    }
  ?>
</td>    <td>
<div class="dropdown" style="position: relative;">
  <button class="dropdown-button" onclick="toggleMenu(this.nextElementSibling)">操作 ▾</button>
  <div class="dropdown-menu">
    <a href="#" onclick="editAccountMaster(<?= $row['id'] ?>)">編集</a>
    <a href="#" onclick="editComment(<?= $row['id'] ?>)">ｺﾒﾝﾄ一覧</a>
    <a href="#" onclick="registComment(<?= $row['id'] ?>)">ｺﾒﾝﾄ登録</a>
    <?php if (!empty($_SESSION['check_enable'])): ?>
      <a href="#" onclick="editCheckAccount(<?= $row['id'] ?>)">自動ﾘﾌﾟ,ﾓﾉﾏﾈ編集</a>
    <?php endif; ?>
    <a href="#" onclick="editXLogin2(<?= $row['id'] ?>)">通常認証</a>
    <a href="#" onclick="editXLogin1(<?= $row['id'] ?>)">ﾒﾃﾞｨｱ認証</a>
    <form class="button_form" method="POST" action="?">
      <input type="hidden" name="type" value="account_del">
      <input type="hidden" name="id" value="<?= htmlspecialchars($row['id']) ?>">
      <button type="submit">削除</button>
    </form>
  </div>
</div>

    </td>
  </tr>
  <?php endwhile; ?>
</tbody>

</table>

    </div>

    <script>
    // 全選択/全解除機能
    function toggleSelectAll() {
        const checkboxes = document.querySelectorAll('input[name="selected_ids[]"]');
        const selectAllCheckbox = document.getElementById('select_all');
        checkboxes.forEach(checkbox => {
            checkbox.checked = selectAllCheckbox.checked;
        });
    }
</script>


    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
    <script>
        function editAccountMaster(id) {
            window.location.href = './account_edit.php?id='+id;
        }

        function editXLogin1(id) {
            window.location.href = './redirect.php?id='+id+'&type=1';
        }

        function editXLogin2(id) {
            window.location.href = './redirect.php?id='+id+'&type=2';
        }
 

        function deleteUser(button,id) {
            if (confirm("ユーザー ID " + id + " を削除します。")) {
                button.form.submit();
            }
        }

        function editComment(id) {
            window.location.href = './comment_list.php?account_id='+id;
        }

        function registComment(id) {
            window.location.href = './comment_regist.php?account_id='+id;
        }

        function editCheckAccount(id) {
            window.location.href = './search_list.php?account_id='+id;
        }
    </script>


    <script>
        $(document).ready(function() {
            $("input[name='new_username']").on("input", function() {
                var username = $(this).val();

                // ユーザー名が空でない場合にチェック
                if (username) {
                    $.get("./ajax/check_username.php", { username: username }, function(data) {
                        var result = JSON.parse(data);
                        if (result.exists) {
                            alert("このユーザー名は既に存在します。別のユーザー名を使用してください。");
                        }
                    });
                }
            });
        });
    </script>
  </div>
</body>
</html>
