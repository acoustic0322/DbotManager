using DbotManager.Table;
using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Data;
using System.Drawing;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using static System.Windows.Forms.VisualStyles.VisualStyleElement;

namespace DbotManager
{
    public partial class MainForm : Form
    {
        private MySqlDataAccess dataAccess;

        private bool _isLoading = true;

        public MainForm()
        {
            InitializeComponent();

            // MySQLデータアクセスの初期化
            dataAccess = new MySqlDataAccess("localhost", "d_bot", "root", "abcd1234");
        }

        private void buttonいいね_Click(object sender, EventArgs e)
        {

        }

        private void buttonブックマーク_Click(object sender, EventArgs e)
        {

        }

        private void MainForm_Load(object sender, EventArgs e)
        {
            FillControls();
            _isLoading = false;
        }

        private void FillControls()
        {
            FillControls_TweetHistory();
            FillControls_UserName();
            FillControls_AccountMaster();
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
            int userID = (int)comboBoxUserMaster.SelectedValue;

            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster().Where(x => x.UserId == userID).ToList();

            if (accountMasterList != null)
            {
                dataGridViewAccount.DataSource = accountMasterList;
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

        private void comboBoxUserMaster_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            FillControls_AccountMaster();
        }
    }
}
