using DbotManager.Table;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Data.Common;
using System.Diagnostics;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace DbotManager
{
    public partial class AccountDialog : System.Windows.Forms.Form
    {
        #region PrivateMemory

        private bool _isLoading = true;

        private MySqlDataAccess dataAccess;

        private DbConnectionInfo dbConnection;

        private int _userId = 0;
        private int _accountId = 0;

        #endregion

        #region 初期化
        public AccountDialog(DbConnectionInfo dbConnection)
        {
            InitializeComponent();

            this.dbConnection = dbConnection;
        }

        private void AccountDialog_Load(object sender, EventArgs e)
        {
            // MySQLデータアクセスの初期化
            dataAccess = new MySqlDataAccess(this.dbConnection);

            /*
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
             
             * */

            FillDebugControls_UserName();

            UpdateInfo(GetUserId());

            FillControl_AccountInfo();

            _isLoading = false;
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

        private void FillControl_AccountInfo()
        {
            if (dataGridViewAccount.CurrentCell != null)
            {
                var accountId = dataGridViewAccount.CurrentRow.Cells[AccountMaster_Id.Name].Value.ToString();
                _accountId = int.Parse(accountId);

                var userId = dataGridViewAccount.CurrentRow.Cells[AccountMaster_UserId.Name].Value.ToString();
                _userId = int.Parse(userId);

                textBoxName.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_Name.Name].Value.ToString();
                textBoxLogInId.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_LoginId.Name].Value.ToString();
                textBoxLogInPass.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_LoginPass.Name].Value.ToString();
                textBoxApiKey.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_ApiKey.Name].Value.ToString();
                textBoxApiKeySecret.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_ApiKeySecret.Name].Value.ToString();
                textBoxClientId.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_ClientId.Name].Value.ToString();
                textBoxClientSecret.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_ClientSecret.Name].Value.ToString();
                textBoxAccessToken.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_AccessToken.Name].Value.ToString();
                textBoxAccessTokenSecret.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_AccessTokenSecret.Name].Value.ToString();
                textBoxBearerToken.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_BearerToken.Name].Value.ToString();
                textBoxRefreshToken.Text = dataGridViewAccount.CurrentRow.Cells[AccountMaster_RefreshToken.Name].Value.ToString();

                var enable = dataGridViewAccount.CurrentRow.Cells[AccountMaster_Enable.Name] as DataGridViewCheckBoxCell;
                if (enable != null)
                {
                    checkBox有効.Checked = Convert.ToBoolean(enable.Value);
                }

                var paid = dataGridViewAccount.CurrentRow.Cells[AccountMaster_Paid.Name] as DataGridViewCheckBoxCell;
                if (paid != null)
                {
                    checkBox有料アカウント.Checked = Convert.ToBoolean(paid.Value);
                }

                var like = dataGridViewAccount.CurrentRow.Cells[AccountMaster_Like.Name] as DataGridViewCheckBoxCell;
                if (like != null)
                {
                    checkBoxいいね.Checked = Convert.ToBoolean(like.Value);
                }

                var bookmark = dataGridViewAccount.CurrentRow.Cells[AccountMaster_Bookmark.Name] as DataGridViewCheckBoxCell;
                if (bookmark != null)
                {
                    checkBoxブックマーク.Checked = Convert.ToBoolean(bookmark.Value);
                }

                var reply = dataGridViewAccount.CurrentRow.Cells[AccountMaster_Reply.Name] as DataGridViewCheckBoxCell;
                if (reply != null)
                {
                    checkBoxリプライ.Checked = Convert.ToBoolean(reply.Value);
                }

                var tweet = dataGridViewAccount.CurrentRow.Cells[AccountMaster_Tweet.Name] as DataGridViewCheckBoxCell;
                if (tweet != null)
                {
                    checkBoxツイート.Checked = Convert.ToBoolean(tweet.Value);
                }

                // データグリッドビューの選択変更時にダイアログを更新
                if (_commentDialog != null && !_commentDialog.IsDisposed)
                {
                    var selectedRow = dataGridViewAccount.CurrentRow;
                    if (selectedRow != null)
                    {
                        _commentDialog.UpdateInfo(_accountId);
                    }
                }

            }
        }

        #endregion

        #region イベント


        private void dataGridViewAccount_CellClick(object sender, DataGridViewCellEventArgs e)
        {
            FillControl_AccountInfo();
        }

        private void dataGridViewAccount_SelectionChanged(object sender, EventArgs e)
        {
        }


        private void buttonアカウント削除_Click(object sender, EventArgs e)
        {
            dataAccess.DeleteAccountMaster(_accountId);
            UpdateInfo(GetUserId());
        }

        private void buttonアカウント追加_Click(object sender, EventArgs e)
        {
            AccountMaster accountMaster = new AccountMaster()
            {
                UserId = GetUserId(),
                Name = textBoxName.Text,
                LoginId = textBoxLogInId.Text,
                LoginPass = textBoxLogInPass.Text,
                ApiKey = textBoxApiKey.Text,
                ApiKeySecret = textBoxApiKeySecret.Text,
                ClientId = textBoxClientId.Text,
                ClientSecret = textBoxClientSecret.Text,
                AccessToken = textBoxAccessToken.Text,
                AccessTokenSecret = textBoxAccessTokenSecret.Text,
                BearerToken = textBoxBearerToken.Text,
                RefreshToken = textBoxRefreshToken.Text,
                Enable = checkBox有効.Checked,
                Paid = checkBox有料アカウント.Checked,
                LikeEnable = checkBoxいいね.Checked,
                BookMarkEnable = checkBoxブックマーク.Checked,
                ReplyEnable = checkBoxリプライ.Checked,
                TweetEnable = checkBoxツイート.Checked,
                Reserve1Enable = false,
                Reserve1Count = 0,
                Reserve1StartHour = 0,
                Reserve1EndHour = 0,
                Reserve2Enable = false,
                Reserve2Count = 0,
                Reserve2StartHour = 0,
                Reserve2EndHour = 0,
                Reserve3Enable = false,
                Reserve3Count = 0,
                Reserve3StartHour = 0,
                Reserve3EndHour = 0,
                Reserve4Enable = false,
                Reserve4Count = 0,
                Reserve4StartHour = 0,
                Reserve4EndHour = 0,
            };

            dataAccess.InsertAccountMaster(accountMaster);
            UpdateInfo(GetUserId() , _accountId);



//            dataGridViewAccount.Rows[1].Selected = true;

            /*

            foreach (DataGridViewRow row in dataGridViewAccount.Rows)
            {
                // 行が新規行ではない場合にのみチェック
                if (!row.IsNewRow && row.Cells[AccountMaster_Id.Name].Value?.Equals(_accountId) == true)
                {
                    row.Selected = true; // 行を選択状態にする
                }
                else
                {
                    row.Selected = false; // 一致しない行は選択を解除
                }
            }
            */
        }

        private void buttonアカウント保存_Click(object sender, EventArgs e)
        {
            AccountMaster accountMaster = new AccountMaster()
            {
                Id = _accountId,
                UserId = GetUserId(),
                Name = textBoxName.Text,
                LoginId = textBoxLogInId.Text,
                LoginPass = textBoxLogInPass.Text,
                ApiKey = textBoxApiKey.Text,
                ApiKeySecret = textBoxApiKeySecret.Text,
                ClientId = textBoxClientId.Text,
                ClientSecret = textBoxClientSecret.Text,
                AccessToken = textBoxAccessToken.Text,
                AccessTokenSecret = textBoxAccessTokenSecret.Text,
                BearerToken = textBoxBearerToken.Text,
                RefreshToken = textBoxRefreshToken.Text,
                Enable = checkBox有効.Checked,
                Paid = checkBox有料アカウント.Checked,
                LikeEnable = checkBoxいいね.Checked,
                BookMarkEnable = checkBoxブックマーク.Checked,
                ReplyEnable = checkBoxリプライ.Checked,
                TweetEnable = checkBoxツイート.Checked,
                Reserve1Enable = false,
                Reserve1Count = 0,
                Reserve1StartHour = 0,
                Reserve1EndHour = 0,
                Reserve2Enable = false,
                Reserve2Count = 0,
                Reserve2StartHour = 0,
                Reserve2EndHour = 0,
                Reserve3Enable = false,
                Reserve3Count = 0,
                Reserve3StartHour = 0,
                Reserve3EndHour = 0,
                Reserve4Enable = false,
                Reserve4Count = 0,
                Reserve4StartHour = 0,
                Reserve4EndHour = 0,
            };

            dataAccess.UpdateAccountMaster(accountMaster);
            UpdateInfo(GetUserId() , _accountId);
            SupportUtil.SelectRowsByColumnValue(dataGridViewAccount, AccountMaster_Id.Name, _accountId);

        }

        private void buttonExe_Click(object sender, EventArgs e)
        {
            /*
            int userId = _userId;
            int accountId = _accountId;
            int commentId = _commentId;
            string tweetId = GetTweetId(true);

            TweetTask _tweetTask = new TweetTask(dbConnection);
            _tweetTask.TweetProc(TweetProcTypes.TWEET, userId, accountId, commentId, tweetId);
            */
        }

        private void buttonClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void buttonGetAccessToken_Click(object sender, EventArgs e)
        {
            TweetTask tweetTask = new TweetTask(dbConnection, AppendLog);
            string command = tweetTask.GetTweetCommand(TweetProcTypes.GET_ACCESSTOKEN, _userId, _accountId, 0, GetTweetId(true));

            // クリップボードに文字列を設定
            Clipboard.SetText(command);
            MessageBox.Show("コマンドプロンプトに貼り付け操作を行って実行してください", "確認");
            Process.Start("cmd.exe"); // "/k" はコマンド実行後もウィンドウを開いたままにする
        }

        private void buttonGetBearerToken_Click(object sender, EventArgs e)
        {
            TweetTask tweetTask = new TweetTask(dbConnection, AppendLog);
            string command = tweetTask.GetTweetCommand(TweetProcTypes.GET_REFRESHTOKEN, _userId, _accountId, 0, GetTweetId(true));

            // クリップボードに文字列を設定
            Clipboard.SetText(command);
            MessageBox.Show("コマンドプロンプトに貼り付け操作を行って実行してください", "確認");
            Process.Start("cmd.exe"); // "/k" はコマンド実行後もウィンドウを開いたままにする
        }

        private void comboBoxUserMaster_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            UpdateInfo(GetUserId());
        }

        private void button再取得_Click(object sender, EventArgs e)
        {
            UpdateInfo(GetUserId() , _accountId);
//            FillControl_AccountInfo();
        }

        #endregion

        #region 画面更新
        public void UpdateInfo(int userId , int account_id = 0)
        {
            _userId = userId;

            var accountMasterList = dataAccess.GetAccountMaster().Where(x => x.UserId == userId).ToList();
            dataGridViewAccount.DataSource = accountMasterList;

            if (account_id != 0)
            {
                SupportUtil.SelectRowsByColumnValue(dataGridViewAccount, AccountMaster_Id.Name, account_id);
            }

            var name = dataAccess.GetUserNames().Where(x => x.Id == userId).FirstOrDefault().Name;
            this.Text = $"{name} の アカウント一覧";

        }

        private int GetUserId()
        {
            return (int)comboBoxUserMaster.SelectedValue;
        }


        #endregion



        private string GetTweetId(bool debug_mode = false)
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

        private void buttonいいね_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = _accountId;
            string tweetId = GetTweetId(true);

            TweetTask tweetTask = new TweetTask(dbConnection, AppendLog);
            tweetTask.TweetProc(TweetProcTypes.LIKE, userId, accountId, 0, tweetId);
        }

        private void buttonブックマーク_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = _accountId;
            string tweetId = GetTweetId(true);

            TweetTask tweetTask = new TweetTask(dbConnection, AppendLog);
            tweetTask.TweetProc(TweetProcTypes.BOOKMARK, userId, accountId, 0, tweetId);
        }

        private void buttonリプライ_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = _accountId;
            string tweetId = GetTweetId(true);

            TweetTask tweetTask = new TweetTask(dbConnection , AppendLog);
            tweetTask.TweetProc(TweetProcTypes.RETWEET, userId, accountId, 0, tweetId);
        }


        private CommentDialog _commentDialog;

        private void buttonコメント編集_Click(object sender, EventArgs e)
        {
            // ダイアログが未作成または破棄されている場合に新しいダイアログを作成
            if (_commentDialog == null || _commentDialog.IsDisposed)
            {
                _commentDialog = new CommentDialog(dbConnection);
                _commentDialog.Show();
                _commentDialog.UpdateInfo(_accountId);
            }
            else
            {
                // 既に開いている場合はフォーカスを移動
                _commentDialog.Focus();
            }
        }

        // TextBoxにログを表示するメソッド
        private void AppendLog(string message)
        {
            if (message != null)
            {
                textBoxRenew.Invoke((MethodInvoker)(() =>
                    textBoxRenew.AppendText(message + Environment.NewLine)
                ));

                // 必要に応じてログファイルにも書き込む
                SupportUtil.SaveLogToFile(message, textBoxRenew);
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
    }
}
