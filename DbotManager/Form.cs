using DbotManager.Table;
using Google.Protobuf.WellKnownTypes;
using Mysqlx.Session;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.Design;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.IO;
using System.Linq;
using System.Security.Policy;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;

namespace DbotManager
{
    public partial class Form : System.Windows.Forms.Form
    {
        TweetTask _tweetTask;
        private MySqlDataAccess dataAccess;

        private bool _isLoading = true;

        private string dbMachineName = "localhost";
        private string dbUser = "d_bot";
        private string dbRoot = "root";
        private string dbPass = "abcd1234";

        List<KeyValuePair<int, string>> resereveCountList = new List<KeyValuePair<int, string>>()
        {
            new KeyValuePair<int, string>(1,"1"),
            new KeyValuePair<int, string>(2,"2"),
            new KeyValuePair<int, string>(3,"3"),
            new KeyValuePair<int, string>(4,"4"),
            new KeyValuePair<int, string>(5,"5"),
            new KeyValuePair<int, string>(6,"6"),
            new KeyValuePair<int, string>(7,"7"),
            new KeyValuePair<int, string>(8,"8"),
            new KeyValuePair<int, string>(9,"9"),
            new KeyValuePair<int, string>(10,"10"),
        };

        List<KeyValuePair<int, string>> resereveHourList = new List<KeyValuePair<int, string>>()
        {
            new KeyValuePair<int, string>(0,"1"),
            new KeyValuePair<int, string>(1,"1"),
            new KeyValuePair<int, string>(2,"2"),
            new KeyValuePair<int, string>(3,"3"),
            new KeyValuePair<int, string>(4,"4"),
            new KeyValuePair<int, string>(5,"5"),
            new KeyValuePair<int, string>(6,"6"),
            new KeyValuePair<int, string>(7,"7"),
            new KeyValuePair<int, string>(8,"8"),
            new KeyValuePair<int, string>(9,"9"),
            new KeyValuePair<int, string>(10,"10"),
            new KeyValuePair<int, string>(11,"11"),
            new KeyValuePair<int, string>(12,"12"),
            new KeyValuePair<int, string>(13,"13"),
            new KeyValuePair<int, string>(14,"14"),
            new KeyValuePair<int, string>(15,"15"),
            new KeyValuePair<int, string>(16,"16"),
            new KeyValuePair<int, string>(17,"17"),
            new KeyValuePair<int, string>(18,"18"),
            new KeyValuePair<int, string>(19,"19"),
            new KeyValuePair<int, string>(20,"20"),
            new KeyValuePair<int, string>(21,"21"),
            new KeyValuePair<int, string>(22,"22"),
            new KeyValuePair<int, string>(23,"23"),
            new KeyValuePair<int, string>(24,"24"),
            new KeyValuePair<int, string>(25,"25"),
            new KeyValuePair<int, string>(26,"26"),
            new KeyValuePair<int, string>(27,"27"),
            new KeyValuePair<int, string>(28,"28"),
        };

        public Form()
        {
            InitializeComponent();

            // MySQLデータアクセスの初期化
            dataAccess = new MySqlDataAccess(dbMachineName, dbUser, dbRoot, dbPass);
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            MakeFolder("python");
            _tweetTask = new TweetTask(AppendLog, dbMachineName, dbUser, dbRoot, dbPass);

            FillControls();
            _isLoading = false;
        }

        #region DataGridView


        #endregion

        #region FillControls

        private void FillControls()
        {
            FillDebugControls_TweetHistory();
            FillDebugControls_UserName();
            FillDebugControls_AccountMaster();
            FillDebugControls_CommentMaster();

            FillControls_Reserve();

        }


        private void FillDebugControls_TweetHistory()
        {
            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistoryView();

            if (tweetHistoryList != null)
            {
                dataGridViewTweetHistory.DataSource = tweetHistoryList;
            }
            else
            {
                MessageBox.Show("データを取得できませんでした。");
            }
        }

        private void FillDebugControls_AccountMaster()
        {
            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster().Where(x => x.UserId == GetUserId()).ToList();

            if (accountMasterList != null)
            {
                dataGridViewAccount.DataSource = accountMasterList;
            }
            else
            {
                MessageBox.Show("データを取得できませんでした。");
            }
        }

