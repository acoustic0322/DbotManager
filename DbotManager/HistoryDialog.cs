using DbotManager.Table;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Data.Common;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace DbotManager
{
    public partial class HistoryDialog : System.Windows.Forms.Form
    {
        private MySqlDataAccess dataAccess;

        private bool _isLoading = true;

        List<TweetHistory> _tweetHistoryList = new List<TweetHistory>();

        public HistoryDialog(DbConnectionInfo dbConnection)
        {
            InitializeComponent();

            // MySQLデータアクセスの初期化
            dataAccess = new MySqlDataAccess(dbConnection);
        }

        private void HistoryDialog_Load(object sender, EventArgs e)
        {
            this.WindowState = FormWindowState.Maximized;

            UpdateControl_Master();

            _isLoading = false;

        }

        private void UpdateControl_Master()
        {
            FillDebugControls_UserName();
            FillDebugControls_AccountName();
        }

        private void FillDebugControls_UserName()
        {
            List<UserMaster> userList = dataAccess.GetUserMaster();

            if (userList != null)
            {
                comboBoxUserMaster.DataSource = userList;
                comboBoxUserMaster.DisplayMember = "DisplayText"; // コンボボックスに表示するプロパティ
                comboBoxUserMaster.ValueMember = "Id";     // 選択されたときに取得するプロパティ
            }
            else
            {
                MessageBox.Show("ユーザー名を取得できませんでした。");
            }
        }

        private void FillDebugControls_AccountName()
        {
            List<AccountMaster> accountList = dataAccess.GetAccountMaster();

            if(checkBoxUser.Checked)
            {
                accountList = accountList.Where(x => x.UserId == (int)(comboBoxUserMaster.SelectedValue)).ToList();
            }

            if (accountList != null)
            {
                comboBoxAccount.DataSource = accountList;
                comboBoxAccount.DisplayMember = "DisplayText"; // コンボボックスに表示するプロパティ
                comboBoxAccount.ValueMember = "Id";     // 選択されたときに取得するプロパティ
            }
            else
            {
                MessageBox.Show("ユーザー名を取得できませんでした。");
            }
        }

        private void Search()
        {
            _tweetHistoryList = dataAccess.GetTweetHistoryView().Where(x => x.UpdateTime >= DateTime.Today.AddDays(-1)).ToList();
            UpdateTweetHistoryFilter();
        }


        private void UpdateTweetHistoryFilter()
        {
            if (_tweetHistoryList != null)
            {

                List<TweetHistory> dspHistoryList = new List<TweetHistory>();

                dspHistoryList.AddRange(_tweetHistoryList);

                if (checkBoxUser.Checked) dspHistoryList = dspHistoryList.Where(x => x.UserId == (int)comboBoxUserMaster.SelectedValue).ToList();
                if (checkBoxAccount.Checked) dspHistoryList = dspHistoryList.Where(x => x.AccountId == (int)comboBoxAccount.SelectedValue).ToList();



                // 匿名型で表示用データを作成（表示したい列だけ）
                var displayList = dspHistoryList.Select(x => new
                {
                    日時 = ((DateTime)x.UpdateTime).ToString("MM/dd HH:mm:ss"),
                    ユーザー名 = x.UserName,
                    アカウント名 = $"{x.AccountName}({x.AccountId})",
                    モード = GetModeName(x.Mode),
                    結果 = x.Result ? "" : "×",
                    ポスト内容 = x.Comment,
                    LOG = x.ErrorLog,
                }).ToList();


                dataGridViewTweetHistory.DataSource = displayList;

                /*
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
                */

            }
            else
            {
                MessageBox.Show("データを取得できませんでした。");
            }

        }

        private string GetModeName(TweetProcTypes mode)
        {
            string ret = "";
            switch(mode)
            {
                case TweetProcTypes.LIKE:
                    ret = "いいね";
                    break;
                case TweetProcTypes.POST:
                    ret = "ポスト";
                    break;
                case TweetProcTypes.CHECKREP:
                    ret = "リプ監視";
                    break;
                case TweetProcTypes.CHECK:
                    ret = "監視";
                    break;
                case TweetProcTypes.UNFOLLOW:
                    ret = "フォロー解除";
                    break;
                case TweetProcTypes.BOOKMARK:
                    ret = "ブックマーク";
                    break;
                case TweetProcTypes.CHECKAIREP:
                    ret = "フォロー解除";
                    break;
                case TweetProcTypes.FOLLOW:
                    ret = "フォロー追加";
                    break;
                case TweetProcTypes.GET_ACCESSTOKEN:
                    ret = "AccessToken取得";
                    break;
                case TweetProcTypes.GET_REFRESHTOKEN:
                    ret = "RefreshToken取得";
                    break;
                case TweetProcTypes.JAP_LIKE:
                    ret = "JAPいいね";
                    break;
                case TweetProcTypes.MONOMANE:
                    ret = "モノマネ監視";
                    break;
                case TweetProcTypes.REPLY:
                    ret = "リプライ";
                    break;
                case TweetProcTypes.REPOST:
                    ret = "リポスト";
                    break;

            }

            return ret;
        }

        private void buttonSearch_Click(object sender, EventArgs e)
        {
            Search();

        }

        private void comboBoxUserMaster_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            checkBoxUser.Checked = true;
            FillDebugControls_AccountName();
        }

        private void comboBoxAccount_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            checkBoxAccount.Checked = true;

        }
        private void checkBoxUser_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
//            FillDebugControls_AccountName();
        }

        private void checkBoxAccount_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

        }

    }
}
