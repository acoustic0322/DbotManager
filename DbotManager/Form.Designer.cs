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
            this.textBoxUrlTweetID_Debug = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.buttonブックマーク_Debug = new System.Windows.Forms.Button();
            this.buttonいいね_Debug = new System.Windows.Forms.Button();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.dataGridViewComment = new System.Windows.Forms.DataGridView();
            this.CommentMaster_Id = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_UserId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_AccountId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_Comment = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_Enable = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.buttonコメント_Debug = new System.Windows.Forms.Button();
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
            this.tabPageいいねブックマーク = new System.Windows.Forms.TabPage();
            this.groupBox3 = new System.Windows.Forms.GroupBox();
            this.radioButtonいいね件数50 = new System.Windows.Forms.RadioButton();
            this.radioButtonいいね件数100 = new System.Windows.Forms.RadioButton();
            this.radioButtonいいね件数200 = new System.Windows.Forms.RadioButton();
            this.radioButtonいいね件数その他 = new System.Windows.Forms.RadioButton();
            this.textBox1 = new System.Windows.Forms.TextBox();
            this.groupBox4 = new System.Windows.Forms.GroupBox();
            this.checkBox_15分以内に履歴のある無料アカウントを除外する = new System.Windows.Forms.CheckBox();
            this.buttonいいねリスト作成 = new System.Windows.Forms.Button();
            this.dataGridViewいいねリスト = new System.Windows.Forms.DataGridView();
            this.dataGridViewTextBoxColumn1 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn2 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn3 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn4 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn5 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn6 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn7 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn8 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn9 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewTextBoxColumn10 = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewCheckBoxColumn1 = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.groupBox5 = new System.Windows.Forms.GroupBox();
            this.radioButtonいいね = new System.Windows.Forms.RadioButton();
            this.radioButtonブックマーク = new System.Windows.Forms.RadioButton();
            this.textBoxUrlTweetID = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.buttonいいねブックマーク実行 = new System.Windows.Forms.Button();
            this.tabControl.SuspendLayout();
            this.tabPageデバッグ.SuspendLayout();
            this.groupBox2.SuspendLayout();
            this.groupBox1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewComment)).BeginInit();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewAccount)).BeginInit();
            this.tabPage履歴.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewTweetHistory)).BeginInit();
            this.tabPageいいねブックマーク.SuspendLayout();
            this.groupBox3.SuspendLayout();
            this.groupBox4.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewいいねリスト)).BeginInit();
            this.groupBox5.SuspendLayout();
            this.SuspendLayout();
            // 
            // tabControl
            // 
            this.tabControl.Controls.Add(this.tabPageいいねブックマーク);
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
            this.groupBox2.Controls.Add(this.textBoxUrlTweetID_Debug);
            this.groupBox2.Controls.Add(this.label1);
            this.groupBox2.Controls.Add(this.buttonブックマーク_Debug);
            this.groupBox2.Controls.Add(this.buttonいいね_Debug);
            this.groupBox2.Location = new System.Drawing.Point(7, 451);
            this.groupBox2.Name = "groupBox2";
            this.groupBox2.Size = new System.Drawing.Size(624, 120);
            this.groupBox2.TabIndex = 6;
            this.groupBox2.TabStop = false;
            this.groupBox2.Text = "いいね・ブックマーク";
            // 
            // textBoxUrlTweetID_Debug
            // 
            this.textBoxUrlTweetID_Debug.Location = new System.Drawing.Point(125, 29);
            this.textBoxUrlTweetID_Debug.Name = "textBoxUrlTweetID_Debug";
            this.textBoxUrlTweetID_Debug.Size = new System.Drawing.Size(470, 27);
            this.textBoxUrlTweetID_Debug.TabIndex = 1;
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
            // buttonブックマーク_Debug
            // 
            this.buttonブックマーク_Debug.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonブックマーク_Debug.Location = new System.Drawing.Point(377, 62);
            this.buttonブックマーク_Debug.Name = "buttonブックマーク_Debug";
            this.buttonブックマーク_Debug.Size = new System.Drawing.Size(106, 45);
            this.buttonブックマーク_Debug.TabIndex = 3;
            this.buttonブックマーク_Debug.Text = "ブックマーク";
            this.buttonブックマーク_Debug.UseVisualStyleBackColor = true;
            this.buttonブックマーク_Debug.Click += new System.EventHandler(this.buttonブックマーク_Debug_Click);
            // 
            // buttonいいね_Debug
            // 
            this.buttonいいね_Debug.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonいいね_Debug.Location = new System.Drawing.Point(489, 62);
            this.buttonいいね_Debug.Name = "buttonいいね_Debug";
            this.buttonいいね_Debug.Size = new System.Drawing.Size(106, 45);
            this.buttonいいね_Debug.TabIndex = 2;
            this.buttonいいね_Debug.Text = "いいね";
            this.buttonいいね_Debug.UseVisualStyleBackColor = true;
            this.buttonいいね_Debug.Click += new System.EventHandler(this.buttonいいね_Debug_Click);
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.dataGridViewComment);
            this.groupBox1.Controls.Add(this.buttonコメント_Debug);
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
            // buttonコメント_Debug
            // 
            this.buttonコメント_Debug.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonコメント_Debug.Location = new System.Drawing.Point(619, 26);
            this.buttonコメント_Debug.Name = "buttonコメント_Debug";
            this.buttonコメント_Debug.Size = new System.Drawing.Size(106, 45);
            this.buttonコメント_Debug.TabIndex = 4;
            this.buttonコメント_Debug.Text = "コメント";
            this.buttonコメント_Debug.UseVisualStyleBackColor = true;
            this.buttonコメント_Debug.Click += new System.EventHandler(this.buttonコメント_Debug_Click);
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
            this.textBoxLog.Font = new System.Drawing.Font("Meiryo UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(128)));
            this.textBoxLog.Location = new System.Drawing.Point(798, 42);
            this.textBoxLog.Multiline = true;
            this.textBoxLog.Name = "textBoxLog";
            this.textBoxLog.ScrollBars = System.Windows.Forms.ScrollBars.Both;
            this.textBoxLog.Size = new System.Drawing.Size(606, 642);
            this.textBoxLog.TabIndex = 1;
            // 
            // tabPageいいねブックマーク
            // 
            this.tabPageいいねブックマーク.Controls.Add(this.buttonいいねブックマーク実行);
            this.tabPageいいねブックマーク.Controls.Add(this.dataGridViewいいねリスト);
            this.tabPageいいねブックマーク.Controls.Add(this.groupBox3);
            this.tabPageいいねブックマーク.Location = new System.Drawing.Point(4, 28);
            this.tabPageいいねブックマーク.Name = "tabPageいいねブックマーク";
            this.tabPageいいねブックマーク.Size = new System.Drawing.Size(760, 642);
            this.tabPageいいねブックマーク.TabIndex = 2;
            this.tabPageいいねブックマーク.Text = "いいね・ブックマーク";
            this.tabPageいいねブックマーク.UseVisualStyleBackColor = true;
            // 
            // groupBox3
            // 
            this.groupBox3.Controls.Add(this.textBoxUrlTweetID);
            this.groupBox3.Controls.Add(this.label2);
            this.groupBox3.Controls.Add(this.groupBox5);
            this.groupBox3.Controls.Add(this.buttonいいねリスト作成);
            this.groupBox3.Controls.Add(this.checkBox_15分以内に履歴のある無料アカウントを除外する);
            this.groupBox3.Controls.Add(this.groupBox4);
            this.groupBox3.Location = new System.Drawing.Point(3, 3);
            this.groupBox3.Name = "groupBox3";
            this.groupBox3.Size = new System.Drawing.Size(742, 165);
            this.groupBox3.TabIndex = 0;
            this.groupBox3.TabStop = false;
            this.groupBox3.Text = "基本設定";
            // 
            // radioButtonいいね件数50
            // 
            this.radioButtonいいね件数50.AutoSize = true;
            this.radioButtonいいね件数50.Location = new System.Drawing.Point(6, 26);
            this.radioButtonいいね件数50.Name = "radioButtonいいね件数50";
            this.radioButtonいいね件数50.Size = new System.Drawing.Size(60, 23);
            this.radioButtonいいね件数50.TabIndex = 0;
            this.radioButtonいいね件数50.TabStop = true;
            this.radioButtonいいね件数50.Text = "50件";
            this.radioButtonいいね件数50.UseVisualStyleBackColor = true;
            // 
            // radioButtonいいね件数100
            // 
            this.radioButtonいいね件数100.AutoSize = true;
            this.radioButtonいいね件数100.Location = new System.Drawing.Point(72, 26);
            this.radioButtonいいね件数100.Name = "radioButtonいいね件数100";
            this.radioButtonいいね件数100.Size = new System.Drawing.Size(69, 23);
            this.radioButtonいいね件数100.TabIndex = 1;
            this.radioButtonいいね件数100.TabStop = true;
            this.radioButtonいいね件数100.Text = "100件";
            this.radioButtonいいね件数100.UseVisualStyleBackColor = true;
            // 
            // radioButtonいいね件数200
            // 
            this.radioButtonいいね件数200.AutoSize = true;
            this.radioButtonいいね件数200.Location = new System.Drawing.Point(147, 26);
            this.radioButtonいいね件数200.Name = "radioButtonいいね件数200";
            this.radioButtonいいね件数200.Size = new System.Drawing.Size(69, 23);
            this.radioButtonいいね件数200.TabIndex = 2;
            this.radioButtonいいね件数200.TabStop = true;
            this.radioButtonいいね件数200.Text = "200件";
            this.radioButtonいいね件数200.UseVisualStyleBackColor = true;
            // 
            // radioButtonいいね件数その他
            // 
            this.radioButtonいいね件数その他.AutoSize = true;
            this.radioButtonいいね件数その他.Location = new System.Drawing.Point(222, 31);
            this.radioButtonいいね件数その他.Name = "radioButtonいいね件数その他";
            this.radioButtonいいね件数その他.Size = new System.Drawing.Size(14, 13);
            this.radioButtonいいね件数その他.TabIndex = 3;
            this.radioButtonいいね件数その他.TabStop = true;
            this.radioButtonいいね件数その他.UseVisualStyleBackColor = true;
            // 
            // textBox1
            // 
            this.textBox1.Location = new System.Drawing.Point(242, 25);
            this.textBox1.Name = "textBox1";
            this.textBox1.Size = new System.Drawing.Size(92, 27);
            this.textBox1.TabIndex = 1;
            // 
            // groupBox4
            // 
            this.groupBox4.Controls.Add(this.textBox1);
            this.groupBox4.Controls.Add(this.radioButtonいいね件数50);
            this.groupBox4.Controls.Add(this.radioButtonいいね件数その他);
            this.groupBox4.Controls.Add(this.radioButtonいいね件数100);
            this.groupBox4.Controls.Add(this.radioButtonいいね件数200);
            this.groupBox4.Location = new System.Drawing.Point(183, 26);
            this.groupBox4.Name = "groupBox4";
            this.groupBox4.Size = new System.Drawing.Size(340, 64);
            this.groupBox4.TabIndex = 1;
            this.groupBox4.TabStop = false;
            this.groupBox4.Text = "件数設定";
            // 
            // checkBox_15分以内に履歴のある無料アカウントを除外する
            // 
            this.checkBox_15分以内に履歴のある無料アカウントを除外する.AutoSize = true;
            this.checkBox_15分以内に履歴のある無料アカウントを除外する.Checked = true;
            this.checkBox_15分以内に履歴のある無料アカウントを除外する.CheckState = System.Windows.Forms.CheckState.Checked;
            this.checkBox_15分以内に履歴のある無料アカウントを除外する.Location = new System.Drawing.Point(10, 96);
            this.checkBox_15分以内に履歴のある無料アカウントを除外する.Name = "checkBox_15分以内に履歴のある無料アカウントを除外する";
            this.checkBox_15分以内に履歴のある無料アカウントを除外する.Size = new System.Drawing.Size(318, 23);
            this.checkBox_15分以内に履歴のある無料アカウントを除外する.TabIndex = 2;
            this.checkBox_15分以内に履歴のある無料アカウントを除外する.Text = "15分以内に履歴のある無料アカウントを除外する";
            this.checkBox_15分以内に履歴のある無料アカウントを除外する.UseVisualStyleBackColor = true;
            // 
            // buttonいいねリスト作成
            // 
            this.buttonいいねリスト作成.Location = new System.Drawing.Point(633, 108);
            this.buttonいいねリスト作成.Name = "buttonいいねリスト作成";
            this.buttonいいねリスト作成.Size = new System.Drawing.Size(103, 44);
            this.buttonいいねリスト作成.TabIndex = 1;
            this.buttonいいねリスト作成.Text = "リスト作成";
            this.buttonいいねリスト作成.UseVisualStyleBackColor = true;
            this.buttonいいねリスト作成.Click += new System.EventHandler(this.buttonいいねリスト作成_Click);
            // 
            // dataGridViewいいねリスト
            // 
            this.dataGridViewいいねリスト.AllowUserToAddRows = false;
            this.dataGridViewいいねリスト.AllowUserToDeleteRows = false;
            this.dataGridViewいいねリスト.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridViewいいねリスト.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.dataGridViewTextBoxColumn1,
            this.dataGridViewTextBoxColumn2,
            this.dataGridViewTextBoxColumn3,
            this.dataGridViewTextBoxColumn4,
            this.dataGridViewTextBoxColumn5,
            this.dataGridViewTextBoxColumn6,
            this.dataGridViewTextBoxColumn7,
            this.dataGridViewTextBoxColumn8,
            this.dataGridViewTextBoxColumn9,
            this.dataGridViewTextBoxColumn10,
            this.dataGridViewCheckBoxColumn1});
            this.dataGridViewいいねリスト.Location = new System.Drawing.Point(3, 174);
            this.dataGridViewいいねリスト.MultiSelect = false;
            this.dataGridViewいいねリスト.Name = "dataGridViewいいねリスト";
            this.dataGridViewいいねリスト.RowHeadersVisible = false;
            this.dataGridViewいいねリスト.RowTemplate.Height = 21;
            this.dataGridViewいいねリスト.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridViewいいねリスト.Size = new System.Drawing.Size(742, 415);
            this.dataGridViewいいねリスト.TabIndex = 2;
            // 
            // dataGridViewTextBoxColumn1
            // 
            this.dataGridViewTextBoxColumn1.DataPropertyName = "Id";
            this.dataGridViewTextBoxColumn1.HeaderText = "Id";
            this.dataGridViewTextBoxColumn1.Name = "dataGridViewTextBoxColumn1";
            // 
            // dataGridViewTextBoxColumn2
            // 
            this.dataGridViewTextBoxColumn2.DataPropertyName = "UserId";
            this.dataGridViewTextBoxColumn2.HeaderText = "UserId";
            this.dataGridViewTextBoxColumn2.Name = "dataGridViewTextBoxColumn2";
            // 
            // dataGridViewTextBoxColumn3
            // 
            this.dataGridViewTextBoxColumn3.DataPropertyName = "Name";
            this.dataGridViewTextBoxColumn3.HeaderText = "Name";
            this.dataGridViewTextBoxColumn3.Name = "dataGridViewTextBoxColumn3";
            // 
            // dataGridViewTextBoxColumn4
            // 
            this.dataGridViewTextBoxColumn4.DataPropertyName = "LoginId";
            this.dataGridViewTextBoxColumn4.HeaderText = "ログインID";
            this.dataGridViewTextBoxColumn4.Name = "dataGridViewTextBoxColumn4";
            // 
            // dataGridViewTextBoxColumn5
            // 
            this.dataGridViewTextBoxColumn5.DataPropertyName = "LoginPass";
            this.dataGridViewTextBoxColumn5.HeaderText = "ログインパス";
            this.dataGridViewTextBoxColumn5.Name = "dataGridViewTextBoxColumn5";
            // 
            // dataGridViewTextBoxColumn6
            // 
            this.dataGridViewTextBoxColumn6.DataPropertyName = "ApiKey";
            this.dataGridViewTextBoxColumn6.HeaderText = "ApiKey";
            this.dataGridViewTextBoxColumn6.Name = "dataGridViewTextBoxColumn6";
            // 
            // dataGridViewTextBoxColumn7
            // 
            this.dataGridViewTextBoxColumn7.DataPropertyName = "ApiKeySecret";
            this.dataGridViewTextBoxColumn7.HeaderText = "ApiKeySecret";
            this.dataGridViewTextBoxColumn7.Name = "dataGridViewTextBoxColumn7";
            // 
            // dataGridViewTextBoxColumn8
            // 
            this.dataGridViewTextBoxColumn8.DataPropertyName = "AccessToken";
            this.dataGridViewTextBoxColumn8.HeaderText = "AccessToken";
            this.dataGridViewTextBoxColumn8.Name = "dataGridViewTextBoxColumn8";
            // 
            // dataGridViewTextBoxColumn9
            // 
            this.dataGridViewTextBoxColumn9.DataPropertyName = "BearerToken";
            this.dataGridViewTextBoxColumn9.HeaderText = "BearerToken";
            this.dataGridViewTextBoxColumn9.Name = "dataGridViewTextBoxColumn9";
            // 
            // dataGridViewTextBoxColumn10
            // 
            this.dataGridViewTextBoxColumn10.DataPropertyName = "RefreshToken";
            this.dataGridViewTextBoxColumn10.HeaderText = "RefreshToken";
            this.dataGridViewTextBoxColumn10.Name = "dataGridViewTextBoxColumn10";
            // 
            // dataGridViewCheckBoxColumn1
            // 
            this.dataGridViewCheckBoxColumn1.DataPropertyName = "Enable";
            this.dataGridViewCheckBoxColumn1.FalseValue = "False";
            this.dataGridViewCheckBoxColumn1.HeaderText = "有効";
            this.dataGridViewCheckBoxColumn1.Name = "dataGridViewCheckBoxColumn1";
            this.dataGridViewCheckBoxColumn1.TrueValue = "True";
            // 
            // groupBox5
            // 
            this.groupBox5.Controls.Add(this.radioButtonいいね);
            this.groupBox5.Controls.Add(this.radioButtonブックマーク);
            this.groupBox5.Location = new System.Drawing.Point(4, 26);
            this.groupBox5.Name = "groupBox5";
            this.groupBox5.Size = new System.Drawing.Size(173, 64);
            this.groupBox5.TabIndex = 3;
            this.groupBox5.TabStop = false;
            this.groupBox5.Text = "モード設定";
            // 
            // radioButtonいいね
            // 
            this.radioButtonいいね.AutoSize = true;
            this.radioButtonいいね.Location = new System.Drawing.Point(6, 26);
            this.radioButtonいいね.Name = "radioButtonいいね";
            this.radioButtonいいね.Size = new System.Drawing.Size(64, 23);
            this.radioButtonいいね.TabIndex = 0;
            this.radioButtonいいね.TabStop = true;
            this.radioButtonいいね.Text = "いいね";
            this.radioButtonいいね.UseVisualStyleBackColor = true;
            // 
            // radioButtonブックマーク
            // 
            this.radioButtonブックマーク.AutoSize = true;
            this.radioButtonブックマーク.Location = new System.Drawing.Point(72, 26);
            this.radioButtonブックマーク.Name = "radioButtonブックマーク";
            this.radioButtonブックマーク.Size = new System.Drawing.Size(90, 23);
            this.radioButtonブックマーク.TabIndex = 1;
            this.radioButtonブックマーク.TabStop = true;
            this.radioButtonブックマーク.Text = "ブックマーク";
            this.radioButtonブックマーク.UseVisualStyleBackColor = true;
            // 
            // textBoxUrlTweetID
            // 
            this.textBoxUrlTweetID.Location = new System.Drawing.Point(119, 125);
            this.textBoxUrlTweetID.Name = "textBoxUrlTweetID";
            this.textBoxUrlTweetID.Size = new System.Drawing.Size(470, 27);
            this.textBoxUrlTweetID.TabIndex = 5;
            // 
            // label2
            // 
            this.label2.AutoSize = true;
            this.label2.Location = new System.Drawing.Point(5, 128);
            this.label2.Name = "label2";
            this.label2.Size = new System.Drawing.Size(108, 19);
            this.label2.TabIndex = 4;
            this.label2.Text = "URL・TweetID";
            // 
            // buttonいいねブックマーク実行
            // 
            this.buttonいいねブックマーク実行.Location = new System.Drawing.Point(642, 595);
            this.buttonいいねブックマーク実行.Name = "buttonいいねブックマーク実行";
            this.buttonいいねブックマーク実行.Size = new System.Drawing.Size(103, 44);
            this.buttonいいねブックマーク実行.TabIndex = 3;
            this.buttonいいねブックマーク実行.Text = "実行";
            this.buttonいいねブックマーク実行.UseVisualStyleBackColor = true;
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
            this.tabPageいいねブックマーク.ResumeLayout(false);
            this.groupBox3.ResumeLayout(false);
            this.groupBox3.PerformLayout();
            this.groupBox4.ResumeLayout(false);
            this.groupBox4.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewいいねリスト)).EndInit();
            this.groupBox5.ResumeLayout(false);
            this.groupBox5.PerformLayout();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TabControl tabControl;
        private System.Windows.Forms.TabPage tabPageデバッグ;
        private System.Windows.Forms.TabPage tabPage履歴;
        private System.Windows.Forms.ComboBox comboBoxUserMaster;
        private System.Windows.Forms.Button buttonブックマーク_Debug;
        private System.Windows.Forms.Button buttonいいね_Debug;
        private System.Windows.Forms.DataGridView dataGridViewAccount;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.DataGridView dataGridViewComment;
        private System.Windows.Forms.Button buttonコメント_Debug;
        private System.Windows.Forms.GroupBox groupBox2;
        private System.Windows.Forms.TextBox textBoxUrlTweetID_Debug;
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
        private System.Windows.Forms.TabPage tabPageいいねブックマーク;
        private System.Windows.Forms.GroupBox groupBox3;
        private System.Windows.Forms.Button buttonいいねリスト作成;
        private System.Windows.Forms.CheckBox checkBox_15分以内に履歴のある無料アカウントを除外する;
        private System.Windows.Forms.GroupBox groupBox4;
        private System.Windows.Forms.TextBox textBox1;
        private System.Windows.Forms.RadioButton radioButtonいいね件数50;
        private System.Windows.Forms.RadioButton radioButtonいいね件数その他;
        private System.Windows.Forms.RadioButton radioButtonいいね件数100;
        private System.Windows.Forms.RadioButton radioButtonいいね件数200;
        private System.Windows.Forms.DataGridView dataGridViewいいねリスト;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn1;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn2;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn3;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn4;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn5;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn6;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn7;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn8;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn9;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewTextBoxColumn10;
        private System.Windows.Forms.DataGridViewCheckBoxColumn dataGridViewCheckBoxColumn1;
        private System.Windows.Forms.TextBox textBoxUrlTweetID;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.GroupBox groupBox5;
        private System.Windows.Forms.RadioButton radioButtonいいね;
        private System.Windows.Forms.RadioButton radioButtonブックマーク;
        private System.Windows.Forms.Button buttonいいねブックマーク実行;
    }
}

