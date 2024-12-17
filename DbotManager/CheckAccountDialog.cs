using DbotManager.Table;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Data.Common;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Text.RegularExpressions;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace DbotManager
{
    public partial class CheckAccountDialog : System.Windows.Forms.Form
    {
        #region PrivateMemory

        private bool _isLoading = true;

        private MySqlDataAccess dataAccess;

        private DbConnectionInfo dbConnection;

        public int AccountId { get; set; }
        public int UserId { get; set; }

        private List<CheckAccountList> _checkAccountList = new List<CheckAccountList>();
        private List<AccountMaster> _accountMasterList = new List<AccountMaster>();      

        #endregion

        #region 初期化
        public CheckAccountDialog(DbConnectionInfo dbConnection)
        {
            InitializeComponent();

            this.dbConnection = dbConnection;
        }

        private void CommentDialog_Load(object sender, EventArgs e)
        {
            // MySQLデータアクセスの初期化
            dataAccess = new MySqlDataAccess(this.dbConnection);

            ReadCheckAccountList();

            _isLoading = false;
        }

        private void ReadCheckAccountList(int checkId = 0)
        {
//            _isLoading = true;
            _checkAccountList = dataAccess.GetCheckAccountList();
            _accountMasterList = dataAccess.GetAccountMaster();

//            dataGridViewCheckAccount.DataSource = _checkAccountList.Where(x => x.AccountId == AccountId).ToList();
            UpdateInfo(true ,AccountId , UserId);
//            _isLoading = false;
        }

        #endregion

        #region イベント
        private void dataGridViewComment_SelectionChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            if (dataGridViewCheckAccount.CurrentCell != null)
            {
                var commentId = int.Parse(dataGridViewCheckAccount.CurrentRow.Cells[CommentMaster_Id.Name].Value.ToString());
                FillControl_CommentInfo(commentId);
            }
        }

        private void FillControl_CommentInfo(int commentId)
        {
            var checkAccount = _checkAccountList.Where(x => x.Id == commentId).FirstOrDefault();
            textBoxId.Text = commentId.ToString();

            checkBox有効.Checked = checkAccount.Enable;
            textBoxCheckAccount.Text = checkAccount.CheckAccount;
        }

        private void buttonコメント削除_Click(object sender, EventArgs e)
        {
            dataAccess.DeleteCommentMaster(int.Parse(textBoxId.Text));
            ReadCheckAccountList();
            //            UpdateInfo(_accountId);
        }

        private void buttonコメント追加_Click(object sender, EventArgs e)
        {
            CheckAccountList checkAccount = new CheckAccountList()
            {
                //                Id = int.Parse(textBoxCommentID.Text),
                AccountId = AccountId,
                Enable = checkBox有効.Checked,
                CheckAccount = textBoxCheckAccount.Text,
                Mode = radioButton監視.Checked ? TweetProcTypes.CHECK : (radioButton監視toReply.Checked ? TweetProcTypes.CHECKREP : TweetProcTypes.MONOMANE)
            };

            int newId = dataAccess.InsertCheckAccountList(checkAccount);
            textBoxId.Text = newId.ToString();
            ReadCheckAccountList(newId);
        }

        private void buttonコメント保存_Click(object sender, EventArgs e)
        {
            CheckAccountList checkAccount = new CheckAccountList()
            {
                Id = int.Parse(textBoxId.Text),
                //                Id = int.Parse(textBoxCommentID.Text),
                AccountId = AccountId,
                Enable = checkBox有効.Checked,
                CheckAccount = textBoxCheckAccount.Text,
                Mode = radioButton監視.Checked ? TweetProcTypes.CHECK : (radioButton監視toReply.Checked ? TweetProcTypes.CHECKREP : TweetProcTypes.MONOMANE)
            };

            dataAccess.UpdateCheckAccountList(checkAccount);
            ReadCheckAccountList(int.Parse(textBoxId.Text));
        }

        private void radioButton監視toReply_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            ReadCheckAccountList();
        }

        private void radioButton監視_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            ReadCheckAccountList();
        }

        private void radioButtonものまね_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            ReadCheckAccountList();
        }

        private void buttonExe_Click(object sender, EventArgs e)
        {
            int userId = UserId;
            int accountId = AccountId;
            int checkAccountId = int.Parse(textBoxId.Text);
            string tweetId = GetTweetId(true);

            TweetTask _tweetTask = new TweetTask(dbConnection , AppendLog);
            _tweetTask.TweetProc(radioButton監視.Checked ? TweetProcTypes.CHECK :  (radioButton監視toReply.Checked ? TweetProcTypes.CHECKREP : TweetProcTypes.MONOMANE), userId, accountId, checkAccountId, tweetId);
        }

        private void buttonClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        #endregion

        #region 画面更新
        public void UpdateInfo(bool reSelect = true, int accountId = 0 , int userId = 0)
        {
            if(accountId != 0)
            {
                var list = _checkAccountList.Where(x => x.AccountId == accountId).ToList();

                if (radioButton監視.Checked)
                {
                    list = list.Where(x => x.Mode == TweetProcTypes.CHECK).ToList();
                }
                else if(radioButton監視toReply.Checked)
                {
                    list = list.Where(x => x.Mode == TweetProcTypes.CHECKREP).ToList();
                }
                else
                {
                    list = list.Where(x => x.Mode == TweetProcTypes.MONOMANE).ToList();
                }

                dataGridViewCheckAccount.DataSource = list;

                if(reSelect)
                {
                    var id = list.FirstOrDefault().Id;
                    SupportUtil.SelectRowsByColumnValue(dataGridViewCheckAccount, CommentMaster_Id.Name, id);
                }

                var accountName = _accountMasterList.Where(x => x.Id == accountId).FirstOrDefault().Name;
                this.Text = $"{accountName} の 監視設定";

                AccountId = accountId;

                /*
                if (_mediaMasterList != null && AccountId != 0)
                {
                    comboBox画像.DataSource = _mediaMasterList.Where(x => x.AccountId == AccountId && x.MediaType == MediaTypes.Photo).ToList();
                    comboBox画像.DisplayMember = "Name"; // コンボボックスに表示するプロパティ
                    comboBox画像.ValueMember = "MediaId";     // 選択されたときに取得するプロパティ

                    comboBox動画.DataSource = _mediaMasterList.Where(x => x.AccountId == AccountId && x.MediaType == MediaTypes.Movie).ToList();
                    comboBox動画.DisplayMember = "Name"; // コンボボックスに表示するプロパティ
                    comboBox動画.ValueMember = "MediaId";     // 選択されたときに取得するプロパティ
                }
                */
            }
            else
            {
                // DataGridViewの先頭行を選択
                dataGridViewCheckAccount.ClearSelection(); // 一度選択をクリア
                if (dataGridViewCheckAccount.Rows.Count > 1)
                    dataGridViewCheckAccount.Rows[0].Selected = true; // 先頭行を選択
            }

            if(userId != 0)
            {
                UserId = userId;
            }
        }

        #endregion

        private string GetTweetId(bool debug_mode = false)
        {
            string input = textBoxUrlTweetID.Text;
            string extractedNumber = SupportUtil.ExtractNumber(input);

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
