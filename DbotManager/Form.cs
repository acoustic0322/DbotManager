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
using System.Timers;

namespace DbotManager
{

    public partial class Form : System.Windows.Forms.Form
    {
        TweetTask _tweetTask;
        DiscordTask _discordTask;
        ReserveTask _reserveTask;

        public DbConnectionInfo DbConnection = new DbConnectionInfo();

        private MySqlDataAccess dataAccess;

        private bool _isLoading = true;

        private WebCommand _webCommand;

        List<TweetHistory> _tweetHistoryList;

        private enum 処理モードTypes
        {
            一括処理,
            監視_予約ツイート
        }

        private  処理モードTypes 処理モードType { get; set; }


        public Form(string[] args)
        {
            InitializeComponent();


            DbConnection.MachineName = "203.137.53.205";
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
            _reserveTask = new ReserveTask(DbConnection, AppendLog);
            _discordTask = new DiscordTask();
            _discordTask.StartTask();

            var col = dataGridView監視.Columns[SearchList_LastPostTime.Name];
            col.DefaultCellStyle.Format = "yyyy/MM/dd HH:mm:ss";
            col = dataGridViewReserveSchedule.Columns[dataGridViewReserveSchedule_ReserveTime.Name];
            col.DefaultCellStyle.Format = "yyyy/MM/dd HH:mm:ss";

            var col2 = dataGridView監視.Columns[SearchList_LastReplyTime.Name];
            col2.DefaultCellStyle.Format = "yyyy/MM/dd HH:mm:ss";
            col2 = dataGridViewReserveSchedule.Columns[dataGridViewReserveSchedule_ReserveTime.Name];
            col2.DefaultCellStyle.Format = "yyyy/MM/dd HH:mm:ss";

            var col3 = dataGridView監視.Columns[SearchList_CheckDate.Name];
            col3.DefaultCellStyle.Format = "HH:mm:ss";
            col3 = dataGridViewReserveSchedule.Columns[dataGridViewReserveSchedule_ReserveTime.Name];
            col3.DefaultCellStyle.Format = "HH:mm:ss";

            FillControls();

            if (処理モードType == 処理モードTypes.一括処理)
            {
                checkBoxWeb一括処理.Checked = true;

                // 予約タブ削除
                HideTab(2);

                // 履歴タブ削除
                HideTab(1);

                this.Text += "(一括処理)";
            }
            else
            {
                // 一括処理タブ削除
                HideTab(0);

                // 予約ポストの自動開始
                button予約作成_Click(sender, e);
                button予約Start_Click(sender, e);

                // 監視モードの自動開始
                button監視Start_Click(sender, e);

                this.Text += "(監視・予約ポスト)";
            }


            _isLoading = false;
        }

        // 非表示にしたいタブを保持するための変数
        TabPage hiddenTabPage;

        // タブを非表示にする
        private void HideTab(int index)
        {
            if (tabControl.TabPages.Count > index)
            {
                hiddenTabPage = tabControl.TabPages[index];
                tabControl.TabPages.RemoveAt(index);
            }
        }

        // 非表示にしたタブを再表示する
        private void ShowTab(int index)
        {
            if (hiddenTabPage != null && !tabControl.TabPages.Contains(hiddenTabPage))
            {
                tabControl.TabPages.Insert(index, hiddenTabPage);
                hiddenTabPage = null; // 再表示後はクリア
            }
        }

        private void Form_FormClosing(object sender, FormClosingEventArgs e)
        {
            SaveIniファイル();
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

            ReadIniファイル();
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

                MakeList_一括処理(
                    checkBoxいいね.Checked, checkBoxいいね.Checked ? int.Parse(textBoxいいね件数.Text) : 0,
                    checkBoxリプライ.Checked, checkBoxリプライ.Checked ? int.Parse(textBoxリプライ件数.Text) : 0,
                    checkBoxRepToRep.Checked,
                    checkBoxブックマーク.Checked, checkBoxブックマーク.Checked ? int.Parse(textBoxブックマーク件数.Text) : 0,
                    checkBoxリポスト.Checked, checkBoxリポスト.Checked ? int.Parse(textBoxリポスト件数.Text) : 0,
                    checkBox_15分以内に履歴のある無料アカウントを除外する.Checked,
                    checkBoxUserID.Checked ? int.Parse(comboBoxUserMaster.SelectedValue.ToString()) : 0,
                    checkBoxDuplicate.Checked ,
                    GetTweetId(textBoxUrlTweetID.Text)        
                );

                Exe一括処理();
                this.Close();
            }
        }

