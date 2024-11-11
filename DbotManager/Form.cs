using DbotManager.Table;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;

namespace DbotManager
{
    public partial class Form : System.Windows.Forms.Form
    {
        private MySqlDataAccess dataAccess;

        private bool _isLoading = true;

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
            dataAccess = new MySqlDataAccess("localhost", "d_bot", "root", "abcd1234");
        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            FillControls();
            _isLoading = false;
        }

        #region DataGridView
        #endregion

        #region FillControls
        private void FillControls()
        {
            FillControls_TweetHistory();
            FillControls_UserName();
            FillControls_AccountMaster();
            FillControls_CommentMaster();
        }

        private void FillControls_TweetHistory()
        {
            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistory();

            if (tweetHistoryList != null)
            {
                dataGridViewTweetHistory.DataSource = tweetHistoryList;
            }
            else
            {
                MessageBox.Show("データを取得できませんでした。");
            }
        }

        private void FillControls_AccountMaster()
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

        private void FillControls_CommentMaster()
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

        private void FillControls_UserName()
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
        private void buttonいいね_Click(object sender, EventArgs e)
        {

        }

        private void buttonブックマーク_Click(object sender, EventArgs e)
        {

        }

        private void buttonコメント_Click(object sender, EventArgs e)
        {
            TweetProc(TweetProcTypes.TWEET);
        }

        #endregion

        #region その他イベント

        private void comboBoxUserMaster_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            FillControls_AccountMaster();
            FillControls_CommentMaster();
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

        #endregion

        #region pythonスクリプト

        private void TweetProc(TweetProcTypes tweetProcType)
        {
            int userId = GetUserId();
            int accountId = GetAccountId();
            int commentId = GetCommentId();

            // Pythonスクリプトのパスを指定
            string pythonScriptPath = @"python\tweet.py";

            switch(tweetProcType)
            {
                case TweetProcTypes.TWEET:
                    pythonScriptPath += $" tweet_mode=tweet account_id={accountId} comment_id={commentId}";
                    break;
            }

            // Pythonの実行ファイルのパスを指定（通常 "python" または "python3" でOK）
            string pythonExePath = "python";

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

            /*
            // プロセスの実行
            using (Process process = new Process { StartInfo = psi })
            {



                process.Start();

                // 標準出力の取得
                string output = process.StandardOutput.ReadToEnd();
                string error = process.StandardError.ReadToEnd();

                process.WaitForExit();

                // 結果の表示
                Console.WriteLine("Output:\n" + output);
                if (!string.IsNullOrEmpty(error))
                {
                    Console.WriteLine("Error:\n" + error);
                }
            }
            */

        }

        // TextBoxにログを表示するメソッド
        private void AppendLog(string message)
        {
            if (message != null)
            {
                textBoxLog.Invoke((MethodInvoker)(() => textBoxLog.AppendText(message + Environment.NewLine)));
            }
        }

        #endregion

    }
}
