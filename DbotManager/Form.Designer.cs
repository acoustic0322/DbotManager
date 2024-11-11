namespace DbotManager
{
    partial class Form
    {
        /// <summary>
        /// 必要なデザイナー変数です。
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        /// 使用中のリソースをすべてクリーンアップします。
        /// </summary>
        /// <param name="disposing">マネージド リソースを破棄する場合は true を指定し、その他の場合は false を指定します。</param>
        protected override void Dispose(bool disposing)
        {
            if (disposing && (components != null))
            {
                components.Dispose();
            }
            base.Dispose(disposing);
        }

        #region Windows フォーム デザイナーで生成されたコード

        /// <summary>
        /// デザイナー サポートに必要なメソッドです。このメソッドの内容を
        /// コード エディターで変更しないでください。
        /// </summary>
        private void InitializeComponent()
        {
            this.tabControl = new System.Windows.Forms.TabControl();
            this.tabPageデバッグ = new System.Windows.Forms.TabPage();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.textBoxUrlTweetID = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.buttonブックマーク = new System.Windows.Forms.Button();
            this.buttonいいね = new System.Windows.Forms.Button();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.dataGridViewComment = new System.Windows.Forms.DataGridView();
            this.CommentMaster_Id = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_UserId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_AccountId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_Comment = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_Enable = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.buttonコメント = new System.Windows.Forms.Button();
            this.dataGridViewAccount = new System.Windows.Forms.DataGridView();
            this.AccountMaster_Id = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_UserId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_Name = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_LoginId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_LoginPass = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_ApiKey = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_ApiKeySecret = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_AccessToken = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_BearerToken = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_RefreshToken = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_Enable = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.comboBoxUserMaster = new System.Windows.Forms.ComboBox();
            this.tabPage履歴 = new System.Windows.Forms.TabPage();
            this.dataGridViewTweetHistory = new System.Windows.Forms.DataGridView();
            this.textBoxLog = new System.Windows.Forms.TextBox();
            this.tabControl.SuspendLayout();
            this.tabPageデバッグ.SuspendLayout();
            this.groupBox2.SuspendLayout();
            this.groupBox1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewComment)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewAccount)).BeginInit();
            this.tabPage履歴.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewTweetHistory)).BeginInit();
            this.SuspendLayout();
            // 
            // tabControl
            // 
            this.tabControl.Controls.Add(this.tabPageデバッグ);
            this.tabControl.Controls.Add(this.tabPage履歴);
            this.tabControl.Font = new System.Drawing.Font("Meiryo UI", 11.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(128)));
            this.tabControl.Location = new System.Drawing.Point(13, 14);
            this.tabControl.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabControl.Name = "tabControl";
            this.tabControl.SelectedIndex = 0;
            this.tabControl.Size = new System.Drawing.Size(768, 674);
            this.tabControl.TabIndex = 0;
            // 
            // tabPageデバッグ
            // 
            this.tabPageデバッグ.Controls.Add(this.groupBox2);
            this.tabPageデバッグ.Controls.Add(this.groupBox1);
            this.tabPageデバッグ.Controls.Add(this.dataGridViewAccount);
            this.tabPageデバッグ.Controls.Add(this.comboBoxUserMaster);
            this.tabPageデバッグ.Location = new System.Drawing.Point(4, 28);
            this.tabPageデバッグ.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabPageデバッグ.Name = "tabPageデバッグ";
            this.tabPageデバッグ.Padding = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabPageデバッグ.Size = new System.Drawing.Size(760, 642);
            this.tabPageデバッグ.TabIndex = 0;
            this.tabPageデバッグ.Text = "デバッグ";
            this.tabPageデバッグ.UseVisualStyleBackColor = true;
            // 
            // groupBox2
            // 
            this.groupBox2.Controls.Add(this.textBoxUrlTweetID);
            this.groupBox2.Controls.Add(this.label1);
            this.groupBox2.Controls.Add(this.buttonブックマーク);
            this.groupBox2.Controls.Add(this.buttonいいね);
            this.groupBox2.Location = new System.Drawing.Point(7, 451);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(624, 120);
            this.groupBox2.TabIndex = 6;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "いいね・ブックマーク";
            // 
            // textBoxUrlTweetID
            // 
            this.textBoxUrlTweetID.Location = new System.Drawing.Point(125, 29);
            this.textBoxUrlTweetID.Name = "textBoxUrlTweetID";
            this.textBoxUrlTweetID.Size = new System.Drawing.Size(470, 27);
            this.textBoxUrlTweetID.TabIndex = 1;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(11, 32);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(108, 19);
            this.label1.TabIndex = 0;
            this.label1.Text = "URL・TweetID";
            // 
            // buttonブックマーク
            // 
            this.buttonブックマーク.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonブックマーク.Location = new System.Drawing.Point(377, 62);
            this.buttonブックマーク.Name = "buttonブックマーク";
            this.buttonブックマーク.Size = new System.Drawing.Size(106, 45);
            this.buttonブックマーク.TabIndex = 3;
            this.buttonブックマーク.Text = "ブックマーク";
            this.buttonブックマーク.UseVisualStyleBackColor = true;
            this.buttonブックマーク.Click += new System.EventHandler(this.buttonブックマーク_Click);
            // 
            // buttonいいね
            // 
            this.buttonいいね.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonいいね.Location = new System.Drawing.Point(489, 62);
            this.buttonいいね.Name = "buttonいいね";
            this.buttonいいね.Size = new System.Drawing.Size(106, 45);
            this.buttonいいね.TabIndex = 2;
            this.buttonいいね.Text = "いいね";
            this.buttonいいね.UseVisualStyleBackColor = true;
            this.buttonいいね.Click += new System.EventHandler(this.buttonいいね_Click);
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.dataGridViewComment);
            this.groupBox1.Controls.Add(this.buttonコメント);
            this.groupBox1.Location = new System.Drawing.Point(22, 319);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(731, 126);
            this.groupBox1.TabIndex = 5;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "コメント";
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
            this.CommentMaster_Comment,
            this.CommentMaster_Enable});
            this.dataGridViewComment.Location = new System.Drawing.Point(6, 26);
            this.dataGridViewComment.Name = "dataGridViewComment";
            this.dataGridViewComment.RowHeadersVisible = false;
            this.dataGridViewComment.RowTemplate.Height = 21;
            this.dataGridViewComment.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridViewComment.Size = new System.Drawing.Size(607, 94);
            this.dataGridViewComment.TabIndex = 4;
            // 
            // CommentMaster_Id
            // 
            this.CommentMaster_Id.DataPropertyName = "Id";
            this.CommentMaster_Id.HeaderText = "Id";
            this.CommentMaster_Id.Name = "CommentMaster_Id";
            // 
            // CommentMaster_UserId
            // 
            this.CommentMaster_UserId.DataPropertyName = "UserId";
            this.CommentMaster_UserId.HeaderText = "UserId";
            this.CommentMaster_UserId.Name = "CommentMaster_UserId";
            // 
            // CommentMaster_AccountId
            // 
            this.CommentMaster_AccountId.DataPropertyName = "AccountId";
            this.CommentMaster_AccountId.HeaderText = "AccountId";
            this.CommentMaster_AccountId.Name = "CommentMaster_AccountId";
            // 
            // CommentMaster_Comment
            // 
            this.CommentMaster_Comment.DataPropertyName = "Comment";
            this.CommentMaster_Comment.HeaderText = "コメント";
            this.CommentMaster_Comment.Name = "CommentMaster_Comment";
            // 
            // CommentMaster_Enable
            // 
            this.CommentMaster_Enable.DataPropertyName = "Enable";
            this.CommentMaster_Enable.FalseValue = "False";
            this.CommentMaster_Enable.HeaderText = "有効";
            this.CommentMaster_Enable.Name = "CommentMaster_Enable";
            this.CommentMaster_Enable.TrueValue = "True";
            // 
            // buttonコメント
            // 
            this.buttonコメント.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonコメント.Location = new System.Drawing.Point(619, 26);
            this.buttonコメント.Name = "buttonコメント";
            this.buttonコメント.Size = new System.Drawing.Size(106, 45);
            this.buttonコメント.TabIndex = 4;
            this.buttonコメント.Text = "コメント";
            this.buttonコメント.UseVisualStyleBackColor = true;
            this.buttonコメント.Click += new System.EventHandler(this.buttonコメント_Click);
            // 
            // dataGridViewAccount
            // 
            this.dataGridViewAccount.AllowUserToAddRows = false;
            this.dataGridViewAccount.AllowUserToDeleteRows = false;
            this.dataGridViewAccount.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridViewAccount.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.AccountMaster_Id,
            this.AccountMaster_UserId,
            this.AccountMaster_Name,
            this.AccountMaster_LoginId,
            this.AccountMaster_LoginPass,
            this.AccountMaster_ApiKey,
            this.AccountMaster_ApiKeySecret,
            this.AccountMaster_AccessToken,
            this.AccountMaster_BearerToken,
            this.AccountMaster_RefreshToken,
            this.AccountMaster_Enable});
            this.dataGridViewAccount.Location = new System.Drawing.Point(22, 45);
            this.dataGridViewAccount.MultiSelect = false;
            this.dataGridViewAccount.Name = "dataGridViewAccount";
            this.dataGridViewAccount.RowHeadersVisible = false;
            this.dataGridViewAccount.RowTemplate.Height = 21;
            this.dataGridViewAccount.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridViewAccount.Size = new System.Drawing.Size(731, 268);
            this.dataGridViewAccount.TabIndex = 1;
            // 
            // AccountMaster_Id
            // 
            this.AccountMaster_Id.DataPropertyName = "Id";
            this.AccountMaster_Id.HeaderText = "Id";
            this.AccountMaster_Id.Name = "AccountMaster_Id";
            // 
            // AccountMaster_UserId
            // 
            this.AccountMaster_UserId.DataPropertyName = "UserId";
            this.AccountMaster_UserId.HeaderText = "UserId";
            this.AccountMaster_UserId.Name = "AccountMaster_UserId";
            // 
            // AccountMaster_Name
            // 
            this.AccountMaster_Name.DataPropertyName = "Name";
            this.AccountMaster_Name.HeaderText = "Name";
            this.AccountMaster_Name.Name = "AccountMaster_Name";
            // 
            // AccountMaster_LoginId
            // 
            this.AccountMaster_LoginId.DataPropertyName = "LoginId";
            this.AccountMaster_LoginId.HeaderText = "ログインID";
            this.AccountMaster_LoginId.Name = "AccountMaster_LoginId";
            // 
            // AccountMaster_LoginPass
            // 
            this.AccountMaster_LoginPass.DataPropertyName = "LoginPass";
            this.AccountMaster_LoginPass.HeaderText = "ログインパス";
            this.AccountMaster_LoginPass.Name = "AccountMaster_LoginPass";
            // 
            // AccountMaster_ApiKey
            // 
            this.AccountMaster_ApiKey.DataPropertyName = "ApiKey";
            this.AccountMaster_ApiKey.HeaderText = "ApiKey";
            this.AccountMaster_ApiKey.Name = "AccountMaster_ApiKey";
            // 
            // AccountMaster_ApiKeySecret
            // 
            this.AccountMaster_ApiKeySecret.DataPropertyName = "ApiKeySecret";
            this.AccountMaster_ApiKeySecret.HeaderText = "ApiKeySecret";
            this.AccountMaster_ApiKeySecret.Name = "AccountMaster_ApiKeySecret";
            // 
            // AccountMaster_AccessToken
            // 
            this.AccountMaster_AccessToken.DataPropertyName = "AccessToken";
            this.AccountMaster_AccessToken.HeaderText = "AccessToken";
            this.AccountMaster_AccessToken.Name = "AccountMaster_AccessToken";
            // 
            // AccountMaster_BearerToken
            // 
            this.AccountMaster_BearerToken.DataPropertyName = "BearerToken";
            this.AccountMaster_BearerToken.HeaderText = "BearerToken";
            this.AccountMaster_BearerToken.Name = "AccountMaster_BearerToken";
            // 
            // AccountMaster_RefreshToken
            // 
            this.AccountMaster_RefreshToken.DataPropertyName = "RefreshToken";
            this.AccountMaster_RefreshToken.HeaderText = "RefreshToken";
            this.AccountMaster_RefreshToken.Name = "AccountMaster_RefreshToken";
            // 
            // AccountMaster_Enable
            // 
            this.AccountMaster_Enable.DataPropertyName = "Enable";
            this.AccountMaster_Enable.FalseValue = "False";
            this.AccountMaster_Enable.HeaderText = "有効";
            this.AccountMaster_Enable.Name = "AccountMaster_Enable";
            this.AccountMaster_Enable.TrueValue = "True";
            // 
            // comboBoxUserMaster
            // 
            this.comboBoxUserMaster.FormattingEnabled = true;
            this.comboBoxUserMaster.Location = new System.Drawing.Point(22, 10);
            this.comboBoxUserMaster.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.comboBoxUserMaster.Name = "comboBoxUserMaster";
            this.comboBoxUserMaster.Size = new System.Drawing.Size(180, 27);
            this.comboBoxUserMaster.TabIndex = 0;
            this.comboBoxUserMaster.SelectedIndexChanged += new System.EventHandler(this.comboBoxUserMaster_SelectedIndexChanged);
            // 
            // tabPage履歴
            // 
            this.tabPage履歴.Controls.Add(this.dataGridViewTweetHistory);
            this.tabPage履歴.Location = new System.Drawing.Point(4, 28);
            this.tabPage履歴.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabPage履歴.Name = "tabPage履歴";
            this.tabPage履歴.Padding = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabPage履歴.Size = new System.Drawing.Size(760, 642);
            this.tabPage履歴.TabIndex = 1;
            this.tabPage履歴.Text = "履歴";
            this.tabPage履歴.UseVisualStyleBackColor = true;
            // 
            // dataGridViewTweetHistory
            // 
            this.dataGridViewTweetHistory.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridViewTweetHistory.Location = new System.Drawing.Point(7, 8);
            this.dataGridViewTweetHistory.Name = "dataGridViewTweetHistory";
            this.dataGridViewTweetHistory.RowTemplate.Height = 21;
            this.dataGridViewTweetHistory.Size = new System.Drawing.Size(631, 626);
            this.dataGridViewTweetHistory.TabIndex = 0;
            // 
            // textBoxLog
            // 
            this.textBoxLog.Location = new System.Drawing.Point(798, 42);
            this.textBoxLog.Multiline = true;
            this.textBoxLog.Name = "textBoxLog";
            this.textBoxLog.Size = new System.Drawing.Size(606, 642);
            this.textBoxLog.TabIndex = 1;
            // 
            // Form
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 19F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1416, 712);
            this.Controls.Add(this.textBoxLog);
            this.Controls.Add(this.tabControl);
            this.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.Name = "Form";
            this.Text = "Form1";
            this.Load += new System.EventHandler(this.MainForm_Load);
            this.tabControl.ResumeLayout(false);
            this.tabPageデバッグ.ResumeLayout(false);
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
            this.groupBox1.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewComment)).EndInit();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewAccount)).EndInit();
            this.tabPage履歴.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewTweetHistory)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TabControl tabControl;
        private System.Windows.Forms.TabPage tabPageデバッグ;
        private System.Windows.Forms.TabPage tabPage履歴;
        private System.Windows.Forms.ComboBox comboBoxUserMaster;
        private System.Windows.Forms.Button buttonブックマーク;
        private System.Windows.Forms.Button buttonいいね;
        private System.Windows.Forms.DataGridView dataGridViewAccount;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.DataGridView dataGridViewComment;
        private System.Windows.Forms.Button buttonコメント;
        private System.Windows.Forms.GroupBox groupBox2;
        private System.Windows.Forms.TextBox textBoxUrlTweetID;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.DataGridView dataGridViewTweetHistory;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_Id;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_UserId;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_AccountId;
        private System.Windows.Forms.DataGridViewTextBoxColumn CommentMaster_Comment;
        private System.Windows.Forms.DataGridViewCheckBoxColumn CommentMaster_Enable;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_Id;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_UserId;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_Name;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_LoginId;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_LoginPass;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_ApiKey;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_ApiKeySecret;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_AccessToken;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_BearerToken;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_RefreshToken;
        private System.Windows.Forms.DataGridViewCheckBoxColumn AccountMaster_Enable;
        private System.Windows.Forms.TextBox textBoxLog;
    }
}

