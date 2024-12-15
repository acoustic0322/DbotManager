using DbotManager.MySql;
using DbotManager.Table;
using DbotManager.Entity;
using Google.Protobuf.WellKnownTypes;
using Mysqlx.Session;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.ComponentModel.Design;
using System.Data;
using System.Data.Common;
using System.Data.Odbc;
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

        private WebCommand _webCommand;

        List<TweetHistory> _tweetHistoryList;


        public Form(string[] args)
        {
            InitializeComponent();


            DbConnection.MachineName = "localhost";
            DbConnection.User = "d_bot";
            DbConnection.Root = "root";
            DbConnection.Pass = "abcd1234";

            // MySQLデータアクセスの初期化
            dataAccess = new MySqlDataAccess(DbConnection);

            _webCommand = InitWebCommand(args);
        }

        private WebCommand InitWebCommand(string[] args)
        {
            WebCommand ret = new WebCommand() 
            {
                Enable = false,
                UserId = 0,
                Like=false,
                Bookmark=false,
                Reply=false,
                Repost=false,
                LikeCount = 110,
                BookmarkCount = 110,
                ReplyCount = 260,
                RepostCount = 260,
                Duplicate = true
            };

            if (args.Length > 0)
            {
                // 引数の解析
                Dictionary<string, string> parameters = ParseArguments(args);

                string receivedArgs = string.Join(", ", args);

                ret.Enable = true;

                // パラメータの処理例
                if (parameters.TryGetValue("UserId", out string userId))
                {
                    ret.UserId = int.Parse(userId);
                }

                if (parameters.TryGetValue("TweetId", out string tweetId))
                {
                    ret.TargetTweetId = tweetId;
                }

                if (parameters.TryGetValue("Like", out string likeValue) && bool.TryParse(likeValue, out bool like))
                {
                    ret.Like = like;
                }

                if (parameters.TryGetValue("Bookmark", out string bookmarkValue) && bool.TryParse(bookmarkValue, out bool bookmark))
                {
                    ret.Bookmark = bookmark;
                }

                if (parameters.TryGetValue("Reply", out string replyValue) && bool.TryParse(replyValue, out bool reply))
                {
                    ret.Reply = reply;
                }

                if (parameters.TryGetValue("Repost", out string repostValue) && bool.TryParse(repostValue, out bool repost))
                {
                    ret.Repost = repost;
                }

                if (parameters.TryGetValue("LikeCount", out string likeCount))
                {
                    ret.LikeCount = int.Parse(likeCount);
                }

                if (parameters.TryGetValue("BookmarkCount", out string bookmarkCount))
                {
                    ret.BookmarkCount = int.Parse(bookmarkCount);
                }

                if (parameters.TryGetValue("RepostCount", out string repostCount))
                {
                    ret.RepostCount = int.Parse(repostCount);
                }

                if (parameters.TryGetValue("ReplyCount", out string replyCount))
                {
                    ret.ReplyCount = int.Parse(replyCount);
                }


                if (parameters.TryGetValue("Duplicate", out string duplicateValue) && bool.TryParse(duplicateValue, out bool duplicate))
                {
                    ret.Duplicate = duplicate;
                }
            }

            return ret;
        }

        // 引数をキーと値のペアに変換するメソッド
        private Dictionary<string, string> ParseArguments(string[] args)
        {
            var result = new Dictionary<string, string>(StringComparer.OrdinalIgnoreCase);

            foreach (var arg in args)
            {
                var parts = arg.Split('=');
                if (parts.Length == 2)
                {
                    string key = parts[0].Trim();
                    string value = parts[1].Trim();
                    result[key] = value;
                }
            }

            return result;
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
            FillDebugControls_UserName();
            FillControls_WebCommand();
        }

        private void FillControls_WebCommand()
        {
            if(_webCommand.Enable)
            {
                checkBox_15分以内に履歴のある無料アカウントを除外する.Checked = true;
                checkBoxいいね.Checked = _webCommand.Like;
                checkBoxブックマーク.Checked = _webCommand.Bookmark;
                checkBoxリプライ.Checked = _webCommand.Reply;
                checkBoxリポスト.Checked = _webCommand.Repost;
                checkBoxUserID.Checked = true;
                comboBoxUserMaster.SelectedValue = _webCommand.UserId;

                textBoxUrlTweetID.Text = _webCommand.TargetTweetId;

                textBoxいいね件数.Text = _webCommand.LikeCount.ToString();
                textBoxブックマーク件数.Text = _webCommand.BookmarkCount.ToString();
                textBoxリプライ件数.Text = _webCommand.ReplyCount.ToString();
                textBoxリポスト件数.Text = _webCommand.RepostCount.ToString();

                checkBoxDuplicate.Checked = _webCommand.Duplicate;

                MakeList();

#if DEBUG
#else
                ExeList();
                this.Close();
#endif
            }
        }

        private void FillDebugControls_TweetHistory()
        {
            _tweetHistoryList = dataAccess.GetTweetHistoryView();
            UpdateTweetHistoryFilter();

        }

        private void UpdateTweetHistoryFilter()
        {
            if (_tweetHistoryList != null)
            {
                if (string.IsNullOrEmpty(textBoxSearchHistoryAccountId.Text))
                {
                    dataGridViewTweetHistory.DataSource = _tweetHistoryList;
                }
                else
                {
                    int historyAccountId;
                    int.TryParse(textBoxSearchHistoryAccountId.Text, out historyAccountId);
                    dataGridViewTweetHistory.DataSource = _tweetHistoryList.Where(x => x.AccountId == historyAccountId).ToList();
                }

            }
            else
            {
                MessageBox.Show("データを取得できませんでした。");
            }

        }

        private void FillDebugControls_AccountMaster()
        {
        }

        private void FillDebugControls_UserName()
        {
            List<UserMaster> userList = dataAccess.GetUserMaster();

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

        private class 処理アカウントInfo
        {
            public int ID { get; set; }
            public string UserName { get; set; }
            public string AccountName { get; set; }
            public string Comment { get; set; }
            public string Media { get; set; }
        }


        private void buttonMakeList_Click(object sender, EventArgs e)
        {
            MakeList();
        }

        private void buttonExeList_Click(object sender, EventArgs e)
        {
            ExeList();
        }

        private void buttonクリアlog_Click(object sender, EventArgs e)
        {
            textBoxRenew.Text = string.Empty;
        }

        #endregion

        #region その他イベント

        private void comboBoxUserMaster_SelectedIndexChanged(object sender, EventArgs e)
        {

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

        #region TweetTask関連


        private void MakeList()
        {
            _tweetTask.いいね件数 = checkBoxいいね.Checked ? int.Parse(textBoxいいね件数.Text) : 0;
            _tweetTask.リプライ件数 = checkBoxリプライ.Checked ? int.Parse(textBoxリプライ件数.Text) : 0;
            _tweetTask.ブックマーク件数 = checkBoxブックマーク.Checked ? int.Parse(textBoxブックマーク件数.Text) : 0;
            _tweetTask.リポスト件数 = checkBoxリポスト.Checked ? int.Parse(textBoxリポスト件数.Text) : 0;

            _tweetTask.制限時間以内に履歴ありの無料アカウントを排除 = checkBox_15分以内に履歴のある無料アカウントを除外する.Checked;
            _tweetTask.TargetTweetID = GetTweetId();

            _tweetTask.LikeEnable = checkBoxいいね.Checked;
            _tweetTask.ReplyEnable = checkBoxリプライ.Checked;
            _tweetTask.BookmarkEnable = checkBoxブックマーク.Checked;
            _tweetTask.RepostEnable = checkBoxリポスト.Checked;
            _tweetTask.DuplicateEnable = checkBoxDuplicate.Checked;

            _tweetTask.UserId = checkBoxUserID.Checked ? int.Parse(comboBoxUserMaster.SelectedValue.ToString()) : 0;

            _tweetTask.InitAccountList();

            var userList = dataAccess.GetUserMaster();
            var commentList = dataAccess.GetCommentMaster();
            var mediaList = dataAccess.GetMediaMaster();

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
                dataGridViewいいね.DataSource = list.OrderBy(x => x.ID).ToList();
                labelいいね件数.Text = $"({list.Count}件)";
            }

            {
                List<処理アカウントInfo> list = new List<処理アカウントInfo>();
                foreach (var item in _tweetTask.ReplyAccountList)
                {
                    var photoName = string.Empty;
                    if(item.PhotoId != 0)
                    {
                        photoName = mediaList.Where(x => x.MediaId == item.PhotoId).FirstOrDefault().Name + "(P)";
                    }
                    var movieName = string.Empty;
                    if (item.MovieId != 0)
                    {
                        movieName = mediaList.Where(x => x.MediaId == item.MovieId).FirstOrDefault().Name + "(M)";
                    }

                    list.Add(new 処理アカウントInfo()
                    {
                        ID = item.Id,
                        AccountName = item.Name,
                        UserName = userList.Where(x => x.Id == item.UserId).FirstOrDefault().Name,
                        Comment = commentList.Where(x => x.Id == item.CommentId).FirstOrDefault().Comment,
                        Media = photoName + movieName
                    }) ;
                }
                dataGridViewリプライ.DataSource = list.OrderBy(x => x.ID).ToList();
                labelリプライ.Text = $"({list.Count}件)";
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
                dataGridViewブックマーク.DataSource = list.OrderBy(x => x.ID).ToList();
                labelブックマーク件数.Text = $"({list.Count}件)";
            }

            {
                List<処理アカウントInfo> list = new List<処理アカウントInfo>();
                foreach (var item in _tweetTask.RepostAccountList)
                {
                    list.Add(new 処理アカウントInfo()
                    {
                        ID = item.Id,
                        AccountName = item.Name,
                        UserName = userList.Where(x => x.Id == item.UserId).FirstOrDefault().Name
                    });
                }
                dataGridViewリポスト.DataSource = list.OrderBy(x => x.ID).ToList();
                labelリポスト件数.Text = $"({list.Count}件)";
            }
        }

        private void ExeList()
        {
            _tweetTask.StartTask();
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
            var accountList = dataAccess.GetAccountMaster(true).Where(x => x.Enable && x.PostEnable);

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

        private void button履歴再取得_Click(object sender, EventArgs e)
        {
            FillDebugControls_TweetHistory();
        }

        private void textBoxSearchHistoryAccountId_TextChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            UpdateTweetHistoryFilter();
        }

        private void buttonものまね_Click(object sender, EventArgs e)
        {
            /*
            //            string path_tmp_account = SanitizeFilename(s.Replace("@", "").Trim());
            string path_tmp_account = "test";

            // search_tweet3.exe プロセスを開始
            ProcessStartInfo startInfo = new ProcessStartInfo
            {
                CreateNoWindow = true,  // ウィンドウを表示しない
                UseShellExecute = false,  // シェルを使用しない
                FileName = "python\search_tweet3.exe",
                RedirectStandardError = true,
                Arguments = $"\"{path_tmp_account}\" \"C:\Users\sound\Desktop\test\" \"{item.プロキシURL}\" \"{item.DMMID}\""
            };

            using (Process process = new Process { StartInfo = startInfo })
            {
                process.Start();  // プロセスを開始
                string error = process.StandardError.ReadToEnd();
                process.WaitForExit();  // プロセスの終了を待つ
                int exitCode = process.ExitCode;
                if (exitCode != 0)
                {
                    try
                    {
                        string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                        string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                        // ファイルにテキストを書き込む
                        using (var writer = File.AppendText(filePath))
                        {
                            writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "のモノマネ投稿でエラーです。" + error);
                        }
                    }
                    catch { }
                }
            }


            TweetTask tweetTask = new TweetTask(DbConnection, AppendLog);
            tweetTask.TweetProc(TweetProcTypes.MONOMANE, 0, 1, 0, GetTweetId());

//            _tweetTask.TweetProc()
            */
        }


    }
}