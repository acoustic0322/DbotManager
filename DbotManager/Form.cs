using DbotManager.Table;
using System;
using System.Collections.Generic;
using System.ComponentModel;
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

        private enum TweetProcTypes
        {
            LIKE,
            BOOKMARK,
            TWEET
        }

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

            TweetProc(TweetProcTypes.LIKE, userId, accountId, commentId, tweetId);
        }

        private void buttonブックマーク_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = GetAccountId();
            int commentId = GetCommentId();
            string tweetId = GetTweetId(true);

            TweetProc(TweetProcTypes.BOOKMARK, userId, accountId, commentId, tweetId);
        }

        private void buttonコメント_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = GetAccountId();
            int commentId = GetCommentId();
            string tweetId = GetTweetId(true);

            TweetProc(TweetProcTypes.TWEET, userId, accountId, commentId, tweetId);
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

        #region pythonスクリプト

        private void TweetProc(TweetProcTypes tweetProcType, int userId, int accountId, int commentId, string tweetId)
        {


            // Pythonスクリプトのパスを指定
            string pythonScriptPath = @"python\tweet.py";

            switch (tweetProcType)
            {
                case TweetProcTypes.TWEET:
                    pythonScriptPath += $" tweet_mode=tweet account_id={accountId} comment_id={commentId}";
                    break;
                case TweetProcTypes.LIKE:
                    pythonScriptPath += $" tweet_mode=like account_id={accountId} tweet_id={tweetId}";
                    break;
                case TweetProcTypes.BOOKMARK:
                    pythonScriptPath += $" tweet_mode=bookmark account_id={accountId} tweet_id={tweetId}";
                    break;
            }

            // Pythonの実行ファイルのパスを指定（通常 "python" または "python3" でOK）
            string pythonExePath = "python";

            MakeFolder(pythonExePath);

            // プロセス情報の設定
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = pythonExePath,
                Arguments = pythonScriptPath,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using (Process process = new Process())
            {
                process.StartInfo = psi;

                // Pythonの標準出力と標準エラーを取得して、TextBoxに出力
                process.OutputDataReceived += (s, ea) => AppendLog(ea.Data);
                process.ErrorDataReceived += (s, ea) => AppendLog("ERROR: " + ea.Data);

                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();

                // タイムアウトを設定して待機（例えば5秒）
                bool exited = process.WaitForExit(5000);
                if (!exited)
                {
                    AppendLog("タイムアウト: プロセスが5秒以内に終了しませんでした");
                    process.Kill(); // 必要に応じてプロセスを強制終了
                }

                //                process.WaitForExit();
            }
        }

        // TextBoxにログを表示するメソッド
        private void AppendLog(string message)
        {
            if (message != null)
            {
                textBoxLog.Invoke((MethodInvoker)(() =>
                    textBoxLog.AppendText(message + Environment.NewLine)
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
                textBoxLog.Invoke((MethodInvoker)(() => textBoxLog.AppendText("ログの書き込みに失敗しました: " + ex.Message + Environment.NewLine)));
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

        private void buttonいいねリスト作成_Click(object sender, EventArgs e)
        {
            if (radioButtonいいね件数50.Checked) _tweetTask.件数 = 50;
            else if (radioButtonいいね件数100.Checked) _tweetTask.件数 = 100;
            else if (radioButtonいいね件数200.Checked) _tweetTask.件数 = 200;
            else _tweetTask.件数 = int.Parse(textBoxいいね件数.Text);
            _tweetTask.制限時間以内に履歴ありの無料アカウントを排除 = checkBox_15分以内に履歴のある無料アカウントを除外する.Checked;
            _tweetTask.TargetTweetID = GetTweetId();
            _tweetTask.InitAccountList();
            dataGridViewいいねリスト.DataSource = _tweetTask.TweetAccountList;

        }

        private void buttonいいねブックマーク実行_Click(object sender, EventArgs e)
        {
            _tweetTask.StartTask();
        }

        #endregion

        private void buttonクリアlog_Click(object sender, EventArgs e)
        {
            textBoxLog.Text = string.Empty;
        }

        private void buttonDebugGetBearerToken_Click(object sender, EventArgs e)
        {
            _tweetTask.StartTask(TweetTask.TweetProcTypes.GET_REFRESHTOKEN, GetUserId(), GetAccountId(), GetCommentId(), GetTweetId(true));
        }

        private void buttonDebugGetAccessToken_Click(object sender, EventArgs e)
        {
            _tweetTask.StartTask(TweetTask.TweetProcTypes.GET_ACCESSTOKEN, GetUserId(), GetAccountId(), GetCommentId(), GetTweetId(true));
        }
    }
}