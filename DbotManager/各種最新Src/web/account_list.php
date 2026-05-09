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
$search = trim($_GET['search'] ?? '');
$status_filter = trim($_GET['status'] ?? '');
$searchParam = '%' . $search . '%';

if ($search !== '') {
    $stmt = $conn->prepare("
    SELECT 
      am.name as name,
      am.id as id,
      am.login_id as login_id,
      am.bearer_token as bearer_token,
      am.refresh_token as refresh_token,
      am.access_token as access_token,
      am.search_enable as search_enable,
      am.use_admin_api as use_admin_api,
      am.ai_mode as ai_mode
    FROM account_master am
    WHERE  (am.regist_type = '' OR am.regist_type IS NULL) and am.user_id = ? AND am.name LIKE ?
    ");
    $stmt->bind_param("ss", $current_userid, $searchParam);
} else {
    $stmt = $conn->prepare("
    SELECT 
      am.name as name,
      am.id as id,
      am.login_id as login_id,
      am.bearer_token as bearer_token,
      am.refresh_token as refresh_token,
      am.access_token as access_token,
      am.search_enable as search_enable,
      am.use_admin_api as use_admin_api,
      am.ai_mode as ai_mode
    FROM account_master am
    WHERE  (am.regist_type = '' OR am.regist_type IS NULL) and am.user_id = ?
    ");
    $stmt->bind_param("s", $current_userid);
}
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


$status_sql = '';
if ($status_filter === 'suspention') {
    $status_sql = " AND am.is_suspended = 1";
} elseif ($status_filter === 'lock') {
    $status_sql = " AND am.is_locked = 1";
} elseif ($status_filter === 'unauthorized') {
    $status_sql = " AND am.is_unauthorized = 1";
}

if ($search !== '') {
    $stmt = $conn->prepare("
    SELECT am.name,am.id,am.login_id,am.bearer_token,am.refresh_token,am.access_token,am.search_enable,am.use_admin_api,am.ai_mode,
           am.is_locked,am.is_suspended,am.is_unauthorized
    FROM account_master am
    WHERE  (am.regist_type = '' OR am.regist_type IS NULL) and am.user_id=? AND am.name LIKE ? $status_sql
    ");
    $stmt->bind_param("ss", $current_userid, $searchParam);
} else {
    $stmt = $conn->prepare("
    SELECT am.name,am.id,am.login_id,am.bearer_token,am.refresh_token,am.access_token,am.search_enable,am.use_admin_api,am.ai_mode,
           am.is_locked,am.is_suspended,am.is_unauthorized
    FROM account_master am
    WHERE  (am.regist_type = '' OR am.regist_type IS NULL) and am.user_id=? $status_sql
    ");
    $stmt->bind_param("s", $current_userid);
}
$stmt->execute();
$result = $stmt->get_result();
// 集計取得
$stmt2 = $conn->prepare("
    SELECT 
        COUNT(*) as total,
        SUM(CASE WHEN am.is_locked = 1       THEN 1 ELSE 0 END) as lock_count,
        SUM(CASE WHEN am.is_suspended = 1    THEN 1 ELSE 0 END) as suspention_count,
        SUM(CASE WHEN am.is_unauthorized = 1 THEN 1 ELSE 0 END) as unauthorized_count,
        SUM(CASE WHEN (am.is_locked = 0 and am.is_suspended = 0 and am.is_unauthorized = 0 ) THEN 1 ELSE 0 END) as normal_count
    FROM account_master am
    WHERE  (am.regist_type = '' OR am.regist_type IS NULL) and am.user_id = ?
");
$stmt2->bind_param("s", $current_userid);
$stmt2->execute();
$summary = $stmt2->get_result()->fetch_assoc();
$stmt2->close();
?>

<!DOCTYPE html>
<html lang="ja">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>Xアカウント一覧(通常登録)</title>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="./css/admin-dashboard.css" />
</head>
<body>
    <div class="layout">
  <?php require PARTS_DIR.'/sidebar.php'; ?>


   <!-- コンテンツエリア -->
   <div class="content" id="content">

    <h2>Xアカウント一覧(通常登録)</h2>
    <div style="display:flex; align-items:center; gap:20px; margin-bottom:20px; flex-wrap:wrap;">
    <form method="GET" style="display:flex; gap:8px; align-items:center; flex-wrap:wrap;">
      <input type="text" name="search" placeholder="ユーザー名で絞り込み" value="<?php echo isset($_GET['search']) ? htmlspecialchars($_GET['search']) : ''; ?>">
      <input type="hidden" name="status" id="status_filter" value="<?php echo htmlspecialchars($_GET['status'] ?? ''); ?>">
      <button type="submit">検索</button>
      <button type="button" onclick="setStatus('')" style="background:<?= ($_GET['status']??'')=='' ? '#fff' : '#555' ?>; color:#000; border:none; padding:6px 12px; border-radius:4px; cursor:pointer;">全て</button>
      <button type="button" onclick="setStatus('suspention')" style="background:<?= ($_GET['status']??'')=='suspention' ? '#ef4444' : '#555' ?>; color:#fff; border:none; padding:6px 12px; border-radius:4px; cursor:pointer;">🚫 凍結のみ</button>
      <button type="button" onclick="setStatus('lock')" style="background:<?= ($_GET['status']??'')=='lock' ? '#f97316' : '#555' ?>; color:#fff; border:none; padding:6px 12px; border-radius:4px; cursor:pointer;">🔒 ロックのみ</button>
      <button type="button" onclick="setStatus('unauthorized')" style="background:<?= ($_GET['status']??'')=='unauthorized' ? '#6366f1' : '#555' ?>; color:#fff; border:none; padding:6px 12px; border-radius:4px; cursor:pointer;">🔑 再連携のみ</button>
    </form>
<script>
function setStatus(val) {
    document.getElementById('status_filter').value = val;
    document.getElementById('status_filter').closest('form').submit();
}
</script>
    <div style="display:flex; gap:20px; font-size:20px; align-items:center;">
      <span style="color:#aaa;">合計: <strong style="color:#fff; font-size:28px;"><?= $summary['total'] ?></strong></span>
      <span style="color:#4ade80;">正常: <strong style="font-size:28px;"><?= $summary['normal_count'] ?></strong></span>
      <span style="color:#facc15;">🔒 ロック: <strong style="font-size:28px;"><?= $summary['lock_count'] ?></strong></span>
      <span style="color:#6366f1;">🔑 再連携: <strong style="font-size:28px;"><?= $summary['unauthorized_count'] ?></strong></span>
      <span style="color:#ef4444;">🚫 凍結: <strong style="font-size:28px;"><?= $summary['suspention_count'] ?></strong></span>
      <button onclick="refreshLockedAccounts()" style="background:#f97316; color:#000; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-size:14px;">🔒 全エラーチェック</button>
      <button onclick="deleteFrozenAccounts()" style="background:#d4af37; color:#000; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-size:14px;">🚫 凍結一括削除</button>
<?php if (isset($_SESSION['admin']) && $_SESSION['admin'] == 1): ?>
<button onclick="showUserSummary()" style="background:#4ade80; color:#000; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-size:14px;">📊 ユーザー別集計</button>
<?php endif; ?>
    </div>
</div>

<div style="margin-bottom: 20px;">
  <div>
    チェックONのアカウントに対し以下の処理を実行：
  </div>

<form method="GET" action="?" style="display: flex; align-items: center; gap: 10px; flex-wrap: wrap; margin-top: 10px;">

  <!-- コマンド選択 -->
  <select id="command_option" name="command" onchange="toggleCommandSource()" style="width: auto; min-width: 140px;">
    <option value="post">ﾎﾟｽﾄｺﾒﾝﾄ</option>
    <option value="reply">ﾘﾌﾟﾗｲｺﾒﾝﾄ</option>
    <option value="replytoreply">ﾘﾌﾟtoﾘﾌﾟｺﾒﾝﾄ</option>
    <?php if (isset($_SESSION['check_enable']) && $_SESSION['check_enable'] == 1): ?>
      <option value="search">監視リプ,モノマネ</option>
    <?php endif; ?>
  </select>

  <span>を</span>

  <!-- 処理種別 -->
  <select id="action1_option" name="action1" onchange="toggleDuplicateSource()" style="width: auto; min-width: 120px;">
    <option value="duplicate">複製する</option>
    <option value="delete">削除する</option>
  </select>

  <!-- ON/OFF操作（初期非表示） -->
  <select id="action2_option" name="action2" style="display: none; width: auto; min-width: 120px;">
    <option value="on">ONにする</option>
    <option value="off">OFFにする</option>
  </select>

  <!-- 複製元選択 -->
  <div id="duplicate_source" style="display: inline-flex; align-items: center; gap: 5px; white-space: nowrap;">
    <span>(複製元：</span>
    <select id="form_account_id" name="xuser" style="width: auto; min-width: 140px;">
      <option value="">未選択</option>
      <?php foreach ($xusers as $k => $row) { ?>
        <option value="<?php echo e($row['id']) ?>" <?php echo ((string)$row['id'] === (string)$xuser_id ? 'selected' : ''); ?>>
          <?php echo e($row['name']) ?>
        </option>
      <?php } ?>
    </select>
    <span>)</span>
  </div>

  <!-- 実行ボタン -->
  <button type="submit" onclick="executeAction()" style="margin-left: 10px;">実行</button>

</form>



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
  ✅=通常認証 / 🎞️=メディア認証 / 🔍=監視 / 🏷️=API貸出 / 👩=AI（裏垢） / 🔥=AI(Xトレンド) / 💬=AI（yahooトレンド） / ₿=AI(BTC為替)
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
         onerror="this.onerror=null;this.src='img/noimage/noimage.jpg';"
         style="width: 60px; height: 60px; border-radius: 50%; object-fit: cover; border: 1px solid #ccc;">
    </td>  
    <td class="name-col">
      <div>
        <div>
  <?php echo htmlspecialchars($row['name']); ?> 
<span style="color: #888; font-size: 12px;">[ID=<?php echo htmlspecialchars($row['id']); ?>]</span>
<div style="margin-top: 4px;">
<?php if ((int)$row['is_suspended'] === 1): ?>
  <span style="background:#ef4444; color:white; font-size:11px; padding:2px 6px; border-radius:4px;">🚫 凍結</span>
<?php elseif ((int)$row['is_locked'] === 1): ?>
  <span style="background:#f97316; color:white; font-size:11px; padding:2px 6px; border-radius:4px;">🔒 ロック</span>
<?php elseif ((int)$row['is_unauthorized'] === 1): ?>
  <span style="background:#6366f1; color:white; font-size:11px; padding:2px 6px; border-radius:4px;">🔑 再連携</span>
<?php endif; ?>
</div>
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
      case 1: echo '<span title="AIモード：裏垢女子">👩</span>'; break;
      case 2: echo '<span title="AIモード：yahooトレンド">💬</span>'; break;
      case 6: echo '<span title="AIモード：Xトレンド">🔥</span>'; break;
      case 3: echo '<span title="AIモード：BTC為替">₿</span>'; break;
    }
  ?>
</td>    <td>
<div class="dropdown" style="position: relative;">
  <button class="dropdown-button" onclick="toggleMenu(this.nextElementSibling)">操作 ▾</button>
  <div class="dropdown-menu">
    <a href="#" onclick="editAccountMaster(<?= $row['id'] ?>)">編集</a>
    <a href="#" onclick="editComment(<?= $row['id'] ?>)">ｺﾒﾝﾄ一覧</a>
    <a href="#" onclick="registComment(<?= $row['id'] ?>)">ｺﾒﾝﾄ登録</a>
    <a href="#" onclick="refreshToken(<?= $row['id'] ?>)">ｱｶｳﾝﾄ更新&ﾛｯｸ解除🔄</a>
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

        function refreshToken(id) {
            if (!confirm('ID:' + id + ' のトークンを更新しますか？')) return;
    
            fetch('account_process.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    command: 'refresh_unlock',
                    selected_ids: [String(id)]
                })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                window.location.reload();
            })
            .catch(error => {
                console.error('エラー:', error);
            }
        );
}

function deleteFrozenAccounts() {
            if (!confirm('凍結アカウントを全て削除しますか？')) return;
            fetch('account_process.php', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ command: 'delete_frozen' })
            })
            .then(response => response.json())
            .then(data => {
                alert(data.message);
                window.location.reload();
            })
            .catch(error => { console.error('エラー:', error); });
        }

    function refreshLockedAccounts() {
    if (!confirm('ロック・再連携・凍結アカウントを全て一括更新しますか？')) return;
    fetch('account_process.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'refresh_locked' })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        window.location.reload();
    })
    .catch(error => { console.error('エラー:', error); });
}

        function showUserSummary() {
    fetch('account_process.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'get_user_summary' })
    })
    .then(response => response.json())
    .then(data => {
        let html = '<input type="text" id="user_filter" placeholder="ユーザー名で絞り込み" oninput="filterSummary()" style="margin-bottom:10px; padding:6px; width:100%; box-sizing:border-box; background:#333; color:#fff; border:1px solid #555; border-radius:4px;">';
        html += '<table id="summary_table" style="width:100%; border-collapse:collapse; color:#fff;">';
        html += '<tr style="background:#333;"><th style="padding:8px;">ユーザー</th><th style="padding:8px;">合計</th><th style="padding:8px; color:#4ade80;">正常</th><th style="padding:8px; color:#facc15;">ロック</th><th style="padding:8px; color:#ef4444;">凍結</th><th style="padding:8px; color:#6366f1;">再連携</th></tr>';
        data.rows.forEach(row => {
            html += `<tr class="summary_row" style="border-bottom:1px solid #444;">
                <td style="padding:8px;">${row.username}</td>
                <td style="padding:8px; text-align:center;">${row.total}</td>
                <td style="padding:8px; text-align:center; color:#4ade80;">${row.normal_count}</td>
                <td style="padding:8px; text-align:center; color:#facc15;">${row.lock_count}</td>
                <td style="padding:8px; text-align:center; color:#ef4444;">${row.suspention_count}</td>
                <td style="padding:8px; text-align:center; color:#6366f1;">${row.unauthorized_count}</td>
            </tr>`;
        });
        html += `<tr style="background:#444; font-weight:bold;">
            <td style="padding:8px;">合計</td>
            <td style="padding:8px; text-align:center;">${data.grand_total}</td>
            <td style="padding:8px; text-align:center; color:#4ade80;">${data.grand_normal}</td>
            <td style="padding:8px; text-align:center; color:#facc15;">${data.grand_lock}</td>
            <td style="padding:8px; text-align:center; color:#ef4444;">${data.grand_suspention}</td>
            <td style="padding:8px; text-align:center; color:#6366f1;">${data.grand_unauthorized}</td>
        </tr>`;
        html += '</table>';
        html += `<div style="margin-top:15px; text-align:right;">
        <button onclick="refreshAllLockedAccounts()" style="background:#f97316; color:#000; border:none; padding:6px 12px; border-radius:4px; cursor:pointer; font-size:14px;">🔒 全ユーザー一括更新</button>
        </div>`;
        document.getElementById('summary_modal_body').innerHTML = html;
        document.getElementById('summary_modal').style.display = 'flex';
    });
}

function filterSummary() {
    const filter = document.getElementById('user_filter').value.toLowerCase();
    document.querySelectorAll('.summary_row').forEach(row => {
        const name = row.cells[0].textContent.toLowerCase();
        row.style.display = name.includes(filter) ? '' : 'none';
    });
}

function refreshAllLockedAccounts() {
    if (!confirm('全ユーザーのロック・再連携・凍結アカウントを一括更新しますか？')) return;
    fetch('account_process.php', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ command: 'refresh_all_locked' })
    })
    .then(response => response.json())
    .then(data => {
        alert(data.message);
        window.location.reload();
    })
    .catch(error => { console.error('エラー:', error); });
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
  <div id="summary_modal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.7); z-index:9999; justify-content:center; align-items:center;">
    <div style="background:#222; padding:20px; border-radius:8px; min-width:500px; max-height:80vh; overflow-y:auto;">
        <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:15px;">
            <h3 style="color:#fff; margin:0;">ユーザー別集計</h3>
            <button onclick="document.getElementById('summary_modal').style.display='none'" style="background:none; border:none; color:#fff; font-size:20px; cursor:pointer;">✕</button>
        </div>
        <div id="summary_modal_body"></div>
    </div>
</div>
</body>
</html>
