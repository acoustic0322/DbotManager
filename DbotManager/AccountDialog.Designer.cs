namespace DbotManager
{
    partial class AccountDialog
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
            this.groupBox6 = new System.Windows.Forms.GroupBox();
            this.buttonGetBearerToken = new System.Windows.Forms.Button();
            this.buttonGetAccessToken = new System.Windows.Forms.Button();
            this.checkBoxツイート = new System.Windows.Forms.CheckBox();
            this.checkBoxリプライ = new System.Windows.Forms.CheckBox();
            this.checkBoxブックマーク = new System.Windows.Forms.CheckBox();
            this.checkBoxいいね = new System.Windows.Forms.CheckBox();
            this.label11 = new System.Windows.Forms.Label();
            this.textBoxRefreshToken = new System.Windows.Forms.TextBox();
            this.label12 = new System.Windows.Forms.Label();
            this.textBoxBearerToken = new System.Windows.Forms.TextBox();
            this.label9 = new System.Windows.Forms.Label();
            this.textBoxAccessTokenSecret = new System.Windows.Forms.TextBox();
            this.label10 = new System.Windows.Forms.Label();
            this.textBoxAccessToken = new System.Windows.Forms.TextBox();
            this.label7 = new System.Windows.Forms.Label();
            this.textBoxClientSecret = new System.Windows.Forms.TextBox();
            this.label8 = new System.Windows.Forms.Label();
            this.textBoxClientId = new System.Windows.Forms.TextBox();
            this.checkBox有料アカウント = new System.Windows.Forms.CheckBox();
            this.label6 = new System.Windows.Forms.Label();
            this.textBoxApiKeySecret = new System.Windows.Forms.TextBox();
            this.label5 = new System.Windows.Forms.Label();
            this.textBoxApiKey = new System.Windows.Forms.TextBox();
            this.label4 = new System.Windows.Forms.Label();
            this.textBoxLogInPass = new System.Windows.Forms.TextBox();
            this.label3 = new System.Windows.Forms.Label();
            this.textBoxLogInId = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.textBoxName = new System.Windows.Forms.TextBox();
            this.buttonアカウント保存 = new System.Windows.Forms.Button();
            this.buttonアカウント追加 = new System.Windows.Forms.Button();
            this.buttonアカウント削除 = new System.Windows.Forms.Button();
            this.checkBox有効 = new System.Windows.Forms.CheckBox();
            this.textBoxUrlTweetID = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.buttonExe = new System.Windows.Forms.Button();
            this.buttonClose = new System.Windows.Forms.Button();
            this.dataGridViewAccount = new System.Windows.Forms.DataGridView();
            this.AccountMaster_Id = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_UserId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_Name = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_LoginId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_LoginPass = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_ApiKey = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_ApiKeySecret = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_ClientId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_ClientSecret = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_AccessToken = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_AccessTokenSecret = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_BearerToken = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_RefreshToken = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.AccountMaster_Enable = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.AccountMaster_Paid = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.AccountMaster_Like = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.AccountMaster_Bookmark = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.AccountMaster_Reply = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.AccountMaster_Tweet = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.comboBoxUserMaster = new System.Windows.Forms.ComboBox();
            this.groupBox6.SuspendLayout();
            this.groupBox1.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewAccount)).BeginInit();
            this.SuspendLayout();
            // 
            // groupBox6
            // 
            this.groupBox6.Controls.Add(this.buttonGetBearerToken);
            this.groupBox6.Controls.Add(this.buttonGetAccessToken);
            this.groupBox6.Controls.Add(this.checkBoxツイート);
            this.groupBox6.Controls.Add(this.checkBoxリプライ);
            this.groupBox6.Controls.Add(this.checkBoxブックマーク);
            this.groupBox6.Controls.Add(this.checkBoxいいね);
            this.groupBox6.Controls.Add(this.label11);
            this.groupBox6.Controls.Add(this.textBoxRefreshToken);
            this.groupBox6.Controls.Add(this.label12);
            this.groupBox6.Controls.Add(this.textBoxBearerToken);
            this.groupBox6.Controls.Add(this.label9);
            this.groupBox6.Controls.Add(this.textBoxAccessTokenSecret);
            this.groupBox6.Controls.Add(this.label10);
            this.groupBox6.Controls.Add(this.textBoxAccessToken);
            this.groupBox6.Controls.Add(this.label7);
            this.groupBox6.Controls.Add(this.textBoxClientSecret);
            this.groupBox6.Controls.Add(this.label8);
            this.groupBox6.Controls.Add(this.textBoxClientId);
            this.groupBox6.Controls.Add(this.checkBox有料アカウント);
            this.groupBox6.Controls.Add(this.label6);
            this.groupBox6.Controls.Add(this.textBoxApiKeySecret);
            this.groupBox6.Controls.Add(this.label5);
            this.groupBox6.Controls.Add(this.textBoxApiKey);
            this.groupBox6.Controls.Add(this.label4);
            this.groupBox6.Controls.Add(this.textBoxLogInPass);
            this.groupBox6.Controls.Add(this.label3);
            this.groupBox6.Controls.Add(this.textBoxLogInId);
            this.groupBox6.Controls.Add(this.label1);
            this.groupBox6.Controls.Add(this.textBoxName);
            this.groupBox6.Controls.Add(this.buttonアカウント保存);
            this.groupBox6.Controls.Add(this.buttonアカウント追加);
            this.groupBox6.Controls.Add(this.buttonアカウント削除);
            this.groupBox6.Controls.Add(this.checkBox有効);
            this.groupBox6.Location = new System.Drawing.Point(663, 14);
            this.groupBox6.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.groupBox6.Name = "groupBox6";
            this.groupBox6.Padding = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.groupBox6.Size = new System.Drawing.Size(623, 569);
            this.groupBox6.TabIndex = 6;
            this.groupBox6.TabStop = false;
            this.groupBox6.Text = "コメント設定";
            // 
            // buttonGetBearerToken
            // 
            this.buttonGetBearerToken.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonGetBearerToken.Location = new System.Drawing.Point(153, 491);
            this.buttonGetBearerToken.Name = "buttonGetBearerToken";
            this.buttonGetBearerToken.Size = new System.Drawing.Size(204, 27);
            this.buttonGetBearerToken.TabIndex = 36;
            this.buttonGetBearerToken.Text = "Bearer/Refresh取得";
            this.buttonGetBearerToken.UseVisualStyleBackColor = true;
            this.buttonGetBearerToken.Click += new System.EventHandler(this.buttonGetBearerToken_Click);
            // 
            // buttonGetAccessToken
            // 
            this.buttonGetAccessToken.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonGetAccessToken.Location = new System.Drawing.Point(8, 491);
            this.buttonGetAccessToken.Name = "buttonGetAccessToken";
            this.buttonGetAccessToken.Size = new System.Drawing.Size(139, 27);
            this.buttonGetAccessToken.TabIndex = 35;
            this.buttonGetAccessToken.Text = "Access取得";
            this.buttonGetAccessToken.UseVisualStyleBackColor = true;
            this.buttonGetAccessToken.Click += new System.EventHandler(this.buttonGetAccessToken_Click);
            // 
            // checkBoxツイート
            // 
            this.checkBoxツイート.AutoSize = true;
            this.checkBoxツイート.Location = new System.Drawing.Point(279, 426);
            this.checkBoxツイート.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.checkBoxツイート.Name = "checkBoxツイート";
            this.checkBoxツイート.Size = new System.Drawing.Size(73, 23);
            this.checkBoxツイート.TabIndex = 34;
            this.checkBoxツイート.Text = "ツイート";
            this.checkBoxツイート.UseVisualStyleBackColor = true;
            // 
            // checkBoxリプライ
            // 
            this.checkBoxリプライ.AutoSize = true;
            this.checkBoxリプライ.Location = new System.Drawing.Point(202, 426);
            this.checkBoxリプライ.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.checkBoxリプライ.Name = "checkBoxリプライ";
            this.checkBoxリプライ.Size = new System.Drawing.Size(69, 23);
            this.checkBoxリプライ.TabIndex = 33;
            this.checkBoxリプライ.Text = "リプライ";
            this.checkBoxリプライ.UseVisualStyleBackColor = true;
            // 
            // checkBoxブックマーク
            // 
            this.checkBoxブックマーク.AutoSize = true;
            this.checkBoxブックマーク.Location = new System.Drawing.Point(103, 426);
            this.checkBoxブックマーク.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.checkBoxブックマーク.Name = "checkBoxブックマーク";
            this.checkBoxブックマーク.Size = new System.Drawing.Size(91, 23);
            this.checkBoxブックマーク.TabIndex = 32;
            this.checkBoxブックマーク.Text = "ブックマーク";
            this.checkBoxブックマーク.UseVisualStyleBackColor = true;
            // 
            // checkBoxいいね
            // 
            this.checkBoxいいね.AutoSize = true;
            this.checkBoxいいね.Location = new System.Drawing.Point(20, 426);
            this.checkBoxいいね.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.checkBoxいいね.Name = "checkBoxいいね";
            this.checkBoxいいね.Size = new System.Drawing.Size(65, 23);
            this.checkBoxいいね.TabIndex = 31;
            this.checkBoxいいね.Text = "いいね";
            this.checkBoxいいね.UseVisualStyleBackColor = true;
            // 
            // label11
            // 
            this.label11.AutoSize = true;
            this.label11.Location = new System.Drawing.Point(18, 361);
            this.label11.Name = "label11";
            this.label11.Size = new System.Drawing.Size(107, 19);
            this.label11.TabIndex = 30;
            this.label11.Text = "RefreshToken";
            // 
            // textBoxRefreshToken
            // 
            this.textBoxRefreshToken.Location = new System.Drawing.Point(130, 358);
            this.textBoxRefreshToken.Name = "textBoxRefreshToken";
            this.textBoxRefreshToken.Size = new System.Drawing.Size(486, 27);
            this.textBoxRefreshToken.TabIndex = 29;
            // 
            // label12
            // 
            this.label12.AutoSize = true;
            this.label12.Location = new System.Drawing.Point(18, 328);
            this.label12.Name = "label12";
            this.label12.Size = new System.Drawing.Size(101, 19);
            this.label12.TabIndex = 28;
            this.label12.Text = "BearerToken";
            // 
            // textBoxBearerToken
            // 
            this.textBoxBearerToken.Location = new System.Drawing.Point(130, 325);
            this.textBoxBearerToken.Name = "textBoxBearerToken";
            this.textBoxBearerToken.Size = new System.Drawing.Size(486, 27);
            this.textBoxBearerToken.TabIndex = 27;
            // 
            // label9
            // 
            this.label9.AutoSize = true;
            this.label9.Location = new System.Drawing.Point(18, 295);
            this.label9.Name = "label9";
            this.label9.Size = new System.Drawing.Size(111, 19);
            this.label9.TabIndex = 26;
            this.label9.Text = "AccessTokenS";
            // 
            // textBoxAccessTokenSecret
            // 
            this.textBoxAccessTokenSecret.Location = new System.Drawing.Point(130, 292);
            this.textBoxAccessTokenSecret.Name = "textBoxAccessTokenSecret";
            this.textBoxAccessTokenSecret.Size = new System.Drawing.Size(486, 27);
            this.textBoxAccessTokenSecret.TabIndex = 25;
            // 
            // label10
            // 
            this.label10.AutoSize = true;
            this.label10.Location = new System.Drawing.Point(18, 262);
            this.label10.Name = "label10";
            this.label10.Size = new System.Drawing.Size(101, 19);
            this.label10.TabIndex = 24;
            this.label10.Text = "AccessToken";
            // 
            // textBoxAccessToken
            // 
            this.textBoxAccessToken.Location = new System.Drawing.Point(130, 259);
            this.textBoxAccessToken.Name = "textBoxAccessToken";
            this.textBoxAccessToken.Size = new System.Drawing.Size(486, 27);
            this.textBoxAccessToken.TabIndex = 23;
            // 
            // label7
            // 
            this.label7.AutoSize = true;
            this.label7.Location = new System.Drawing.Point(18, 229);
            this.label7.Name = "label7";
            this.label7.Size = new System.Drawing.Size(99, 19);
            this.label7.TabIndex = 22;
            this.label7.Text = "ClientSecret";
            // 
            // textBoxClientSecret
            // 
            this.textBoxClientSecret.Location = new System.Drawing.Point(130, 226);
            this.textBoxClientSecret.Name = "textBoxClientSecret";
            this.textBoxClientSecret.Size = new System.Drawing.Size(486, 27);
            this.textBoxClientSecret.TabIndex = 21;
            // 
            // label8
            // 
            this.label8.AutoSize = true;
            this.label8.Location = new System.Drawing.Point(18, 196);
            this.label8.Name = "label8";
            this.label8.Size = new System.Drawing.Size(68, 19);
            this.label8.TabIndex = 20;
            this.label8.Text = "ClientID";
            // 
            // textBoxClientId
            // 
            this.textBoxClientId.Location = new System.Drawing.Point(130, 193);
            this.textBoxClientId.Name = "textBoxClientId";
            this.textBoxClientId.Size = new System.Drawing.Size(486, 27);
            this.textBoxClientId.TabIndex = 19;
            // 
            // checkBox有料アカウント
            // 
            this.checkBox有料アカウント.AutoSize = true;
            this.checkBox有料アカウント.Location = new System.Drawing.Point(103, 393);
            this.checkBox有料アカウント.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.checkBox有料アカウント.Name = "checkBox有料アカウント";
            this.checkBox有料アカウント.Size = new System.Drawing.Size(113, 23);
            this.checkBox有料アカウント.TabIndex = 18;
            this.checkBox有料アカウント.Text = "有料アカウント";
            this.checkBox有料アカウント.UseVisualStyleBackColor = true;
            // 
            // label6
            // 
            this.label6.AutoSize = true;
            this.label6.Location = new System.Drawing.Point(18, 163);
            this.label6.Name = "label6";
            this.label6.Size = new System.Drawing.Size(107, 19);
            this.label6.TabIndex = 17;
            this.label6.Text = "ApiKeySecret";
            // 
            // textBoxApiKeySecret
            // 
            this.textBoxApiKeySecret.Location = new System.Drawing.Point(130, 160);
            this.textBoxApiKeySecret.Name = "textBoxApiKeySecret";
            this.textBoxApiKeySecret.Size = new System.Drawing.Size(486, 27);
            this.textBoxApiKeySecret.TabIndex = 16;
            // 
            // label5
            // 
            this.label5.AutoSize = true;
            this.label5.Location = new System.Drawing.Point(18, 130);
            this.label5.Name = "label5";
            this.label5.Size = new System.Drawing.Size(59, 19);
            this.label5.TabIndex = 15;
            this.label5.Text = "ApiKey";
            // 
            // textBoxApiKey
            // 
            this.textBoxApiKey.Location = new System.Drawing.Point(130, 127);
            this.textBoxApiKey.Name = "textBoxApiKey";
            this.textBoxApiKey.Size = new System.Drawing.Size(486, 27);
            this.textBoxApiKey.TabIndex = 14;
            // 
            // label4
            // 
            this.label4.AutoSize = true;
            this.label4.Location = new System.Drawing.Point(18, 97);
            this.label4.Name = "label4";
            this.label4.Size = new System.Drawing.Size(78, 19);
            this.label4.TabIndex = 13;
            this.label4.Text = "ログインパス";
            // 
            // textBoxLogInPass
            // 
            this.textBoxLogInPass.Location = new System.Drawing.Point(130, 94);
            this.textBoxLogInPass.Name = "textBoxLogInPass";
            this.textBoxLogInPass.Size = new System.Drawing.Size(486, 27);
            this.textBoxLogInPass.TabIndex = 12;
            // 
            // label3
            // 
            this.label3.AutoSize = true;
            this.label3.Location = new System.Drawing.Point(18, 64);
            this.label3.Name = "label3";
            this.label3.Size = new System.Drawing.Size(71, 19);
            this.label3.TabIndex = 11;
            this.label3.Text = "ログインID";
            // 
            // textBoxLogInId
            // 
            this.textBoxLogInId.Location = new System.Drawing.Point(130, 61);
            this.textBoxLogInId.Name = "textBoxLogInId";
            this.textBoxLogInId.Size = new System.Drawing.Size(486, 27);
            this.textBoxLogInId.TabIndex = 10;
            // 
            // label1
            // 
            this.label1.AutoSize = true;
            this.label1.Location = new System.Drawing.Point(16, 31);
            this.label1.Name = "label1";
            this.label1.Size = new System.Drawing.Size(39, 19);
            this.label1.TabIndex = 9;
            this.label1.Text = "名前";
            // 
            // textBoxName
            // 
            this.textBoxName.Location = new System.Drawing.Point(130, 28);
            this.textBoxName.Name = "textBoxName";
            this.textBoxName.Size = new System.Drawing.Size(486, 27);
            this.textBoxName.TabIndex = 8;
            // 
            // buttonアカウント保存
            // 
            this.buttonアカウント保存.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonアカウント保存.Location = new System.Drawing.Point(524, 526);
            this.buttonアカウント保存.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonアカウント保存.Name = "buttonアカウント保存";
            this.buttonアカウント保存.Size = new System.Drawing.Size(92, 33);
            this.buttonアカウント保存.TabIndex = 7;
            this.buttonアカウント保存.Text = "更新";
            this.buttonアカウント保存.UseVisualStyleBackColor = true;
            this.buttonアカウント保存.Click += new System.EventHandler(this.buttonアカウント保存_Click);
            // 
            // buttonアカウント追加
            // 
            this.buttonアカウント追加.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.buttonアカウント追加.Location = new System.Drawing.Point(108, 526);
            this.buttonアカウント追加.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonアカウント追加.Name = "buttonアカウント追加";
            this.buttonアカウント追加.Size = new System.Drawing.Size(92, 33);
            this.buttonアカウント追加.TabIndex = 6;
            this.buttonアカウント追加.Text = "複製・追加";
            this.buttonアカウント追加.UseVisualStyleBackColor = true;
            this.buttonアカウント追加.Click += new System.EventHandler(this.buttonアカウント追加_Click);
            // 
            // buttonアカウント削除
            // 
            this.buttonアカウント削除.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Bottom | System.Windows.Forms.AnchorStyles.Left)));
            this.buttonアカウント削除.Location = new System.Drawing.Point(8, 526);
            this.buttonアカウント削除.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonアカウント削除.Name = "buttonアカウント削除";
            this.buttonアカウント削除.Size = new System.Drawing.Size(92, 33);
            this.buttonアカウント削除.TabIndex = 5;
            this.buttonアカウント削除.Text = "削除";
            this.buttonアカウント削除.UseVisualStyleBackColor = true;
            this.buttonアカウント削除.Click += new System.EventHandler(this.buttonアカウント削除_Click);
            // 
            // checkBox有効
            // 
            this.checkBox有効.AutoSize = true;
            this.checkBox有効.Location = new System.Drawing.Point(21, 393);
            this.checkBox有効.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.checkBox有効.Name = "checkBox有効";
            this.checkBox有効.Size = new System.Drawing.Size(58, 23);
            this.checkBox有効.TabIndex = 1;
            this.checkBox有効.Text = "有効";
            this.checkBox有効.UseVisualStyleBackColor = true;
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
            this.groupBox1.Location = new System.Drawing.Point(13, 589);
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
            this.buttonClose.Location = new System.Drawing.Point(539, 667);
            this.buttonClose.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.buttonClose.Name = "buttonClose";
            this.buttonClose.Size = new System.Drawing.Size(92, 33);
            this.buttonClose.TabIndex = 12;
            this.buttonClose.Text = "閉じる";
            this.buttonClose.UseVisualStyleBackColor = true;
            this.buttonClose.Click += new System.EventHandler(this.buttonClose_Click);
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
            this.AccountMaster_ClientId,
            this.AccountMaster_ClientSecret,
            this.AccountMaster_AccessToken,
            this.AccountMaster_AccessTokenSecret,
            this.AccountMaster_BearerToken,
            this.AccountMaster_RefreshToken,
            this.AccountMaster_Enable,
            this.AccountMaster_Paid,
            this.AccountMaster_Like,
            this.AccountMaster_Bookmark,
            this.AccountMaster_Reply,
            this.AccountMaster_Tweet});
            this.dataGridViewAccount.Location = new System.Drawing.Point(12, 49);
            this.dataGridViewAccount.MultiSelect = false;
            this.dataGridViewAccount.Name = "dataGridViewAccount";
            this.dataGridViewAccount.RowHeadersVisible = false;
            this.dataGridViewAccount.RowTemplate.Height = 21;
            this.dataGridViewAccount.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridViewAccount.Size = new System.Drawing.Size(625, 534);
            this.dataGridViewAccount.TabIndex = 13;
            this.dataGridViewAccount.SelectionChanged += new System.EventHandler(this.dataGridViewAccount_SelectionChanged);
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
            // AccountMaster_ClientId
            // 
            this.AccountMaster_ClientId.DataPropertyName = "ClientId";
            this.AccountMaster_ClientId.HeaderText = "ClientId";
            this.AccountMaster_ClientId.Name = "AccountMaster_ClientId";
            // 
            // AccountMaster_ClientSecret
            // 
            this.AccountMaster_ClientSecret.DataPropertyName = "ClientSecret";
            this.AccountMaster_ClientSecret.HeaderText = "ClientSecret";
            this.AccountMaster_ClientSecret.Name = "AccountMaster_ClientSecret";
            // 
            // AccountMaster_AccessToken
            // 
            this.AccountMaster_AccessToken.DataPropertyName = "AccessToken";
            this.AccountMaster_AccessToken.HeaderText = "AccessToken";
            this.AccountMaster_AccessToken.Name = "AccountMaster_AccessToken";
            // 
            // AccountMaster_AccessTokenSecret
            // 
            this.AccountMaster_AccessTokenSecret.DataPropertyName = "AccessTokenSecret";
            this.AccountMaster_AccessTokenSecret.HeaderText = "AccessTokenSecret";
            this.AccountMaster_AccessTokenSecret.Name = "AccountMaster_AccessTokenSecret";
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
            // AccountMaster_Paid
            // 
            this.AccountMaster_Paid.DataPropertyName = "Paid";
            this.AccountMaster_Paid.FalseValue = "False";
            this.AccountMaster_Paid.HeaderText = "有料";
            this.AccountMaster_Paid.Name = "AccountMaster_Paid";
            this.AccountMaster_Paid.TrueValue = "True";
            // 
            // AccountMaster_Like
            // 
            this.AccountMaster_Like.DataPropertyName = "LikeEnable";
            this.AccountMaster_Like.FalseValue = "False";
            this.AccountMaster_Like.HeaderText = "いいね";
            this.AccountMaster_Like.Name = "AccountMaster_Like";
            this.AccountMaster_Like.TrueValue = "True";
            // 
            // AccountMaster_Bookmark
            // 
            this.AccountMaster_Bookmark.DataPropertyName = "Bookmark";
            this.AccountMaster_Bookmark.FalseValue = "False";
            this.AccountMaster_Bookmark.HeaderText = "ブックマーク";
            this.AccountMaster_Bookmark.Name = "AccountMaster_Bookmark";
            this.AccountMaster_Bookmark.TrueValue = "True";
            // 
            // AccountMaster_Reply
            // 
            this.AccountMaster_Reply.DataPropertyName = "Reply";
            this.AccountMaster_Reply.FalseValue = "False";
            this.AccountMaster_Reply.HeaderText = "リプライ";
            this.AccountMaster_Reply.Name = "AccountMaster_Reply";
            this.AccountMaster_Reply.TrueValue = "True";
            // 
            // AccountMaster_Tweet
            // 
            this.AccountMaster_Tweet.DataPropertyName = "TweetEnable";
            this.AccountMaster_Tweet.FalseValue = "False";
            this.AccountMaster_Tweet.HeaderText = "ツイート";
            this.AccountMaster_Tweet.Name = "AccountMaster_Tweet";
            this.AccountMaster_Tweet.TrueValue = "True";
            // 
            // comboBoxUserMaster
            // 
            this.comboBoxUserMaster.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.comboBoxUserMaster.FormattingEnabled = true;
            this.comboBoxUserMaster.Location = new System.Drawing.Point(12, 14);
            this.comboBoxUserMaster.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.comboBoxUserMaster.Name = "comboBoxUserMaster";
            this.comboBoxUserMaster.Size = new System.Drawing.Size(180, 27);
            this.comboBoxUserMaster.TabIndex = 14;
            this.comboBoxUserMaster.SelectedIndexChanged += new System.EventHandler(this.comboBoxUserMaster_SelectedIndexChanged);
            // 
            // AccountDialog
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 19F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1299, 725);
            this.Controls.Add(this.comboBoxUserMaster);
            this.Controls.Add(this.dataGridViewAccount);
            this.Controls.Add(this.buttonClose);
            this.Controls.Add(this.groupBox1);
            this.Controls.Add(this.groupBox6);
            this.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.MaximizeBox = false;
            this.MinimizeBox = false;
            this.Name = "AccountDialog";
            this.Text = "CommentRegistrationDialog";
            this.Load += new System.EventHandler(this.AccountDialog_Load);
            this.groupBox6.ResumeLayout(false);
            this.groupBox6.PerformLayout();
            this.groupBox1.ResumeLayout(false);
            this.groupBox1.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewAccount)).EndInit();
            this.ResumeLayout(false);

        }

        #endregion
        private System.Windows.Forms.GroupBox groupBox6;
        private System.Windows.Forms.Button buttonアカウント保存;
        private System.Windows.Forms.Button buttonアカウント追加;
        private System.Windows.Forms.Button buttonアカウント削除;
        private System.Windows.Forms.CheckBox checkBox有効;
        private System.Windows.Forms.TextBox textBoxUrlTweetID;
        private System.Windows.Forms.Label label2;
        private System.Windows.Forms.GroupBox groupBox1;
        private System.Windows.Forms.Button buttonExe;
        private System.Windows.Forms.Button buttonClose;
        private System.Windows.Forms.DataGridView dataGridViewAccount;
        private System.Windows.Forms.Label label11;
        private System.Windows.Forms.TextBox textBoxRefreshToken;
        private System.Windows.Forms.Label label12;
        private System.Windows.Forms.TextBox textBoxBearerToken;
        private System.Windows.Forms.Label label9;
        private System.Windows.Forms.TextBox textBoxAccessTokenSecret;
        private System.Windows.Forms.Label label10;
        private System.Windows.Forms.TextBox textBoxAccessToken;
        private System.Windows.Forms.Label label7;
        private System.Windows.Forms.TextBox textBoxClientSecret;
        private System.Windows.Forms.Label label8;
        private System.Windows.Forms.TextBox textBoxClientId;
        private System.Windows.Forms.CheckBox checkBox有料アカウント;
        private System.Windows.Forms.Label label6;
        private System.Windows.Forms.TextBox textBoxApiKeySecret;
        private System.Windows.Forms.Label label5;
        private System.Windows.Forms.TextBox textBoxApiKey;
        private System.Windows.Forms.Label label4;
        private System.Windows.Forms.TextBox textBoxLogInPass;
        private System.Windows.Forms.Label label3;
        private System.Windows.Forms.TextBox textBoxLogInId;
        private System.Windows.Forms.Label label1;
        private System.Windows.Forms.TextBox textBoxName;
        private System.Windows.Forms.CheckBox checkBoxいいね;
        private System.Windows.Forms.CheckBox checkBoxツイート;
        private System.Windows.Forms.CheckBox checkBoxリプライ;
        private System.Windows.Forms.CheckBox checkBoxブックマーク;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_Id;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_UserId;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_Name;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_LoginId;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_LoginPass;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_ApiKey;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_ApiKeySecret;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_ClientId;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_ClientSecret;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_AccessToken;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_AccessTokenSecret;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_BearerToken;
        private System.Windows.Forms.DataGridViewTextBoxColumn AccountMaster_RefreshToken;
        private System.Windows.Forms.DataGridViewCheckBoxColumn AccountMaster_Enable;
        private System.Windows.Forms.DataGridViewCheckBoxColumn AccountMaster_Paid;
        private System.Windows.Forms.DataGridViewCheckBoxColumn AccountMaster_Like;
        private System.Windows.Forms.DataGridViewCheckBoxColumn AccountMaster_Bookmark;
        private System.Windows.Forms.DataGridViewCheckBoxColumn AccountMaster_Reply;
        private System.Windows.Forms.DataGridViewCheckBoxColumn AccountMaster_Tweet;
        private System.Windows.Forms.Button buttonGetBearerToken;
        private System.Windows.Forms.Button buttonGetAccessToken;
        private System.Windows.Forms.ComboBox comboBoxUserMaster;
    }
}