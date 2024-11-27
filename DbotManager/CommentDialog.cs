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

        public int AccountId { get; set; }
        public int UserId { get; set; }

        private List<CommentMaster> _commentMasterList = new List<CommentMaster>();
        private List<AccountMaster> _accountMasterList = new List<AccountMaster>();
        private List<MediaMaster> _mediaMasterList = new List<MediaMaster>();

        

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

            ReadCommentMaster();

            _isLoading = false;
        }

        private void ReadCommentMaster(int commentId = 0)
        {
            _isLoading = true;
            _commentMasterList = dataAccess.GetCommentMaster();
            _accountMasterList = dataAccess.GetAccountMaster();
            _mediaMasterList = dataAccess.GetMediaMaster();

            dataGridViewComment.DataSource = _commentMasterList.Where(x => x.AccountId == AccountId).ToList();
            UpdateInfo(commentId ,AccountId , UserId);
            _isLoading = false;
        }

        #endregion

        #region イベント
        private void dataGridViewComment_SelectionChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;

            if (dataGridViewComment.CurrentCell != null)
            {
                var commentId = int.Parse(dataGridViewComment.CurrentRow.Cells[CommentMaster_Id.Name].Value.ToString());
                FillControl_CommentInfo(commentId);
            }
        }

        private void FillControl_CommentInfo(int commentId)
        {
            var commentMaster = _commentMasterList.Where(x => x.Id == commentId).FirstOrDefault();
            textBoxCommentID.Text = commentId.ToString();

            checkBox有効.Checked = commentMaster.Enable;
            checkBoxChatGpt.Checked = commentMaster.ChatGpt;
            textBoxコメント.Text = commentMaster.Comment;

            if (commentMaster.MovieId != 0)
                radioButton動画.Checked = true;
            else if (commentMaster.PhotoId != 0)
                radioButton画像.Checked = true;
            else
                radioButtonメディアなし.Checked = true;
        }

        private void buttonコメント削除_Click(object sender, EventArgs e)
        {
            dataAccess.DeleteCommentMaster(int.Parse(textBoxCommentID.Text));
            ReadCommentMaster();
            //            UpdateInfo(_accountId);
        }

        private void buttonコメント追加_Click(object sender, EventArgs e)
        {
            CommentMaster commentMaster = new CommentMaster()
            {
                Id = int.Parse(textBoxCommentID.Text),
                UserId = UserId,
                AccountId = AccountId,
                ChatGpt = checkBoxChatGpt.Checked,
                Enable = checkBox有効.Checked,
                Comment = textBoxコメント.Text,
                TweetModeType = radioButtonツイート.Checked ? TweetModeTypes.Tweet : TweetModeTypes.Replay,
                PhotoId = radioButton画像.Checked ? int.Parse(comboBox画像.SelectedValue.ToString()) : 0,
                MovieId = radioButton動画.Checked ? int.Parse(comboBox動画.SelectedValue.ToString()) : 0,
            };

            dataAccess.InsertCommentMaster(commentMaster);
            ReadCommentMaster(int.Parse(textBoxCommentID.Text));
        }

        private void buttonコメント保存_Click(object sender, EventArgs e)
        {
            var movie = comboBox動画.SelectedValue.ToString();
            var photo = comboBox画像.SelectedValue.ToString();

            CommentMaster commentMaster = new CommentMaster()
            {
                Id = int.Parse(textBoxCommentID.Text),
                UserId = UserId,
                AccountId = AccountId,
                ChatGpt = checkBoxChatGpt.Checked,
                Enable = checkBox有効.Checked,
                Comment = textBoxコメント.Text,
                TweetModeType = radioButtonツイート.Checked ? TweetModeTypes.Tweet : TweetModeTypes.Replay,
                PhotoId = radioButton画像.Checked ? int.Parse(comboBox画像.SelectedValue.ToString()) : 0,
                MovieId = radioButton動画.Checked ? int.Parse(comboBox動画.SelectedValue.ToString()) : 0,
            };

            dataAccess.UpdateCommentMaster(commentMaster);
            ReadCommentMaster(int.Parse(textBoxCommentID.Text));
        }

        private void radioButtonリプライ_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            ReadCommentMaster();
        }

        private void radioButtonツイート_CheckedChanged(object sender, EventArgs e)
        {
            if (_isLoading) return;
            ReadCommentMaster();
        }

        private void buttonExe_Click(object sender, EventArgs e)
        {
            int userId = UserId;
            int accountId = AccountId;
            int commentId = int.Parse(textBoxCommentID.Text);

            TweetTask _tweetTask = new TweetTask(dbConnection , AppendLog);
            _tweetTask.TweetProc(TweetProcTypes.POST, userId, accountId, commentId, "");
        }

        private void buttonClose_Click(object sender, EventArgs e)
        {
            this.Close();
        }

        #endregion

        #region 画面更新
        public void UpdateInfo(int commentId = 0, int accountId = 0 , int userId = 0)
        {
            if(accountId != 0)
            {
                var list = _commentMasterList.Where(x => x.AccountId == accountId).ToList();

                if (radioButtonツイート.Checked)
                {
                    list = list.Where(x => x.TweetModeType == TweetModeTypes.Tweet).ToList();
                }
                else
                {
                    list = list.Where(x => x.TweetModeType == TweetModeTypes.Replay).ToList();
                }

                dataGridViewComment.DataSource = list;

                if(commentId != 0)
                {
                    SupportUtil.SelectRowsByColumnValue(dataGridViewComment, CommentMaster_Id.Name, commentId);
                }

                var accountName = _accountMasterList.Where(x => x.Id == accountId).FirstOrDefault().Name;
                this.Text = $"{accountName} の コメント設定";

                AccountId = accountId;

                if (_mediaMasterList != null && AccountId != 0)
                {
                    comboBox画像.DataSource = _mediaMasterList.Where(x => x.AccountId == AccountId && x.MediaType == MediaTypes.Photo).ToList();
                    comboBox画像.DisplayMember = "Name"; // コンボボックスに表示するプロパティ
                    comboBox画像.ValueMember = "MediaId";     // 選択されたときに取得するプロパティ

                    comboBox動画.DataSource = _mediaMasterList.Where(x => x.AccountId == AccountId && x.MediaType == MediaTypes.Movie).ToList();
                    comboBox動画.DisplayMember = "Name"; // コンボボックスに表示するプロパティ
                    comboBox動画.ValueMember = "MediaId";     // 選択されたときに取得するプロパティ
                }
            }
            else
            {
                // DataGridViewの先頭行を選択
                dataGridViewComment.ClearSelection(); // 一度選択をクリア
                if (dataGridViewComment.Rows.Count > 1)
                    dataGridViewComment.Rows[0].Selected = true; // 先頭行を選択
            }

            if(userId != 0)
            {
                UserId = userId;
            }
        }

        #endregion

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
