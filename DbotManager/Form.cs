using DbotManager.MySql;
using DbotManager.Table;
using Google.Protobuf.WellKnownTypes;
using Mysqlx.Session;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.Design;
using System.Data;
using System.Data.Common;
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
using static System.Windows.Forms.VisualStyles.VisualStyleElement.Window;

namespace DbotManager
{
    public partial class Form : System.Windows.Forms.Form
    {
        TweetTask _tweetTask;

        public DbConnectionInfo DbConnection = new DbConnectionInfo();

        private MySqlDataAccess dataAccess;

        private bool _isLoading = true;

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


            DbConnection.MachineName = "localhost";
            DbConnection.User = "d_bot";
            DbConnection.Root = "root";
            DbConnection.Pass = "abcd1234";

            // MySQLデータアクセスの初期化
            dataAccess = new MySqlDataAccess(DbConnection);
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            SupportUtil.MakeFolder("python");
            _tweetTask = new TweetTask(DbConnection , AppendLog);

            FillControls();
            _isLoading = false;
        }

        #region DataGridView


        #endregion

        #region FillControls

        private void FillControls()
        {
            FillDebugControls_TweetHistory();
            FillDebugControls_AccountMaster();

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
        }

        #endregion

        #region Button

        private class 処理アカウントInfo
        {
            public int ID { get; set; }
            public string UserName { get; set; }
            public string AccountName { get; set; }
        }


        private void buttonいいねリスト作成_Click(object sender, EventArgs e)
        {
            /*
            if (radioButtonいいね件数50.Checked) _tweetTask.件数 = 50;
            else if (radioButtonいいね件数100.Checked) _tweetTask.件数 = 100;
            else if (radioButtonいいね件数200.Checked) _tweetTask.件数 = 200;
            else _tweetTask.件数 = int.Parse(textBoxいいね件数.Text);
            */

            _tweetTask.いいね件数 = checkBoxいいね.Checked ? int.Parse(textBoxいいね件数.Text) : 0;
            _tweetTask.ブックマーク件数 = checkBoxブックマーク.Checked ? int.Parse(textBoxブックマーク.Text) : 0 ;
            _tweetTask.リプライ件数 = checkBoxリプライ.Checked ? int.Parse(textBoxリプライ.Text) : 0;

            _tweetTask.制限時間以内に履歴ありの無料アカウントを排除 = checkBox_15分以内に履歴のある無料アカウントを除外する.Checked;
            _tweetTask.TargetTweetID = GetTweetId();

            _tweetTask.LikeEnable = checkBoxいいね.Checked;
            _tweetTask.BookmarkEnable = checkBoxブックマーク.Checked;
            _tweetTask.ReplyEnable = checkBoxリプライ.Checked;

            _tweetTask.InitAccountList();

            var userList = dataAccess.GetUserNames();

            {
                List<処理アカウントInfo> list = new List<処理アカウントInfo>();
                foreach (var item in _tweetTask.LikeAccountList)
                {
                    list.Add(new 処理アカウントInfo()
                    {
                        ID = item.Id,
                        AccountName = item.Name,
                        UserName = userList.Where(x => x.Id == item.UserId).FirstOrDefault().Name
                    });
                }
                dataGridViewいいね.DataSource = list;
            }

            {
                List<処理アカウントInfo> list = new List<処理アカウントInfo>();
                foreach (var item in _tweetTask.BookmarkAccountList)
                {
                    list.Add(new 処理アカウントInfo()
                    {
                        ID = item.Id,
                        AccountName = item.Name,
                        UserName = userList.Where(x => x.Id == item.UserId).FirstOrDefault().Name
                    });
                }
                dataGridViewブックマーク.DataSource = list;
            }

            {
                List<処理アカウントInfo> list = new List<処理アカウントInfo>();
                foreach (var item in _tweetTask.ReplyAccountList)
                {
                    list.Add(new 処理アカウントInfo()
                    {
                        ID = item.Id,
                        AccountName = item.Name,
                        UserName = userList.Where(x => x.Id == item.UserId).FirstOrDefault().Name
                    });
                }
                dataGridViewリプライ.DataSource = list;
            }

        }

        private void buttonいいねブックマーク実行_Click(object sender, EventArgs e)
        {
            _tweetTask.StartTask();
        }


        private void buttonクリアlog_Click(object sender, EventArgs e)
        {
            textBoxRenew.Text = string.Empty;
        }

        #endregion

        #region その他イベント

        private void comboBoxUserMaster_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            FillDebugControls_AccountMaster();
        }
        #endregion

        #region その他処理

        private string GetTweetId()
        {
            string input = textBoxUrlTweetID.Text;
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
                SupportUtil.SaveLogToFile(message , textBoxRenew);
            }
        }

        /*

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
        */
#endregion

        #region コメントタブ

        private CommentDialog _commentDialog;

        private void buttonコメント編集_Click(object sender, EventArgs e)
        {
            // ダイアログが未作成または破棄されている場合に新しいダイアログを作成
            if (_commentDialog == null || _commentDialog.IsDisposed)
            {
                _commentDialog = new CommentDialog(DbConnection);
                _commentDialog.Show();
//                _commentDialog.UpdateInfo(GetAccountId());
            }
            else
            {
                // 既に開いている場合はフォーカスを移動
                _commentDialog.Focus();
            }
        }

        #endregion

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

            dataAccess.DeleteReserveSchedule(DateTime.Today);

            foreach (var item in reserveScheduleList)
            {
                dataAccess.InsertReserveSchedule(item);
            }

            dataGridViewReserveSchedule.DataSource = dataAccess.GetReserveScheduleView(DateTime.Today).OrderBy(x => x.ReserveTime).ToList();

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
                    randomTime = startDateTime.AddMinutes(random.Next(totalMinutes)).AddSeconds(random.Next(60));
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
                    ReserveId = $"{accountId}-{type}-{(i+1)}",
                    Result = false
                });
            }

            return schedules;
        }


        AccountDialog _accountDialog;

        private void buttonアカウント設定_Click(object sender, EventArgs e)
        {
            // ダイアログが未作成または破棄されている場合に新しいダイアログを作成
            if (_accountDialog == null || _accountDialog.IsDisposed)
            {
                _accountDialog = new AccountDialog(DbConnection);
                _accountDialog.Show();
            }
            else
            {
                // 既に開いている場合はフォーカスを移動
                _accountDialog.Focus();
            }
        }
    }
}