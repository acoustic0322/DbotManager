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
    public partial class CommentDialog : System.Windows.Forms.Form
    {
        #region PrivateMemory

        private bool _isLoading = true;

        private MySqlDataAccess dataAccess;

        private DbConnectionInfo dbConnection;

        private int _userId = 0;
        private int _accountId = 0;
        private int _commentId = 0;

        #endregion

        #region 初期化
        public CommentDialog(DbConnectionInfo dbConnection)
        {
            InitializeComponent();

            this.dbConnection = dbConnection;
        }

        private void CommentDialog_Load(object sender, EventArgs e)
        {
            // MySQLデータアクセスの初期化
            dataAccess = new MySqlDataAccess(this.dbConnection);

            _isLoading = false;
        }

        #endregion

        #region イベント
        private void dataGridViewComment_SelectionChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            if (dataGridViewComment.CurrentCell != null)
            {
                var commentId = dataGridViewComment.CurrentRow.Cells[CommentMaster_Id.Name].Value.ToString();
                _commentId = int.Parse(commentId);

                var comment = dataGridViewComment.CurrentRow.Cells[CommentMaster_Comment.Name].Value.ToString();
                textBoxコメント.Text = comment;

                var commentChatGpt = dataGridViewComment.CurrentRow.Cells[CommentMaster_ChatGpt.Name] as DataGridViewCheckBoxCell;
                if (commentChatGpt != null)
                {
                    checkBoxChatGpt.Checked = Convert.ToBoolean(commentChatGpt.Value);
                }

                var commentEnable = dataGridViewComment.CurrentRow.Cells[CommentMaster_Enable.Name] as DataGridViewCheckBoxCell;
                if (commentEnable != null)
                {
                    checkBox有効.Checked = Convert.ToBoolean(commentEnable.Value);
                }
            }
        }

        private void buttonコメント削除_Click(object sender, EventArgs e)
        {
            dataAccess.DeleteCommentMaster(_commentId);
            UpdateInfo(_accountId);
        }

        private void buttonコメント追加_Click(object sender, EventArgs e)
        {
            CommentMaster commentMaster = new CommentMaster()
            {
                Id = _commentId,
                UserId = _userId,
                AccountId = _accountId,
                ChatGpt = checkBoxChatGpt.Checked,
                Enable = checkBox有効.Checked,
                Comment = textBoxコメント.Text,
                TweetModeType = radioButtonツイート.Checked ? TweetModeTypes.Tweet : TweetModeTypes.Replay
            };

            dataAccess.InsertCommentMaster(commentMaster);
            UpdateInfo(_accountId);
        }

        private void buttonコメント保存_Click(object sender, EventArgs e)
        {
            CommentMaster commentMaster = new CommentMaster()
            {
                Id = _commentId,
                UserId = _userId,
                AccountId = _accountId,
                ChatGpt = checkBoxChatGpt.Checked,
                Enable = checkBox有効.Checked,
                Comment = textBoxコメント.Text,
                TweetModeType = radioButtonツイート.Checked ? TweetModeTypes.Tweet : TweetModeTypes.Replay
            };

            dataAccess.UpdateCommentMaster(commentMaster);
            UpdateInfo(_accountId);
        }

        private void radioButtonリプライ_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            UpdateInfo(_accountId);
        }

        private void radioButtonツイート_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            UpdateInfo(_accountId);
        }

        private void buttonExe_Click(object sender, EventArgs e)
        {
            int userId = _userId;
            int accountId = _accountId;
            int commentId = _commentId;
            string tweetId = GetTweetId(true);

            TweetTask _tweetTask = new TweetTask(dbConnection);
            _tweetTask.TweetProc(TweetProcTypes.TWEET, userId, accountId, commentId, tweetId);
        }

        private void buttonClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        #endregion

        #region 画面更新
        public void UpdateInfo(int accountId)
        {
            if (_isLoading) return;

            var accountMaster = dataAccess.GetAccountMaster().Where(x => x.Id == accountId).FirstOrDefault();
            _userId = accountMaster.UserId;
            _accountId = accountId;

            var list = dataAccess.GetCommentMasterByAccountId(accountId);

            if (radioButtonツイート.Checked)
            {
                list = list.Where(x => x.TweetModeType == TweetModeTypes.Tweet).ToList();
            }
            else
            {
                list = list.Where(x => x.TweetModeType == TweetModeTypes.Replay).ToList();
            }

            dataGridViewComment.DataSource = list;

            this.Text = $"{accountMaster.Name} の コメント設定";
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


    }
}
