namespace DbotManager
{
    partial class CheckAccountDialog
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
            this.groupBox6 = new System.Windows.Forms.GroupBox();
            this.textBoxId = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.buttonコメント保存 = new System.Windows.Forms.Button();
            this.buttonコメント追加 = new System.Windows.Forms.Button();
            this.buttonコメント削除 = new System.Windows.Forms.Button();
            this.checkBox有効 = new System.Windows.Forms.CheckBox();
            this.textBoxCheckAccount = new System.Windows.Forms.TextBox();
            this.buttonExe = new System.Windows.Forms.Button();
            this.radioButton監視 = new System.Windows.Forms.RadioButton();
            this.radioButton監視toReply = new System.Windows.Forms.RadioButton();
            this.buttonClose = new System.Windows.Forms.Button();
            this.textBoxRenew = new System.Windows.Forms.TextBox();
            this.label13 = new System.Windows.Forms.Label();
            this.textBoxUrlTweetID = new System.Windows.Forms.TextBox();
            this.radioButtonものまね = new System.Windows.Forms.RadioButton();
            this.CommentMaster_Id = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_UserId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_AccountId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_Enable = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.CommentMaster_Comment = new System.Windows.Forms.DataGridViewTextBoxColumn();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewComment)).BeginInit();
            this.groupBox6.SuspendLayout();
            this.SuspendLayout();
            // 
            // dataGridViewComment
            // 
            this.dataGridViewComment.AllowUserToAddRows = false;
            this.dataGridViewComment.AllowUserToDeleteRows = false;
            this.dataGridViewComment.AllowUserToResizeRows = false;
            this.dataGridViewComment.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridViewComment.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.CommentMaster_Id,
            this.CommentMaster_UserId,
            this.CommentMaster_AccountId,
            this.CommentMaster_Enable,
            this.CommentMaster_Comment});
            this.dataGridViewComment.Location = new System.Drawing.Point(13, 37);
            this.dataGridViewComment.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.dataGridViewComment.MultiSelect = false;
            this.dataGridViewComment.Name = "dataGridViewComment";
            this.dataGridViewComment.RowHeadersVisible = false;
            this.dataGridViewComment.RowTemplate.Height = 21;
            this.dataGridViewComment.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridViewComment.Size = new System.Drawing.Size(617, 272);
            this.dataGridViewComment.TabIndex = 5;
            this.dataGridViewComment.SelectionChanged += new System.EventHandler(this.dataGridViewComment_SelectionChanged);
            // 
            // groupBox6
            // 
            this.groupBox6.Controls.Add(this.textBoxId);
            this.groupBox6.Controls.Add(this.label1);
            this.groupBox6.Controls.Add(this.buttonコメント保存);
            this.groupBox6.Controls.Add(this.buttonコメント追加);
            this.groupBox6.Controls.Add(this.buttonコメント削除);
            this.groupBox6.Controls.Add(this.checkBox有効);
            this.groupBox6.Controls.Add(this.textBoxCheckAccount);
            this.groupBox6.Location = new System.Drawing.Point(13, 319);
            this.groupBox6.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.groupBox6.Name = "groupBox6";
            this.groupBox6.Padding = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.groupBox6.Size = new System.Drawing.Size(617, 218);
            this.groupBox6.TabIndex = 6;
            this.groupBox6.TabStop = false;
            this.groupBox6.Text = "コメント設定";
            // 
            // textBoxId
            // 
            this.textBoxId.Enabled = false;
            this.textBoxId.Location = new System.Drawing.Point(516, 28);
            this.textBoxId.Name = "textBoxId";
            this.textBoxId.Size = new System.Drawing.Size(70, 27);
            this.textBoxId.TabIndex = 37;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(484, 31);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(26, 19);
            this.label1.TabIndex = 36;
            this.label1.Text = "ID";
            // 
            // buttonコメント保存
            // 
            this.buttonコメント保存.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonコメント保存.Location = new System.Drawing.Point(516, 175);
            this.buttonコメント保存.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonコメント保存.Name = "buttonコメント保存";
            this.buttonコメント保存.Size = new System.Drawing.Size(92, 33);
            this.buttonコメント保存.TabIndex = 7;
            this.buttonコメント保存.Text = "保存";
            this.buttonコメント保存.UseVisualStyleBackColor = true;
            this.buttonコメント保存.Click += new System.EventHandler(this.buttonコメント保存_Click);
            // 
            // buttonコメント追加
            // 
            this.buttonコメント追加.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonコメント追加.Location = new System.Drawing.Point(416, 175);
            this.buttonコメント追加.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonコメント追加.Name = "buttonコメント追加";
            this.buttonコメント追加.Size = new System.Drawing.Size(92, 33);
            this.buttonコメント追加.TabIndex = 6;
            this.buttonコメント追加.Text = "複製";
            this.buttonコメント追加.UseVisualStyleBackColor = true;
            this.buttonコメント追加.Click += new System.EventHandler(this.buttonコメント追加_Click);
            // 
            // buttonコメント削除
            // 
            this.buttonコメント削除.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonコメント削除.Location = new System.Drawing.Point(316, 175);
            this.buttonコメント削除.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonコメント削除.Name = "buttonコメント削除";
            this.buttonコメント削除.Size = new System.Drawing.Size(92, 33);
            this.buttonコメント削除.TabIndex = 5;
            this.buttonコメント削除.Text = "削除";
            this.buttonコメント削除.UseVisualStyleBackColor = true;
            this.buttonコメント削除.Click += new System.EventHandler(this.buttonコメント削除_Click);
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
            // textBoxCheckAccount
            // 
            this.textBoxCheckAccount.Location = new System.Drawing.Point(24, 64);
            this.textBoxCheckAccount.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.textBoxCheckAccount.Name = "textBoxCheckAccount";
            this.textBoxCheckAccount.Size = new System.Drawing.Size(562, 27);
            this.textBoxCheckAccount.TabIndex = 0;
            // 
            // buttonExe
            // 
            this.buttonExe.Location = new System.Drawing.Point(13, 653);
            this.buttonExe.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonExe.Name = "buttonExe";
            this.buttonExe.Size = new System.Drawing.Size(109, 30);
            this.buttonExe.TabIndex = 11;
            this.buttonExe.Text = "テストツイート";
            this.buttonExe.UseVisualStyleBackColor = true;
            this.buttonExe.Click += new System.EventHandler(this.buttonExe_Click);
            // 
            // radioButton監視
            // 
            this.radioButton監視.AutoSize = true;
            this.radioButton監視.Checked = true;
            this.radioButton監視.Location = new System.Drawing.Point(13, 8);
            this.radioButton監視.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.radioButton監視.Name = "radioButton監視";
            this.radioButton監視.Size = new System.Drawing.Size(57, 23);
            this.radioButton監視.TabIndex = 7;
            this.radioButton監視.TabStop = true;
            this.radioButton監視.Text = "監視";
            this.radioButton監視.UseVisualStyleBackColor = true;
            this.radioButton監視.CheckedChanged += new System.EventHandler(this.radioButton監視_CheckedChanged);
            // 
            // radioButton監視toReply
            // 
            this.radioButton監視toReply.AutoSize = true;
            this.radioButton監視toReply.Location = new System.Drawing.Point(109, 8);
            this.radioButton監視toReply.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.radioButton監視toReply.Name = "radioButton監視toReply";
            this.radioButton監視toReply.Size = new System.Drawing.Size(112, 23);
            this.radioButton監視toReply.TabIndex = 8;
            this.radioButton監視toReply.Text = "監視toReply";
            this.radioButton監視toReply.UseVisualStyleBackColor = true;
            this.radioButton監視toReply.CheckedChanged += new System.EventHandler(this.radioButton監視toReply_CheckedChanged);
            // 
            // buttonClose
            // 
            this.buttonClose.Location = new System.Drawing.Point(538, 653);
            this.buttonClose.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonClose.Name = "buttonClose";
            this.buttonClose.Size = new System.Drawing.Size(92, 30);
            this.buttonClose.TabIndex = 12;
            this.buttonClose.Text = "閉じる";
            this.buttonClose.UseVisualStyleBackColor = true;
            this.buttonClose.Click += new System.EventHandler(this.buttonClose_Click);
            // 
            // textBoxRenew
            // 
            this.textBoxRenew.Font = new System.Drawing.Font("Meiryo UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(128)));
            this.textBoxRenew.Location = new System.Drawing.Point(13, 578);
            this.textBoxRenew.Multiline = true;
            this.textBoxRenew.Name = "textBoxRenew";
            this.textBoxRenew.ScrollBars = System.Windows.Forms.ScrollBars.Both;
            this.textBoxRenew.Size = new System.Drawing.Size(617, 67);
            this.textBoxRenew.TabIndex = 22;
            // 
            // label13
            // 
            this.label13.AutoSize = true;
            this.label13.Location = new System.Drawing.Point(14, 548);
            this.label13.Name = "label13";
            this.label13.Size = new System.Drawing.Size(108, 19);
            this.label13.TabIndex = 23;
            this.label13.Text = "URL・TweetID";
            // 
            // textBoxUrlTweetID
            // 
            this.textBoxUrlTweetID.Location = new System.Drawing.Point(128, 545);
            this.textBoxUrlTweetID.Name = "textBoxUrlTweetID";
            this.textBoxUrlTweetID.Size = new System.Drawing.Size(502, 27);
            this.textBoxUrlTweetID.TabIndex = 24;
            // 
            // radioButtonものまね
            // 
            this.radioButtonものまね.AutoSize = true;
            this.radioButtonものまね.Location = new System.Drawing.Point(258, 8);
            this.radioButtonものまね.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.radioButtonものまね.Name = "radioButtonものまね";
            this.radioButtonものまね.Size = new System.Drawing.Size(74, 23);
            this.radioButtonものまね.TabIndex = 25;
            this.radioButtonものまね.Text = "ものまね";
            this.radioButtonものまね.UseVisualStyleBackColor = true;
            this.radioButtonものまね.CheckedChanged += new System.EventHandler(this.radioButtonものまね_CheckedChanged);
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
            // CommentMaster_Comment
            // 
            this.CommentMaster_Comment.DataPropertyName = "CheckAccount";
            this.CommentMaster_Comment.HeaderText = "対象アカウント";
            this.CommentMaster_Comment.Name = "CommentMaster_Comment";
            this.CommentMaster_Comment.Width = 500;
            // 
            // CheckAccountDialog
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 19F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(647, 686);
            this.Controls.Add(this.radioButtonものまね);
            this.Controls.Add(this.label13);
            this.Controls.Add(this.textBoxUrlTweetID);
            this.Controls.Add(this.textBoxRenew);
            this.Controls.Add(this.buttonExe);
            this.Controls.Add(this.buttonClose);
            this.Controls.Add(this.radioButton監視toReply);
            this.Controls.Add(this.radioButton監視);
            this.Controls.Add(this.groupBox6);
            this.Controls.Add(this.dataGridViewComment);
            this.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "CheckAccountDialog";
            this.Text = "CommentRegistrationDialog";
            this.Load += new System.EventHandler(this.CommentDialog_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewComment)).EndInit();
            this.groupBox6.ResumeLayout(false);
            this.groupBox6.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.DataGridView dataGridViewComment;
        private System.Windows.Forms.GroupBox groupBox6;
        private System.Windows.Forms.Button buttonコメント保存;
        private System.Windows.Forms.Button buttonコメント追加;
        private System.Windows.Forms.Button buttonコメント削除;
        private System.Windows.Forms.CheckBox checkBox有効;
        private System.Windows.Forms.TextBox textBoxCheckAccount;
        private System.Windows.Forms.RadioButton radioButton監視;
        private System.Windows.Forms.RadioButton radioButton監視toReply;
        private System.Windows.Forms.Button buttonExe;
        private System.Windows.Forms.Button buttonClose;
        private System.Windows.Forms.TextBox textBoxId;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox textBoxRenew;
        private System.Windows.Forms.Label label13;
        private System.Windows.Forms.TextBox textBoxUrlTweetID;
        private System.Windows.Forms.RadioButton radioButtonものまね;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_Id;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_UserId;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_AccountId;
        private System.Windows.Forms.DataGridViewCheckBoxColumn CommentMaster_Enable;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_Comment;
    }
}