        private void FillDebugControls_TweetHistory()
        {
            _tweetHistoryList = dataAccess.GetTweetHistoryView().Where(x => x.UpdateTime >= DateTime.Today.AddDays(-3)).ToList();
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
            List<AccountMaster> acciuntList = dataAccess.GetAccountMaster().Where(x => x.Paid).ToList();

            if (acciuntList != null)
            {
                comboBox監視実施アカウント.DataSource = acciuntList;
                comboBox監視実施アカウント.DisplayMember = "Name"; // コンボボックスに表示するプロパティ
                comboBox監視実施アカウント.ValueMember = "Id";     // 選択されたときに取得するプロパティ
            }
            else
            {
                MessageBox.Show("アカウント名を取得できませんでした。");
            }
        }

        private void FillDebugControls_UserName()
        {
            List<UserMaster> userList = dataAccess.GetUserMaster();

            if (userList != null)
            {
                comboBoxUserMaster.DataSource = userList;
                comboBoxUserMaster.DisplayMember = "Name"; // コンボボックスに表示するプロパティ
                comboBoxUserMaster.ValueMember = "Id";     // 選択されたときに取得するプロパティ

                comboBox監視UserMaster.DataSource = userList;
                comboBox監視UserMaster.DisplayMember = "Name"; // コンボボックスに表示するプロパティ
                comboBox監視UserMaster.ValueMember = "Id";     // 選択されたときに取得するプロパティ
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

        private class 監視アカウントInfo
        {
            public string CheckAccountName { get; set; }
            public string ExeAccountName { get; set; }
            public DateTime? SinceDatetime { get; set; }
        }


        private void buttonMakeList_Click(object sender, EventArgs e)
        {

            MakeList_一括処理(
                checkBoxいいね.Checked, checkBoxいいね.Checked ? int.Parse(textBoxいいね件数.Text) : 0,
                checkBoxリプライ.Checked, checkBoxリプライ.Checked ? int.Parse(textBoxリプライ件数.Text) : 0,
                checkBoxRepToRep.Checked,
                checkBoxブックマーク.Checked, checkBoxブックマーク.Checked ? int.Parse(textBoxブックマーク件数.Text) : 0,
                checkBoxリポスト.Checked, checkBoxリポスト.Checked ? int.Parse(textBoxリポスト件数.Text) : 0,
                checkBox_15分以内に履歴のある無料アカウントを除外する.Checked,
                checkBoxUserID.Checked ? int.Parse(comboBoxUserMaster.SelectedValue.ToString()) : 0,
                checkBoxDuplicate.Checked,
                GetTweetId(textBoxUrlTweetID.Text),
                true,
                checkBox一括処理禁止権限無視.Checked
            );
        }

        private void buttonExeList_Click(object sender, EventArgs e)
        {
            Exe一括処理();

            TweetProcessList followItem = new TweetProcessList()
            {
                TargetAccountName = textBox対象アカウント名.Text,
                ExeFollow = checkBoxFollow.Checked,
                ExeUnFollow = checkBoxUnFollow.Checked,
                UserId = checkBoxUserID.Checked ? int.Parse(comboBoxUserMaster.SelectedValue.ToString()) : 0
            };

            ExeFollow処理(followItem);

            if(checkBoxJAPいいね.Checked)
            {
                TweetTask task = new TweetTask(DbConnection, AppendLog);
                task.Exe_JAPいいね(
                    GetTweetName(textBoxUrlTweetID.Text),
                    GetTweetId(textBoxUrlTweetID.Text),
                    int.Parse(textBoxJAPいいね件数.Text.ToString())
                   
                    );
            }
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

        private string GetTweetId(string input)
        {
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

        private string GetTweetName(string input)
        {

            // 正規表現でユーザー名を抽出
            Match match = Regex.Match(input, @"x\.com/([^/]+)/status");

            string tweetname = string.Empty;

            if (match.Success)
            {
                tweetname = match.Groups[1].Value;
                Console.WriteLine($"Username: {tweetname}");
            }
            else
            {
                Console.WriteLine("Username not found.");
            }

            return tweetname;
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

        private void MakeList_一括処理(
            bool likeChecked, int likeCount,
            bool replyChecked, int replyCount,
            bool repToRep,
            bool bookmarkChecked, int bookmarkCount,
            bool repostChecked, int repostCount,
            bool excludeFreeAccount, int userId,
            bool duplicateChecked, string tweetId,
            bool fillControl = true,
            bool ユーザー権限無視 = false
            
            )
        {
            _tweetTask.いいね件数 = likeChecked ? likeCount : 0;
            _tweetTask.リプライ件数 = replyChecked ? replyCount : 0;
            _tweetTask.ブックマーク件数 = bookmarkChecked ? bookmarkCount : 0;
            _tweetTask.リポスト件数 = repostChecked ? repostCount : 0;

            _tweetTask.制限時間以内に履歴ありの無料アカウントを排除 = excludeFreeAccount;
            _tweetTask.TargetTweetID = tweetId;// GetTweetId();

            _tweetTask.LikeEnable = likeChecked;
            _tweetTask.ReplyEnable = replyChecked;
            _tweetTask.ReplyToRep = repToRep;
            _tweetTask.BookmarkEnable = bookmarkChecked;
            _tweetTask.RepostEnable = repostChecked;
            _tweetTask.DuplicateEnable = duplicateChecked;

            _tweetTask.UserId = userId;

            _tweetTask.Init一括処理list(ユーザー権限無視);

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

                if(fillControl)
                {
                    dataGridViewいいね.DataSource = list.OrderBy(x => x.ID).ToList();
                    labelいいね件数.Text = $"({list.Count}件)";
                }
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

                if(fillControl)
                {
                    dataGridViewリプライ.DataSource = list.OrderBy(x => x.ID).ToList();
                    labelリプライ.Text = $"({list.Count}件)";
                }
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

                if(fillControl)
                {
                    dataGridViewブックマーク.DataSource = list.OrderBy(x => x.ID).ToList();
                    labelブックマーク件数.Text = $"({list.Count}件)";

                }
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

                if(fillControl)
                {
                    dataGridViewリポスト.DataSource = list.OrderBy(x => x.ID).ToList();
                    labelリポスト件数.Text = $"({list.Count}件)";

                }
            }
        }

        private void Exe一括処理()
        {
            _tweetTask.Exe_一括処理();
        }

        private void ExeFollow処理(TweetProcessList tweetProcessList)
        {
            _tweetTask.ExeFollow処理(tweetProcessList);
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

                _discordTask.SendMessage(message);
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
            var list = _reserveTask.MakeScheduleList().OrderBy(x => x.ReserveTime).ToList();

            label予約ポスト件数.Text = $"({list.Count}件)";

            dataGridViewReserveSchedule.DataSource = list;
        }


        private void button予約Start_Click(object sender, EventArgs e)
        {
            if(_reserveTask.作成済 == false)
            {
                _reserveTask.MakeScheduleList();
            }

            _reserveTask.StartTask();

            button予約Start.Enabled = false;
            button予約End.Enabled = true;
        }

        private void button予約End_Click(object sender, EventArgs e)
        {
            _reserveTask.EndTask();

            button予約Start.Enabled = true;
            button予約End.Enabled = false;
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

        #region Web一括処理

        private static System.Timers.Timer _Web監視Timer;

        private void checkBoxWeb一括処理_CheckedChanged(object sender, EventArgs e)
        {
            if(checkBoxWeb一括処理.Checked)
            {
                StartTask_Web監視();

            }
            else
            {
                EndTask_Web監視();
            }
        }

        private void EndTask_Web監視()
        {
            _Web監視Timer.Enabled = false;
        }

        private void StartTask_Web監視()
        {
            // タイマーを設定（1000msごと = 1秒ごと）
            _Web監視Timer = new System.Timers.Timer(5000);
            _Web監視Timer.Elapsed += (sender, e) => OnTimedEvent_監視(sender, e, null); //OnTimedEvent_監視(null,null, );
            _Web監視Timer.AutoReset = true; // 繰り返し実行
            _Web監視Timer.Enabled = true;
        }

        public void OnTimedEvent_監視(object sender, ElapsedEventArgs e, Action callback)
        {
            _Web監視Timer.Enabled = false;
            Console.WriteLine($"OnTimedEvent_監視処理を実行中: {DateTime.Now}");
            var item = dataAccess.GetTargetTweetProcess();
            if(item != null)
            {
                // 選手権モード時は各パラメータを固定
                item = UpdateSensyukenMode(item);


                MakeList_一括処理(
                    item.LikeEnable,
                    item.LikeCount,
                    item.ReplyEnable,
                    item.ReplyCount,
                    item.RepToRep,
                    item.BookmarkEnable,
                    item.BookmarkCount,
                    item.RepostEnable,
                    item.RepostCount,
                    checkBox_15分以内に履歴のある無料アカウントを除外する.Checked,
                    item.UserId,
                    item.Dumplicate,
                    ExtractNumber(item.TweetId),
                    false
                    
                );

                Exe一括処理();

                ExeFollow処理(item);

                if (item.JapLikeCount != 0)
                {
                    TweetTask task = new TweetTask(DbConnection, AppendLog);
                    task.Exe_JAPいいね(
                        GetTweetName(item.TweetId),
                        GetTweetId(item.TweetId),
                        item.JapLikeCount
                        );
                }

                item.ExeFlag = true;

                dataAccess.UpdateTweetProcess(item);
            }
            _Web監視Timer.Enabled = true;

        }

        private TweetProcessList UpdateSensyukenMode(TweetProcessList item)
        {
            switch(item.SensyukenMode)
            {
                case 0:
                    break;

                case 1:
                    item.LikeCount = 200;
                    item.LikeEnable = true;
                    item.JapLikeCount = 50;
                    item.BookmarkCount = 250;
                    item.BookmarkEnable = true;
                    item.ReplyEnable = false;
                    item.RepostEnable = false;

                    // 選手権モード時はUserアカウントは指定しない
                    item.UserId = 0;

//                    item.LikeCount = 1;
//                    item.JapLikeCount = 20;
//                    item.BookmarkCount = 20;
                    break;
            }

            return item;
        }

        #endregion

        #region 監視・モノマネ

        private void button監視Start_Click(object sender, EventArgs e)
        {
            MakeList_監視(true);

            _tweetTask.StartTask_監視();
            _tweetTask.監視完了 += On監視完了;

            button監視Start.Enabled = false;
            button監視End.Enabled = true;

            groupBox基本設定_監視.Enabled = false;
        }

        /// <summary>
        /// TweetTaskの監視処理が実行された際に呼び出されるイベント
        /// </summary>
        /// <param name="sender"></param>
        /// <param name="e"></param>
        private void On監視完了(object sender, EventArgs e)
        {
            Console.WriteLine("監視処理が完了しました。追加処理を行います。");

            var list = _tweetTask.CheckSearchList.OrderBy(x => x.CheckDate).ToList();

            // メインスレッドで UI を更新する
            if (dataGridView監視.InvokeRequired)
            {
                dataGridView監視.Invoke(new Action(() =>
                {
                    UpdateUI(list);
                }));
            }
            else
            {
                UpdateUI(list);
            }
        }

        // UI を更新する処理を別メソッドにまとめる
        private void UpdateUI(List<SearchList> list)
        {
            dataGridView監視.DataSource = list;
            label監視件数.Text = $"({list.Count}件)";
        }

        private void button監視End_Click(object sender, EventArgs e)
        {
            _tweetTask.EndTask_監視();
            button監視Start.Enabled = true;
            button監視End.Enabled = false;

            groupBox基本設定_監視.Enabled = true;
        }

        private void MakeList_監視(bool first_flag = false)
        {
            _tweetTask.CheckUserId = checkBox監視UserId.Checked ? int.Parse(comboBox監視UserMaster.SelectedValue.ToString()) : 0;
            _tweetTask.Init監視list(first_flag);

            var list = _tweetTask.CheckSearchList.OrderBy(x => x.CheckDate).ToList();
            dataGridView監視.DataSource = list;
            label監視件数.Text = $"({list.Count}件)";

        }

        private void Exe監視()
        {
            _tweetTask.Exe_一括処理();
        }

        #endregion 監視・モノマネ

        #region iniファイル

        private void SaveIniファイル()
        {
            /*
            string filePath = "config.ini";

            string account = comboBox監視実施アカウント.SelectedValue == null ? "" : comboBox監視実施アカウント.SelectedValue.ToString();

            // 複数の設定項目を保存する内容
            var iniContent = $@"
";
            // ファイルに書き込み
            File.WriteAllText(filePath, iniContent.Trim());
            */
        }

        private void ReadIniファイル()
        {
            string filePath = "config.ini";

            // ファイルを読み込み
            if (File.Exists(filePath))
            {
                var lines = File.ReadAllLines(filePath);
                var settings = new Dictionary<string, Dictionary<string, string>>();
                string currentSection = "";

                foreach (var line in lines)
                {
                    if (line.StartsWith("[") && line.EndsWith("]"))
                    {
                        currentSection = line.Trim('[', ']');
                        if (!settings.ContainsKey(currentSection))
                        {
                            settings[currentSection] = new Dictionary<string, string>();
                        }
                    }
                    else if (!string.IsNullOrWhiteSpace(line) && line.Contains('='))
                    {
                        var keyValue = line.Split(new[] { '=' }, 2);
                        if (!string.IsNullOrEmpty(currentSection) && keyValue.Length == 2)
                        {
                            settings[currentSection][keyValue[0].Trim()] = keyValue[1].Trim();
                        }
                    }
                }

                if (settings.ContainsKey("全体設定") && settings["全体設定"].ContainsKey("処理モード"))
                {
                    if (settings["全体設定"]["処理モード"] == "一括処理")
                        処理モードType = 処理モードTypes.一括処理;
                    else
                        処理モードType = 処理モードTypes.監視_予約ツイート;
                }
            }
        }


        #endregion


    }
}