        private void FillDebugControls_CommentMaster()
        {

            List<CommentMaster> commentMasterList = dataAccess.GetCommentMaster().Where(x => x.UserId == GetUserId()).ToList();

            if (commentMasterList != null)
            {
                dataGridViewComment.DataSource = commentMasterList;
            }
            else
            {
                MessageBox.Show("データを取得できませんでした。");
            }
        }

        private void FillDebugControls_UserName()
        {
            List<UserMaster> userList = dataAccess.GetUserNames();

            if (userList != null)
            {
                comboBoxUserMaster.DataSource = userList;
                comboBoxUserMaster.DisplayMember = "Name"; // コンボボックスに表示するプロパティ
                comboBoxUserMaster.ValueMember = "Id";     // 選択されたときに取得するプロパティ
            }
            else
            {
                MessageBox.Show("ユーザー名を取得できませんでした。");
            }
        }
        #endregion

        #region Button

        private void buttonいいね_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = GetAccountId();
            int commentId = GetCommentId();
            string tweetId = GetTweetId(true);

            _tweetTask.TweetProc(TweetProcTypes.LIKE, userId, accountId, commentId, tweetId);
        }

        private void buttonブックマーク_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = GetAccountId();
            int commentId = GetCommentId();
            string tweetId = GetTweetId(true);

