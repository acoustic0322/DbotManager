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

        private List<AccountMaster> _accountMasterList = new List<AccountMaster>();

        private MySqlDataAccess dataAccess;

        private DbConnectionInfo dbConnection;

        private CommentDialog _commentDialog;

        private CheckAccountDialog _checkAccountDialog;

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
            ReadAccountMaster(GetUserId());
            _isLoading = false;
            dataGridViewAccount_SelectionChanged(sender, e);
        }

        #endregion

        #region 処理

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

        private void FillControl_AccountInfo(int accountId)
        {
            var accountMaster = _accountMasterList.Where(x => x.Id == accountId).FirstOrDefault();
            textBoxAccountID.Text = accountId.ToString();

            textBoxName.Text = accountMaster.Name;
            textBoxLogInId.Text = accountMaster.LoginId;
            textBoxLogInPass.Text = accountMaster.LoginPass;
            textBoxApiKey.Text = accountMaster.ApiKey;
            textBoxApiKeySecret.Text = accountMaster.ApiKeySecret;
            textBoxClientId.Text = accountMaster.ClientId;
            textBoxClientSecret.Text = accountMaster.ClientSecret;
            textBoxAccessToken.Text = accountMaster.AccessToken;
            textBoxAccessTokenSecret.Text = accountMaster.AccessTokenSecret;
            textBoxBearerToken.Text = accountMaster.BearerToken;
            textBoxRefreshToken.Text = accountMaster.RefreshToken;
            checkBox有効.Checked = accountMaster.Enable;
            checkBox有料.Checked = accountMaster.Paid;
            checkBoxいいね.Checked = accountMaster.LikeEnable;
            checkBoxリプライ.Checked = accountMaster.ReplyEnable;
            checkBoxブックマーク.Checked = accountMaster.BookMarkEnable;
            checkBoxリポスト.Checked = accountMaster.RepostEnable;
            checkBoxツイート.Checked = accountMaster.PostEnable;

            checkBox有料APIいいね.Checked = accountMaster.PaidLike;
            checkBox有料APIブックマーク.Checked = accountMaster.PaidBookmark;
        }

        private void ReadAccountMaster(int userId, int accountId = 0)
        {
            _isLoading = true;
            _accountMasterList = dataAccess.GetAccountMaster();
            dataGridViewAccount.DataSource = _accountMasterList.Where(x => x.UserId == userId).ToList();
            UpdateInfo(userId, accountId);
            _isLoading = false;
        }

        public void UpdateInfo(int userId, int account_id = 0)
        {
            dataGridViewAccount.DataSource = _accountMasterList.Where(x => x.UserId == userId).ToList();

            if (account_id != 0)
            {
                SupportUtil.SelectRowsByColumnValue(dataGridViewAccount, AccountMaster_Id.Name, account_id);
            }
            else
            {
                // DataGridViewの先頭行を選択
                dataGridViewAccount.ClearSelection(); // 一度選択をクリア
                if (dataGridViewAccount.Rows.Count > 1)
                    dataGridViewAccount.Rows[0].Selected = true; // 先頭行を選択
            }

            var name = dataAccess.GetUserMaster().Where(x => x.Id == userId).FirstOrDefault().Name;
            this.Text = $"{name} の アカウント一覧";

        }

        private int GetUserId()
        {
            return (int)comboBoxUserMaster.SelectedValue;
        }


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

        #endregion

        #region イベント

        private void dataGridViewAccount_SelectionChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            if (dataGridViewAccount.CurrentCell != null)
            {
                var accountId = int.Parse(dataGridViewAccount.CurrentRow.Cells[AccountMaster_Id.Name].Value.ToString());
                FillControl_AccountInfo(accountId);
            }

            // データグリッドビューの選択変更時にダイアログを更新
            if (_commentDialog != null && !_commentDialog.IsDisposed)
            {
                var selectedRow = dataGridViewAccount.CurrentRow;
                if (selectedRow != null)
                {
                    _commentDialog.UpdateInfo(0, int.Parse(textBoxAccountID.Text) , GetUserId());
                }
            }

            if (_checkAccountDialog != null && !_checkAccountDialog.IsDisposed)
            {
                var selectedRow = dataGridViewAccount.CurrentRow;
                if (selectedRow != null)
                {
                    _checkAccountDialog.UpdateInfo(0, int.Parse(textBoxAccountID.Text), GetUserId());
                }
            }
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
                Paid = checkBox有料.Checked,
                LikeEnable = checkBoxいいね.Checked,
                ReplyEnable = checkBoxリプライ.Checked,
                BookMarkEnable = checkBoxブックマーク.Checked,
                RepostEnable = checkBoxリポスト.Checked,
                PostEnable = checkBoxツイート.Checked,
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
                PaidLike = checkBox有料APIいいね.Checked,
                PaidBookmark = checkBox有料APIブックマーク.Checked,
            };

            int newId = dataAccess.InsertAccountMaster(accountMaster);
            textBoxAccountID.Text = newId.ToString();
            ReadAccountMaster(GetUserId() , newId);
        }

        private void buttonアカウント保存_Click(object sender, EventArgs e)
        {
            AccountMaster accountMaster = new AccountMaster()
            {
                Id = int.Parse(textBoxAccountID.Text),
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
                Paid = checkBox有料.Checked,
                LikeEnable = checkBoxいいね.Checked,
                ReplyEnable = checkBoxリプライ.Checked,
                BookMarkEnable = checkBoxブックマーク.Checked,
                RepostEnable = checkBoxリポスト.Checked,
                PostEnable = checkBoxツイート.Checked,
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
                PaidLike = checkBox有料APIいいね.Checked,
                PaidBookmark = checkBox有料APIブックマーク.Checked,
            };

            dataAccess.UpdateAccountMaster(accountMaster);
            ReadAccountMaster(GetUserId() , accountMaster.Id);
        }

        private void buttonアカウント削除_Click(object sender, EventArgs e)
        {
            dataAccess.DeleteAccountMaster(int.Parse(textBoxAccountID.Text));
            ReadAccountMaster(GetUserId());
        }

        private void buttonClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        private void buttonGetAccessToken_Click(object sender, EventArgs e)
        {
            TweetTask tweetTask = new TweetTask(dbConnection, AppendLog);
            string command = tweetTask.GetTweetCommand(TweetProcTypes.GET_ACCESSTOKEN, GetUserId(), int.Parse(textBoxAccountID.Text), 0, GetTweetId(true));

            // クリップボードに文字列を設定
            Clipboard.SetText(command);
            MessageBox.Show("コマンドプロンプトに貼り付け操作を行って実行してください", "確認");
            Process.Start("cmd.exe"); // "/k" はコマンド実行後もウィンドウを開いたままにする
        }

        private void buttonGetBearerToken_Click(object sender, EventArgs e)
        {
            TweetTask tweetTask = new TweetTask(dbConnection, AppendLog);
            string command = tweetTask.GetTweetCommand(TweetProcTypes.GET_REFRESHTOKEN, GetUserId(), int.Parse(textBoxAccountID.Text), 0, GetTweetId(true));

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
            ReadAccountMaster(GetUserId(), int.Parse(textBoxAccountID.Text));
            FillControl_AccountInfo(int.Parse(textBoxAccountID.Text));
        }

        private void buttonいいね_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = int.Parse(textBoxAccountID.Text);
            string tweetId = GetTweetId(true);

            TweetTask tweetTask = new TweetTask(dbConnection, AppendLog);
            tweetTask.TweetProc(TweetProcTypes.LIKE, userId, accountId, 0, tweetId);
        }

        private void buttonブックマーク_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = int.Parse(textBoxAccountID.Text); ;
            string tweetId = GetTweetId(true);

            TweetTask tweetTask = new TweetTask(dbConnection, AppendLog);
            tweetTask.TweetProc(TweetProcTypes.BOOKMARK, userId, accountId, 0, tweetId);
        }

        private void buttonリプライ_Debug_Click(object sender, EventArgs e)
        {
            int userId = GetUserId();
            int accountId = int.Parse(textBoxAccountID.Text); ;
            string tweetId = GetTweetId(true);

            TweetTask tweetTask = new TweetTask(dbConnection, AppendLog);
            tweetTask.TweetProc(TweetProcTypes.REPOST, userId, accountId, 0, tweetId);
        }

        private void buttonコメント編集_Click(object sender, EventArgs e)
        {
            // ダイアログが未作成または破棄されている場合に新しいダイアログを作成
            if (_commentDialog == null || _commentDialog.IsDisposed)
            {
                _commentDialog = new CommentDialog(dbConnection);
                _commentDialog.Show();
                _commentDialog.UpdateInfo(0 ,int.Parse(textBoxAccountID.Text) , GetUserId());
            }
            else
            {
                // 既に開いている場合はフォーカスを移動
                _commentDialog.Focus();
            }
        }
        #endregion

        private void button監視設定_Click(object sender, EventArgs e)
        {
            // ダイアログが未作成または破棄されている場合に新しいダイアログを作成
            if (_checkAccountDialog == null || _checkAccountDialog.IsDisposed)
            {
                _checkAccountDialog = new CheckAccountDialog(dbConnection);
                _checkAccountDialog.Show();
                _checkAccountDialog.UpdateInfo(0, int.Parse(textBoxAccountID.Text), GetUserId());
            }
            else
            {
                // 既に開いている場合はフォーカスを移動
                _checkAccountDialog.Focus();
            }
        }
    }
}
