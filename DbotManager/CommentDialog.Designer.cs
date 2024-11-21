namespace DbotManager
{
    partial class CommentDialog
    {
        /// <summary>
        /// Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// Clean up any resources being used.
        /// </summary>
        /// <param name="disposing">true if managed resources should be disposed; otherwise, false.</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows Form Designer generated code

        /// <summary>
        /// Required method for Designer support - do not modify
        /// the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            this.dataGridViewComment = new System.Windows.Forms.DataGridView();
            this.CommentMaster_Id = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_UserId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_AccountId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_Enable = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.CommentMaster_ChatGpt = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.CommentMaster_Comment = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.groupBox6 = new System.Windows.Forms.GroupBox();
            this.buttonコメント保存 = new System.Windows.Forms.Button();
            this.buttonコメント追加 = new System.Windows.Forms.Button();
            this.buttonコメント削除 = new System.Windows.Forms.Button();
            this.checkBoxChatGpt = new System.Windows.Forms.CheckBox();
            this.checkBox有効 = new System.Windows.Forms.CheckBox();
            this.textBoxコメント = new System.Windows.Forms.TextBox();
            this.radioButtonツイート = new System.Windows.Forms.RadioButton();
            this.radioButtonリプライ = new System.Windows.Forms.RadioButton();
            this.textBoxUrlTweetID = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.buttonExe = new System.Windows.Forms.Button();
            this.buttonClose = new System.Windows.Forms.Button();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewComment)).BeginInit();
            this.groupBox6.SuspendLayout();
            this.groupBox1.SuspendLayout();
            this.SuspendLayout();
            // 
            // dataGridViewComment
            // 
            this.dataGridViewComment.AllowUserToAddRows = false;
            this.dataGridViewComment.AllowUserToDeleteRows = false;
            this.dataGridViewComment.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridViewComment.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.CommentMaster_Id,
            this.CommentMaster_UserId,
            this.CommentMaster_AccountId,
            this.CommentMaster_Enable,
            this.CommentMaster_ChatGpt,
            this.CommentMaster_Comment});
            this.dataGridViewComment.Location = new System.Drawing.Point(13, 37);
            this.dataGridViewComment.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.dataGridViewComment.Name = "dataGridViewComment";
            this.dataGridViewComment.RowHeadersVisible = false;
            this.dataGridViewComment.RowTemplate.Height = 21;
            this.dataGridViewComment.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridViewComment.Size = new System.Drawing.Size(617, 272);
            this.dataGridViewComment.TabIndex = 5;
            this.dataGridViewComment.SelectionChanged += new System.EventHandler(this.dataGridViewComment_SelectionChanged);
            // 
            // CommentMaster_Id
            // 
            this.CommentMaster_Id.DataPropertyName = "Id";
            this.CommentMaster_Id.HeaderText = "Id";
            this.CommentMaster_Id.Name = "CommentMaster_Id";
            this.CommentMaster_Id.Visible = false;
            // 
            // CommentMaster_UserId
            // 
            this.CommentMaster_UserId.DataPropertyName = "UserId";
            this.CommentMaster_UserId.HeaderText = "UserId";
            this.CommentMaster_UserId.Name = "CommentMaster_UserId";
            this.CommentMaster_UserId.Visible = false;
            // 
            // CommentMaster_AccountId
            // 
            this.CommentMaster_AccountId.DataPropertyName = "AccountId";
            this.CommentMaster_AccountId.HeaderText = "AccountId";
            this.CommentMaster_AccountId.Name = "CommentMaster_AccountId";
            this.CommentMaster_AccountId.Visible = false;
            // 
            // CommentMaster_Enable
            // 
            this.CommentMaster_Enable.DataPropertyName = "Enable";
            this.CommentMaster_Enable.FalseValue = "False";
            this.CommentMaster_Enable.HeaderText = "有効";
            this.CommentMaster_Enable.Name = "CommentMaster_Enable";
            this.CommentMaster_Enable.TrueValue = "True";
            this.CommentMaster_Enable.Width = 80;
            // 
            // CommentMaster_ChatGpt
            // 
            this.CommentMaster_ChatGpt.DataPropertyName = "ChatGpt";
            this.CommentMaster_ChatGpt.FalseValue = "False";
            this.CommentMaster_ChatGpt.HeaderText = "ChatGpt";
            this.CommentMaster_ChatGpt.Name = "CommentMaster_ChatGpt";
            this.CommentMaster_ChatGpt.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.CommentMaster_ChatGpt.SortMode = System.Windows.Forms.DataGridViewColumnSortMode.Automatic;
            this.CommentMaster_ChatGpt.TrueValue = "True";
            this.CommentMaster_ChatGpt.Width = 80;
            // 
            // CommentMaster_Comment
            // 
            this.CommentMaster_Comment.DataPropertyName = "Comment";
            this.CommentMaster_Comment.HeaderText = "コメント";
            this.CommentMaster_Comment.Name = "CommentMaster_Comment";
            this.CommentMaster_Comment.Width = 500;
            // 
            // groupBox6
            // 
            this.groupBox6.Controls.Add(this.buttonコメント保存);
            this.groupBox6.Controls.Add(this.buttonコメント追加);
            this.groupBox6.Controls.Add(this.buttonコメント削除);
            this.groupBox6.Controls.Add(this.checkBoxChatGpt);
            this.groupBox6.Controls.Add(this.checkBox有効);
            this.groupBox6.Controls.Add(this.textBoxコメント);
            this.groupBox6.Location = new System.Drawing.Point(13, 319);
            this.groupBox6.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.groupBox6.Name = "groupBox6";
            this.groupBox6.Padding = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.groupBox6.Size = new System.Drawing.Size(617, 217);
            this.groupBox6.TabIndex = 6;
            this.groupBox6.TabStop = false;
            this.groupBox6.Text = "コメント設定";
            // 
            // buttonコメント保存
            // 
            this.buttonコメント保存.Location = new System.Drawing.Point(494, 174);
            this.buttonコメント保存.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonコメント保存.Name = "buttonコメント保存";
            this.buttonコメント保存.Size = new System.Drawing.Size(92, 33);
            this.buttonコメント保存.TabIndex = 7;
            this.buttonコメント保存.Text = "更新";
            this.buttonコメント保存.UseVisualStyleBackColor = true;
            this.buttonコメント保存.Click += new System.EventHandler(this.buttonコメント保存_Click);
            // 
            // buttonコメント追加
            // 
            this.buttonコメント追加.Location = new System.Drawing.Point(124, 174);
            this.buttonコメント追加.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonコメント追加.Name = "buttonコメント追加";
            this.buttonコメント追加.Size = new System.Drawing.Size(92, 33);
            this.buttonコメント追加.TabIndex = 6;
            this.buttonコメント追加.Text = "複製・追加";
            this.buttonコメント追加.UseVisualStyleBackColor = true;
            this.buttonコメント追加.Click += new System.EventHandler(this.buttonコメント追加_Click);
            // 
            // buttonコメント削除
            // 
            this.buttonコメント削除.Location = new System.Drawing.Point(24, 174);
            this.buttonコメント削除.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonコメント削除.Name = "buttonコメント削除";
            this.buttonコメント削除.Size = new System.Drawing.Size(92, 33);
            this.buttonコメント削除.TabIndex = 5;
            this.buttonコメント削除.Text = "削除";
            this.buttonコメント削除.UseVisualStyleBackColor = true;
            this.buttonコメント削除.Click += new System.EventHandler(this.buttonコメント削除_Click);
            // 
            // checkBoxChatGpt
            // 
            this.checkBoxChatGpt.AutoSize = true;
            this.checkBoxChatGpt.Location = new System.Drawing.Point(100, 30);
            this.checkBoxChatGpt.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.checkBoxChatGpt.Name = "checkBoxChatGpt";
            this.checkBoxChatGpt.Size = new System.Drawing.Size(88, 23);
            this.checkBoxChatGpt.TabIndex = 2;
            this.checkBoxChatGpt.Text = "ChatGpt";
            this.checkBoxChatGpt.UseVisualStyleBackColor = true;
            // 
            // checkBox有効
            // 
            this.checkBox有効.AutoSize = true;
            this.checkBox有効.Location = new System.Drawing.Point(24, 30);
            this.checkBox有効.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.checkBox有効.Name = "checkBox有効";
            this.checkBox有効.Size = new System.Drawing.Size(58, 23);
            this.checkBox有効.TabIndex = 1;
            this.checkBox有効.Text = "有効";
            this.checkBox有効.UseVisualStyleBackColor = true;
            // 
            // textBoxコメント
            // 
            this.textBoxコメント.Location = new System.Drawing.Point(24, 64);
            this.textBoxコメント.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.textBoxコメント.Multiline = true;
            this.textBoxコメント.Name = "textBoxコメント";
            this.textBoxコメント.Size = new System.Drawing.Size(562, 100);
            this.textBoxコメント.TabIndex = 0;
            // 
            // radioButtonツイート
            // 
            this.radioButtonツイート.AutoSize = true;
            this.radioButtonツイート.Checked = true;
            this.radioButtonツイート.Location = new System.Drawing.Point(13, 8);
            this.radioButtonツイート.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.radioButtonツイート.Name = "radioButtonツイート";
            this.radioButtonツイート.Size = new System.Drawing.Size(72, 23);
            this.radioButtonツイート.TabIndex = 7;
            this.radioButtonツイート.TabStop = true;
            this.radioButtonツイート.Text = "ツイート";
            this.radioButtonツイート.UseVisualStyleBackColor = true;
            this.radioButtonツイート.CheckedChanged += new System.EventHandler(this.radioButtonツイート_CheckedChanged);
            // 
            // radioButtonリプライ
            // 
            this.radioButtonリプライ.AutoSize = true;
            this.radioButtonリプライ.Location = new System.Drawing.Point(109, 8);
            this.radioButtonリプライ.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.radioButtonリプライ.Name = "radioButtonリプライ";
            this.radioButtonリプライ.Size = new System.Drawing.Size(68, 23);
            this.radioButtonリプライ.TabIndex = 8;
            this.radioButtonリプライ.Text = "リプライ";
            this.radioButtonリプライ.UseVisualStyleBackColor = true;
            this.radioButtonリプライ.CheckedChanged += new System.EventHandler(this.radioButtonリプライ_CheckedChanged);
            // 
            // textBoxUrlTweetID
            // 
            this.textBoxUrlTweetID.Location = new System.Drawing.Point(121, 29);
            this.textBoxUrlTweetID.Name = "textBoxUrlTweetID";
            this.textBoxUrlTweetID.Size = new System.Drawing.Size(395, 27);
            this.textBoxUrlTweetID.TabIndex = 10;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(9, 32);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(108, 19);
            this.label2.TabIndex = 9;
            this.label2.Text = "URL・TweetID";
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.buttonExe);
            this.groupBox1.Controls.Add(this.textBoxUrlTweetID);
            this.groupBox1.Controls.Add(this.label2);
            this.groupBox1.Location = new System.Drawing.Point(12, 544);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(618, 70);
            this.groupBox1.TabIndex = 11;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "コメントテスト";
            // 
            // buttonExe
            // 
            this.buttonExe.Location = new System.Drawing.Point(525, 28);
            this.buttonExe.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonExe.Name = "buttonExe";
            this.buttonExe.Size = new System.Drawing.Size(84, 27);
            this.buttonExe.TabIndex = 11;
            this.buttonExe.Text = "実行";
            this.buttonExe.UseVisualStyleBackColor = true;
            this.buttonExe.Click += new System.EventHandler(this.buttonExe_Click);
            // 
            // buttonClose
            // 
            this.buttonClose.Location = new System.Drawing.Point(538, 622);
            this.buttonClose.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonClose.Name = "buttonClose";
            this.buttonClose.Size = new System.Drawing.Size(92, 33);
            this.buttonClose.TabIndex = 12;
            this.buttonClose.Text = "閉じる";
            this.buttonClose.UseVisualStyleBackColor = true;
            this.buttonClose.Click += new System.EventHandler(this.buttonClose_Click);
            // 
            // CommentDialog
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 19F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(647, 681);
            this.Controls.Add(this.buttonClose);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.radioButtonリプライ);
            this.Controls.Add(this.radioButtonツイート);
            this.Controls.Add(this.groupBox6);
            this.Controls.Add(this.dataGridViewComment);
            this.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "CommentDialog";
            this.Text = "CommentRegistrationDialog";
            this.Load += new System.EventHandler(this.CommentDialog_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewComment)).EndInit();
            this.groupBox6.ResumeLayout(false);
            this.groupBox6.PerformLayout();
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.DataGridView dataGridViewComment;
        private System.Windows.Forms.GroupBox groupBox6;
        private System.Windows.Forms.Button buttonコメント保存;
        private System.Windows.Forms.Button buttonコメント追加;
        private System.Windows.Forms.Button buttonコメント削除;
        private System.Windows.Forms.CheckBox checkBoxChatGpt;
        private System.Windows.Forms.CheckBox checkBox有効;
        private System.Windows.Forms.TextBox textBoxコメント;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_Id;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_UserId;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_AccountId;
        private System.Windows.Forms.DataGridViewCheckBoxColumn CommentMaster_Enable;
        private System.Windows.Forms.DataGridViewCheckBoxColumn CommentMaster_ChatGpt;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_Comment;
        private System.Windows.Forms.RadioButton radioButtonツイート;
        private System.Windows.Forms.RadioButton radioButtonリプライ;
        private System.Windows.Forms.TextBox textBoxUrlTweetID;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.Button buttonExe;
        private System.Windows.Forms.Button buttonClose;
    }
}