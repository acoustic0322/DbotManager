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

            Search();

            button再表示.BackColor = Color.Red;

            _isLoading = false;

        }

        private void UpdateControl_Master()
        {
            FillControls_UserName();
            FillControls_AccountName();
            FillControls_Mode();
        }

        private void FillControls_UserName()
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

        private void FillControls_AccountName()
        {
            List<AccountMaster> accountList = dataAccess.GetAccountMaster();

            /*
            if(checkBoxUser.Checked)
            {
                accountList = accountList.Where(x => x.UserId == (int)(comboBoxUserMaster.SelectedValue)).ToList();
            }
            */
            accountList = accountList.Where(x => x.UserId == (int)(comboBoxUserMaster.SelectedValue)).ToList();

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

        private void FillControls_Mode()
        {
            var items = Enum.GetValues(typeof(TweetProcTypes))
                .Cast<TweetProcTypes>()
                /*
                .Where(x => x != TweetProcTypes)  // ← 除外条件
                .Where(x => x != TweetProcTypes.NONE)  // ← 除外条件
                .Where(x => x != TweetProcTypes.NONE)  // ← 除外条件
                .Where(x => x != TweetProcTypes.NONE)  // ← 除外条件
                */
                .Select(e => new
                {
                    Value = e,
                    Display = GetEnumDescription(e)
                })
                .ToList();

            comboBoxモード.DataSource = items;
            comboBoxモード.DisplayMember = "Display";
            comboBoxモード.ValueMember = "Value";
        }

        private string GetEnumDescription(Enum value)
        {
            var fi = value.GetType().GetField(value.ToString());
            var attributes = (DescriptionAttribute[])fi.GetCustomAttributes(typeof(DescriptionAttribute), false);
            return attributes.Length > 0 ? attributes[0].Description : value.ToString();
        }

        private void Search()
        {
            _tweetHistoryList = dataAccess.GetTweetHistoryView().Where(x => x.UpdateTime >= DateTime.Today.AddDays(-1)).ToList();
        }


        private void UpdateTweetHistoryFilter()
        {
            if (_tweetHistoryList != null)
            {

                List<TweetHistory> dspHistoryList = new List<TweetHistory>();

                dspHistoryList.AddRange(_tweetHistoryList);

                if (checkBoxエラー.Checked) dspHistoryList = dspHistoryList.Where(x => x.Result == false).ToList();
                if (checkBoxUser.Checked) dspHistoryList = dspHistoryList.Where(x => x.UserId == (int)comboBoxUserMaster.SelectedValue).ToList();
                if (checkBoxAccount.Checked) dspHistoryList = dspHistoryList.Where(x => x.AccountId == (int)comboBoxAccount.SelectedValue).ToList();
                if (checkBoxモード.Checked) dspHistoryList = dspHistoryList.Where(x => x.Mode == (TweetProcTypes)comboBoxモード.SelectedValue).ToList();

                // 匿名型で表示用データを作成（表示したい列だけ）
                var displayList = dspHistoryList.Select(x => new
                {
                    日時 = ((DateTime)x.UpdateTime).ToString("MM/dd HH:mm:ss"),
                    ユーザー名 = x.UserName,
                    アカウントID = $"{x.AccountId}",
                    アカウント名 = $"{x.AccountName}",
                    モード = x.Mode,// GetModeName(x.Mode),
                    結果 = x.Result ? "" : "×",
                    LOG = x.ErrorLog,
                    ポスト内容 = x.Comment,
                }).ToList();


                dataGridViewTweetHistory.DataSource = displayList;

                // 列幅の設定（列名はプロパティ名またはヘッダ表示名と一致させる）
                dataGridViewTweetHistory.Columns["日時"].Width = 120;
                dataGridViewTweetHistory.Columns["ユーザー名"].Width = 100;
                dataGridViewTweetHistory.Columns["アカウントID"].Width = 100;
                dataGridViewTweetHistory.Columns["アカウント名"].Width = 120;
                dataGridViewTweetHistory.Columns["モード"].Width = 80;
                dataGridViewTweetHistory.Columns["結果"].Width = 50;
                dataGridViewTweetHistory.Columns["ポスト内容"].Width = 200;
                dataGridViewTweetHistory.Columns["LOG"].Width = 250;

                dataGridViewTweetHistory.AllowUserToResizeColumns = true;
                dataGridViewTweetHistory.AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.None;
            }
            else
            {
                MessageBox.Show("データを取得できませんでした。");
            }

        }

        private void buttonSearch_Click(object sender, EventArgs e)
        {
            Search();
        }

        private void comboBoxUserMaster_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            checkBoxUser.Checked = true;
            FillControls_AccountName();
            button再表示.BackColor = Color.Red;
        }

        private void comboBoxAccount_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            checkBoxAccount.Checked = true;
            button再表示.BackColor = Color.Red;

        }
        private void checkBoxUser_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            //            FillDebugControls_AccountName();
            button再表示.BackColor = Color.Red;
        }

        private void checkBoxAccount_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            button再表示.BackColor = Color.Red;
        }

        private void comboBoxモード_SelectedIndexChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            checkBoxモード.Checked = true;
            button再表示.BackColor = Color.Red;
        }

        private void button絞込_Click(object sender, EventArgs e)
        {
            UpdateTweetHistoryFilter();
            button再表示.BackColor = SystemColors.Control;
        }

        private void checkBoxエラー_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            button再表示.BackColor = Color.Red;
        }

        private void checkBoxモード_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            button再表示.BackColor = Color.Red;
        }
    }
}