            _tweetTask.TweetProc(TweetProcTypes.BOOKMARK, userId, accountId, commentId, tweetId);
        }

        private void buttonリプライ_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = GetAccountId();
            int commentId = GetCommentId();
            string tweetId = GetTweetId(true);

            _tweetTask.TweetProc(TweetProcTypes.RETWEET, userId, accountId, commentId, tweetId);
        }

        private void buttonコメント_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = GetAccountId();
            int commentId = GetCommentId();
            string tweetId = GetTweetId(true);

            _tweetTask.TweetProc(TweetProcTypes.TWEET, userId, accountId, commentId, tweetId);
        }

        private void buttonいいねリスト作成_Click(object sender, EventArgs e)
        {
            if (radioButtonいいね件数50.Checked) _tweetTask.件数 = 50;
            else if (radioButtonいいね件数100.Checked) _tweetTask.件数 = 100;
            else if (radioButtonいいね件数200.Checked) _tweetTask.件数 = 200;
            else _tweetTask.件数 = int.Parse(textBoxいいね件数.Text);
            _tweetTask.制限時間以内に履歴ありの無料アカウントを排除 = checkBox_15分以内に履歴のある無料アカウントを除外する.Checked;
            _tweetTask.TargetTweetID = GetTweetId();

            _tweetTask.LikeEnable = checkBoxいいね.Checked;
            _tweetTask.BookmarkEnable = checkBoxブックマーク.Checked;
            _tweetTask.RetweetEnable = checkBoxリプライ.Checked;

            _tweetTask.InitAccountList();
            dataGridViewいいねリスト.DataSource = _tweetTask.TweetAccountList;

        }

        private void buttonいいねブックマーク実行_Click(object sender, EventArgs e)
        {
            _tweetTask.StartTask();
        }


        private void buttonクリアlog_Click(object sender, EventArgs e)
        {
            textBoxRenew.Text = string.Empty;
        }

        private void buttonDebugGetBearerToken_Click(object sender, EventArgs e)
        {
            string command = _tweetTask.GetTweetCommand(TweetProcTypes.GET_REFRESHTOKEN, GetUserId(), GetAccountId(), GetCommentId(), GetTweetId(true));

            // クリップボードに文字列を設定
            Clipboard.SetText(command);
            MessageBox.Show("コマンドプロンプトに貼り付け操作を行って実行してください", "確認");
            Process.Start("cmd.exe"); // "/k" はコマンド実行後もウィンドウを開いたままにする

        }

        private void buttonDebugGetAccessToken_Click(object sender, EventArgs e)
        {
            string command = _tweetTask.GetTweetCommand(TweetProcTypes.GET_ACCESSTOKEN, GetUserId(), GetAccountId(), GetCommentId(), GetTweetId(true));

            // クリップボードに文字列を設定
            Clipboard.SetText(command);
            MessageBox.Show("コマンドプロンプトに貼り付け操作を行って実行してください", "確認");
            Process.Start("cmd.exe"); // "/k" はコマンド実行後もウィンドウを開いたままにする

        }

        private void button1_Click(object sender, EventArgs e)
        {
            FillControls();
        }

        #endregion

        #region その他イベント

        private void comboBoxUserMaster_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            FillDebugControls_AccountMaster();
            FillDebugControls_CommentMaster();
        }
        #endregion

        #region その他処理

        private int GetUserId()
        {
            return (int)comboBoxUserMaster.SelectedValue;
        }

        private int GetAccountId()
        {
            // 選択されている行があるか確認
            if (dataGridViewAccount.SelectedRows.Count > 0)
            {
                // 選択されている最初の行を取得
                DataGridViewRow selectedRow = dataGridViewAccount.SelectedRows[0];

                // 特定の列（例: 列インデックスが2の列）の値を取得
                var cellValue = selectedRow.Cells[AccountMaster_Id.Name].Value;

                return int.Parse(cellValue.ToString());
            }
            return 0;
        }

        private int GetCommentId()
        {
            // 選択されている行があるか確認
            if (dataGridViewComment.SelectedRows.Count > 0)
            {
                // 選択されている最初の行を取得
                DataGridViewRow selectedRow = dataGridViewComment.SelectedRows[0];

                // 特定の列（例: 列インデックスが2の列）の値を取得
                var cellValue = selectedRow.Cells[CommentMaster_Id.Name].Value;

                return int.Parse(cellValue.ToString());
            }
            return 0;
        }

        private string GetTweetId(bool debug_mode = false)
        {
            string input = debug_mode ? textBoxUrlTweetID_Debug.Text : textBoxUrlTweetID.Text;
            string extractedNumber = ExtractNumber(input);

            if (extractedNumber != null)
            {
                Console.WriteLine($"Extracted number: {extractedNumber}");
            }
            else
            {
                Console.WriteLine("No valid number found.");
            }

            return extractedNumber;
        }

        private string ExtractNumber(string input)
        {
            // URLの場合と単なる数値の場合を考慮
            Match match = Regex.Match(input, @"(?:status/(\d+)|^(\d+))");

            if (match.Success)
            {
                // マッチした部分のうち、最初にキャプチャされたグループ（数値部分）を返す
                return match.Groups[1].Success ? match.Groups[1].Value : match.Groups[2].Value;
            }

            return null;
        }

        #endregion

        #region ファイル処理関連

        // TextBoxにログを表示するメソッド
        private void AppendLog(string message)
        {
            if (message != null)
            {
                textBoxRenew.Invoke((MethodInvoker)(() =>
                    textBoxRenew.AppendText(message + Environment.NewLine)
                ));

                // 必要に応じてログファイルにも書き込む
                SaveLogToFile(message);
            }
            /*
            if (message != null)
            {
                textBoxLog.Invoke((MethodInvoker)(() => textBoxLog.AppendText(message + Environment.NewLine)));

                // ログファイルに書き込み
                SaveLogToFile(message);
            }
            */
        }

        // ログメッセージを日付別のファイルに保存するメソッド
        private void SaveLogToFile(string message)
        {
            // ログフォルダのパスを設定
            string logDirectory = "log";

            MakeFolder(logDirectory);

            // 日付別のログファイルパスを設定
            string logFilePath = Path.Combine(logDirectory, $"log_{DateTime.Now:yyyyMMdd}.txt"); // 例: log/log_20241113.txt

            try
            {
                // メッセージを追記で日別ログファイルに書き込み
                using (StreamWriter writer = new StreamWriter(logFilePath, true))
                {
                    writer.WriteLine($"{DateTime.Now:yyyy-MM-dd HH:mm:ss}: {message}");
                }
            }
            catch (Exception ex)
            {
                // ファイル書き込みに失敗した場合のエラーハンドリング
                textBoxRenew.Invoke((MethodInvoker)(() => textBoxRenew.AppendText("ログの書き込みに失敗しました: " + ex.Message + Environment.NewLine)));
            }
        }

        private void MakeFolder(string folderPath)
        {
            // ログフォルダが存在しない場合は作成
            if (!Directory.Exists(folderPath))
            {
                Directory.CreateDirectory(folderPath);
            }
        }




        #endregion

        #region コメントタブ
        private void dataGridViewComment_SelectionChanged(object sender, EventArgs e)
        {
        }

        private void buttonコメント編集_Click(object sender, EventArgs e)
        {
            FillDebugControls_コメント();
        }


        private void FillDebugControls_コメント()
        {
            int commentId = GetCommentId();

            CommentMaster commentMaster = dataAccess.GetCommentMaster(commentId);

            checkBoxコメント有効.Checked = commentMaster.Enable;
            checkBoxコメント_全アカウント共通.Checked = commentMaster.Whole;
            textBoxコメント.Text = commentMaster.Comment;
            textBoxコメント_コメントID.Text = commentId.ToString();
            textBoxコメント_UserID.Text = commentMaster.UserId.ToString();
            textBoxコメント_AccountId.Text = commentMaster.AccountId.ToString();
        }

        private void buttonコメント削除_Click(object sender, EventArgs e)
        {
            dataAccess.DeleteCommentMaster(int.Parse(textBoxコメント_コメントID.Text));
            FillDebugControls_CommentMaster();

        }

        private void buttonコメント追加_Click(object sender, EventArgs e)
        {
            CommentMaster commentMaster = new CommentMaster()
            {
                Id = int.Parse(textBoxコメント_コメントID.Text),
                UserId = int.Parse(textBoxコメント_UserID.Text),
                AccountId = int.Parse(textBoxコメント_AccountId.Text),
                Whole = checkBoxコメント_全アカウント共通.Checked,
                Enable = checkBoxコメント有効.Checked,
                Comment = textBoxコメント.Text,
            };

            dataAccess.InsertCommentMaster(commentMaster);
            FillDebugControls_CommentMaster();

        }

        private void buttonコメント保存_Click(object sender, EventArgs e)
        {
            CommentMaster commentMaster = new CommentMaster()
            {
                Id = int.Parse(textBoxコメント_コメントID.Text),
                UserId = int.Parse(textBoxコメント_UserID.Text),
                AccountId = int.Parse(textBoxコメント_AccountId.Text),
                Whole = checkBoxコメント_全アカウント共通.Checked,
                Enable = checkBoxコメント有効.Checked,
                Comment = textBoxコメント.Text,
            };

            dataAccess.UpdateCommentMaster(commentMaster);
            FillDebugControls_CommentMaster();
        }


        #endregion

        private void dataGridViewAccount_CellDoubleClick(object sender, DataGridViewCellEventArgs e)
        {
            // ヘッダー部分をダブルクリックした場合は無視
            if (e.RowIndex < 0)
                return;

            // ダブルクリックされた行と列の値を取得
            DataGridViewRow selectedRow = dataGridViewAccount.Rows[e.RowIndex];
            string accountId = selectedRow.Cells["AccountMaster_Id"].Value?.ToString() ?? string.Empty;
            string userId = selectedRow.Cells["AccountMaster_UserId"].Value?.ToString() ?? string.Empty;


            FillControlsReserveSetting(int.Parse(userId) , int.Parse(accountId));
        }

        private void FillControls_Reserve()
        {
            comboBox予約設定１_回数.DataSource = new BindingList<KeyValuePair<int, string>>(resereveCountList); 
            comboBox予約設定１_回数.DisplayMember = "Value";
            comboBox予約設定１_回数.ValueMember = "Key";

            comboBox予約設定２_回数.DataSource = new BindingList<KeyValuePair<int, string>>(resereveCountList); 
            comboBox予約設定２_回数.DisplayMember = "Value";
            comboBox予約設定２_回数.ValueMember = "Key";

            comboBox予約設定３_回数.DataSource = new BindingList<KeyValuePair<int, string>>(resereveCountList);
            comboBox予約設定３_回数.DisplayMember = "Value";
            comboBox予約設定３_回数.ValueMember = "Key";

            comboBox予約設定１_Start.DataSource = new BindingList<KeyValuePair<int, string>>(resereveHourList);
            comboBox予約設定１_Start.DisplayMember = "Value";
            comboBox予約設定１_Start.ValueMember = "Key";
            comboBox予約設定２_Start.DataSource = new BindingList<KeyValuePair<int, string>>(resereveHourList);
            comboBox予約設定２_Start.DisplayMember = "Value";
            comboBox予約設定２_Start.ValueMember = "Key";
            comboBox予約設定３_Start.DataSource = new BindingList<KeyValuePair<int, string>>(resereveHourList);
            comboBox予約設定３_Start.DisplayMember = "Value";
            comboBox予約設定３_Start.ValueMember = "Key";
            comboBox予約設定１_End.DataSource = new BindingList<KeyValuePair<int, string>>(resereveHourList);
            comboBox予約設定１_End.DisplayMember = "Value";
            comboBox予約設定１_End.ValueMember = "Key";
            comboBox予約設定２_End.DataSource = new BindingList<KeyValuePair<int, string>>(resereveHourList);
            comboBox予約設定２_End.DisplayMember = "Value";
            comboBox予約設定２_End.ValueMember = "Key";
            comboBox予約設定３_End.DataSource = new BindingList<KeyValuePair<int, string>>(resereveHourList);
            comboBox予約設定３_End.DisplayMember = "Value";
            comboBox予約設定３_End.ValueMember = "Key";
        }


        private void FillControlsReserveSetting(int userId , int accountId)
        {
            // テキストボックスに値を設定
            textBox予約_AccountId.Text = accountId.ToString();
            textBox予約_UserId.Text = userId.ToString();

            var reserveItem = dataAccess.GetReserveMaster(accountId);

            if(reserveItem == null)
            {
                reserveItem = new ReserveMaster()
                {
                    AccountId = accountId,
                    Reserve1Count = 1,
                    Reserve1StartHour = 8,
                    Reserve1EndHour = 10,
                    Reserve1Enable = false,
                    Reserve2Count = 1,
                    Reserve2StartHour = 8,
                    Reserve2EndHour = 10,
                    Reserve2Enable = false,
                    Reserve3Count = 1,
                    Reserve3StartHour = 8,
                    Reserve3EndHour = 10,
                    Reserve3Enable = false,
                };
                dataAccess.InsertReserveMaster(reserveItem);
            }

            checkBox予約設定1.Checked = reserveItem.Reserve1Enable;
            checkBox予約設定2.Checked = reserveItem.Reserve2Enable;
            checkBox予約設定3.Checked = reserveItem.Reserve3Enable;

            comboBox予約設定１_Start.SelectedValue = reserveItem.Reserve1StartHour;
            comboBox予約設定２_Start.SelectedValue = reserveItem.Reserve2StartHour;
            comboBox予約設定３_Start.SelectedValue = reserveItem.Reserve3StartHour;

            comboBox予約設定１_End.SelectedValue = reserveItem.Reserve1EndHour;
            comboBox予約設定２_End.SelectedValue = reserveItem.Reserve2EndHour;
            comboBox予約設定３_End.SelectedValue = reserveItem.Reserve3EndHour;

            comboBox予約設定１_回数.SelectedValue = reserveItem.Reserve1Count;
            comboBox予約設定２_回数.SelectedValue = reserveItem.Reserve2Count;
            comboBox予約設定３_回数.SelectedValue = reserveItem.Reserve3Count;

        }

        private void button予約保存_Click(object sender, EventArgs e)
        {
            // テキストボックスに値を設定
            int accountId = int.Parse(textBox予約_AccountId.Text);
            int userId = int.Parse(textBox予約_UserId.Text);

            ReserveMaster reservedItem = new ReserveMaster()
            {
                UserId = userId,
                AccountId = accountId,
                Reserve1Enable = checkBox予約設定1.Checked,
                Reserve2Enable = checkBox予約設定2.Checked,
                Reserve3Enable = checkBox予約設定3.Checked,
                Reserve1StartHour = int.Parse(comboBox予約設定１_Start.SelectedValue.ToString()),
                Reserve2StartHour = int.Parse(comboBox予約設定２_Start.SelectedValue.ToString()),
                Reserve3StartHour = int.Parse(comboBox予約設定３_Start.SelectedValue.ToString()),
                Reserve1EndHour = int.Parse(comboBox予約設定１_End.SelectedValue.ToString()),
                Reserve2EndHour = int.Parse(comboBox予約設定２_End.SelectedValue.ToString()),
                Reserve3EndHour = int.Parse(comboBox予約設定３_End.SelectedValue.ToString()),
                Reserve1Count = int.Parse(comboBox予約設定１_回数.SelectedValue.ToString()),
                Reserve2Count = int.Parse(comboBox予約設定２_回数.SelectedValue.ToString()),
                Reserve3Count = int.Parse(comboBox予約設定３_回数.SelectedValue.ToString()),
            };

            dataAccess.UpdateReserveMaster(reservedItem);

        }

        private void button予約作成_Click(object sender, EventArgs e)
        {
            var accountList = dataAccess.GetAccountMaster(true).Where(x => x.Enable && x.TweetEnable);

            List<ReserveMaster> reserveMasterList = new List<ReserveMaster>();
            List<CommentMaster> commentMasterList = dataAccess.GetCommentMaster();

            foreach(var account in accountList)
            {
                reserveMasterList.Add(dataAccess.GetReserveMaster(account.Id));
            }

            List<ReserveSchedule> reserveScheduleList = new List<ReserveSchedule>();

            foreach(var reserve in reserveMasterList)
            {
                var commentList = commentMasterList.Where(x => x.UserId == reserve.UserId).ToList();

                if (reserve.Reserve1Enable)
                {
                    var scheduleWk = MakeSchedule(reserve.Reserve1Count , reserve.Reserve1StartHour , reserve.Reserve1EndHour , reserve.UserId , reserve.AccountId , commentList ,1);
                    reserveScheduleList.AddRange(scheduleWk);
                }

                if (reserve.Reserve2Enable)
                {
                    var scheduleWk = MakeSchedule(reserve.Reserve2Count, reserve.Reserve2StartHour, reserve.Reserve2EndHour, reserve.UserId, reserve.AccountId, commentList, 2);
                    reserveScheduleList.AddRange(scheduleWk);
                }

                if (reserve.Reserve3Enable)
                {
                    var scheduleWk = MakeSchedule(reserve.Reserve3Count, reserve.Reserve3StartHour, reserve.Reserve3EndHour, reserve.UserId, reserve.AccountId, commentList, 3);
                    reserveScheduleList.AddRange(scheduleWk);
                }
            }

            foreach(var item in reserveScheduleList)
            {
                dataAccess.InsertReserveSchedule(item);
            }

            dataGridViewReserveSchedule.DataSource = reserveScheduleList;

        }

        private List<ReserveSchedule> MakeSchedule(int count, int startHour, int endHour, int userId, int accountId, List<CommentMaster> commentList , int type)
        {
            var schedules = new List<ReserveSchedule>();
            var random = new Random();

            // 今日の日付
            var today = DateTime.Today;

            // 開始時刻と終了時刻
            var startDateTime = startHour >= 24
                ? today.AddDays(1).AddHours(startHour - 24) // 翌日の時間
                : today.AddHours(startHour);

            var endDateTime = endHour >= 24
                ? today.AddDays(1).AddHours(endHour - 24) // 翌日の時間
                : today.AddHours(endHour);                // 当日の時間

            // ランダムな時間を生成する
            for (int i = 0; i < count; i++)
            {
                DateTime randomTime;

                do
                {
                    // ランダムな時刻を生成
                    var totalMinutes = (int)(endDateTime - startDateTime).TotalMinutes;
                    randomTime = startDateTime.AddMinutes(random.Next(totalMinutes));
                }
                // 直前のスケジュールと5分以上の間隔を設ける
                while (schedules.Any(s => Math.Abs(((DateTime)s.ReserveTime - randomTime).TotalMinutes) < 5));

                // CommentMaster からランダムに1つ選択
                var randomComment = commentList[random.Next(commentList.Count)];

                // スケジュールを追加
                schedules.Add(new ReserveSchedule
                {
                    ReserveDate = today,
                    ReserveTime = randomTime,
                    UserId = userId,
                    AccountId = accountId,
                    CommentId = randomComment.Id,
                    ReserveId = $"{type}-{(i+1)}",
                    Result = ""
                });
            }

            return schedules;
        }

    }
}