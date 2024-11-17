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
            this.tabPageいいねブックマーク = new System.Windows.Forms.TabPage();
            this.buttonいいねブックマーク実行 = new System.Windows.Forms.Button();
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
            this.groupBox3 = new System.Windows.Forms.GroupBox();
            this.textBoxUrlTweetID = new System.Windows.Forms.TextBox();
            this.label2 = new System.Windows.Forms.Label();
            this.groupBox5 = new System.Windows.Forms.GroupBox();
            this.checkBoxリプライ = new System.Windows.Forms.CheckBox();
            this.checkBoxブックマーク = new System.Windows.Forms.CheckBox();
            this.checkBoxいいね = new System.Windows.Forms.CheckBox();
            this.buttonいいねリスト作成 = new System.Windows.Forms.Button();
            this.checkBox_15分以内に履歴のある無料アカウントを除外する = new System.Windows.Forms.CheckBox();
            this.groupBox4 = new System.Windows.Forms.GroupBox();
            this.textBoxいいね件数 = new System.Windows.Forms.TextBox();
            this.radioButtonいいね件数50 = new System.Windows.Forms.RadioButton();
            this.radioButtonいいね件数その他 = new System.Windows.Forms.RadioButton();
            this.radioButtonいいね件数100 = new System.Windows.Forms.RadioButton();
            this.radioButtonいいね件数200 = new System.Windows.Forms.RadioButton();
            this.tabPageツイート = new System.Windows.Forms.TabPage();
            this.groupBox1 = new System.Windows.Forms.GroupBox();
            this.groupBox6 = new System.Windows.Forms.GroupBox();
            this.textBoxコメント_コメントID = new System.Windows.Forms.TextBox();
            this.buttonコメント保存 = new System.Windows.Forms.Button();
            this.buttonコメント_Debug = new System.Windows.Forms.Button();
            this.buttonコメント追加 = new System.Windows.Forms.Button();
            this.buttonコメント削除 = new System.Windows.Forms.Button();
            this.checkBoxコメント_全アカウント共通 = new System.Windows.Forms.CheckBox();
            this.checkBoxコメント有効 = new System.Windows.Forms.CheckBox();
            this.textBoxコメント = new System.Windows.Forms.TextBox();
            this.dataGridViewComment = new System.Windows.Forms.DataGridView();
            this.CommentMaster_Id = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_UserId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_AccountId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_Comment = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.CommentMaster_Enable = new System.Windows.Forms.DataGridViewCheckBoxColumn();
            this.tabPageデバッグ = new System.Windows.Forms.TabPage();
            this.button1 = new System.Windows.Forms.Button();
            this.buttonDebugGetBearerToken = new System.Windows.Forms.Button();
            this.buttonDebugGetAccessToken = new System.Windows.Forms.Button();
            this.groupBox2 = new System.Windows.Forms.GroupBox();
            this.buttonリプライ_Debug = new System.Windows.Forms.Button();
            this.textBoxUrlTweetID_Debug = new System.Windows.Forms.TextBox();
            this.label1 = new System.Windows.Forms.Label();
            this.buttonブックマーク_Debug = new System.Windows.Forms.Button();
            this.buttonいいね_Debug = new System.Windows.Forms.Button();
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
            this.tabPage履歴 = new System.Windows.Forms.TabPage();
            this.dataGridViewTweetHistory = new System.Windows.Forms.DataGridView();
            this.comboBoxUserMaster = new System.Windows.Forms.ComboBox();
            this.textBoxRenew = new System.Windows.Forms.TextBox();
            this.buttonクリアlog = new System.Windows.Forms.Button();
            this.textBoxコメント_UserID = new System.Windows.Forms.TextBox();
            this.textBoxコメント_AccountId = new System.Windows.Forms.TextBox();
            this.tabControl.SuspendLayout();
            this.tabPageいいねブックマーク.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewいいねリスト)).BeginInit();
            this.groupBox3.SuspendLayout();
            this.groupBox5.SuspendLayout();
            this.groupBox4.SuspendLayout();
            this.tabPageツイート.SuspendLayout();
            this.groupBox1.SuspendLayout();
            this.groupBox6.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewComment)).BeginInit();
            this.tabPageデバッグ.SuspendLayout();
            this.groupBox2.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewAccount)).BeginInit();
            this.tabPage履歴.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewTweetHistory)).BeginInit();
            this.SuspendLayout();
            // 
            // tabControl
            // 
            this.tabControl.Controls.Add(this.tabPageいいねブックマーク);
            this.tabControl.Controls.Add(this.tabPageツイート);
            this.tabControl.Controls.Add(this.tabPageデバッグ);
            this.tabControl.Controls.Add(this.tabPage履歴);
            this.tabControl.Font = new System.Drawing.Font("Meiryo UI", 11.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(128)));
            this.tabControl.Location = new System.Drawing.Point(13, 51);
            this.tabControl.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabControl.Name = "tabControl";
            this.tabControl.SelectedIndex = 0;
            this.tabControl.Size = new System.Drawing.Size(768, 637);
            this.tabControl.TabIndex = 0;
            // 
            // tabPageいいねブックマーク
            // 
            this.tabPageいいねブックマーク.Controls.Add(this.buttonいいねブックマーク実行);
            this.tabPageいいねブックマーク.Controls.Add(this.dataGridViewいいねリスト);
            this.tabPageいいねブックマーク.Controls.Add(this.groupBox3);
            this.tabPageいいねブックマーク.Location = new System.Drawing.Point(4, 28);
            this.tabPageいいねブックマーク.Name = "tabPageいいねブックマーク";
            this.tabPageいいねブックマーク.Size = new System.Drawing.Size(760, 605);
            this.tabPageいいねブックマーク.TabIndex = 2;
            this.tabPageいいねブックマーク.Text = "いいね・ブックマーク・リプライ";
            this.tabPageいいねブックマーク.UseVisualStyleBackColor = true;
            // 
            // buttonいいねブックマーク実行
            // 
            this.buttonいいねブックマーク実行.Location = new System.Drawing.Point(642, 595);
            this.buttonいいねブックマーク実行.Name = "buttonいいねブックマーク実行";
            this.buttonいいねブックマーク実行.Size = new System.Drawing.Size(103, 44);
            this.buttonいいねブックマーク実行.TabIndex = 3;
            this.buttonいいねブックマーク実行.Text = "実行";
            this.buttonいいねブックマーク実行.UseVisualStyleBackColor = true;
            this.buttonいいねブックマーク実行.Click += new System.EventHandler(this.buttonいいねブックマーク実行_Click);
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
            // groupBox5
            // 
            this.groupBox5.Controls.Add(this.checkBoxリプライ);
            this.groupBox5.Controls.Add(this.checkBoxブックマーク);
            this.groupBox5.Controls.Add(this.checkBoxいいね);
            this.groupBox5.Location = new System.Drawing.Point(4, 26);
            this.groupBox5.Name = "groupBox5";
            this.groupBox5.Size = new System.Drawing.Size(297, 64);
            this.groupBox5.TabIndex = 3;
            this.groupBox5.TabStop = false;
            this.groupBox5.Text = "モード設定";
            // 
            // checkBoxリプライ
            // 
            this.checkBoxリプライ.AutoSize = true;
            this.checkBoxリプライ.Location = new System.Drawing.Point(174, 27);
            this.checkBoxリプライ.Name = "checkBoxリプライ";
            this.checkBoxリプライ.Size = new System.Drawing.Size(69, 23);
            this.checkBoxリプライ.TabIndex = 7;
            this.checkBoxリプライ.Text = "リプライ";
            this.checkBoxリプライ.UseVisualStyleBackColor = true;
            // 
            // checkBoxブックマーク
            // 
            this.checkBoxブックマーク.AutoSize = true;
            this.checkBoxブックマーク.Location = new System.Drawing.Point(77, 27);
            this.checkBoxブックマーク.Name = "checkBoxブックマーク";
            this.checkBoxブックマーク.Size = new System.Drawing.Size(91, 23);
            this.checkBoxブックマーク.TabIndex = 6;
            this.checkBoxブックマーク.Text = "ブックマーク";
            this.checkBoxブックマーク.UseVisualStyleBackColor = true;
            // 
            // checkBoxいいね
            // 
            this.checkBoxいいね.AutoSize = true;
            this.checkBoxいいね.Location = new System.Drawing.Point(6, 27);
            this.checkBoxいいね.Name = "checkBoxいいね";
            this.checkBoxいいね.Size = new System.Drawing.Size(65, 23);
            this.checkBoxいいね.TabIndex = 5;
            this.checkBoxいいね.Text = "いいね";
            this.checkBoxいいね.UseVisualStyleBackColor = true;
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
            // groupBox4
            // 
            this.groupBox4.Controls.Add(this.textBoxいいね件数);
            this.groupBox4.Controls.Add(this.radioButtonいいね件数50);
            this.groupBox4.Controls.Add(this.radioButtonいいね件数その他);
            this.groupBox4.Controls.Add(this.radioButtonいいね件数100);
            this.groupBox4.Controls.Add(this.radioButtonいいね件数200);
            this.groupBox4.Location = new System.Drawing.Point(307, 26);
            this.groupBox4.Name = "groupBox4";
            this.groupBox4.Size = new System.Drawing.Size(340, 64);
            this.groupBox4.TabIndex = 1;
            this.groupBox4.TabStop = false;
            this.groupBox4.Text = "件数設定";
            // 
            // textBoxいいね件数
            // 
            this.textBoxいいね件数.Location = new System.Drawing.Point(242, 25);
            this.textBoxいいね件数.Name = "textBoxいいね件数";
            this.textBoxいいね件数.Size = new System.Drawing.Size(92, 27);
            this.textBoxいいね件数.TabIndex = 1;
            // 
            // radioButtonいいね件数50
            // 
            this.radioButtonいいね件数50.AutoSize = true;
            this.radioButtonいいね件数50.Checked = true;
            this.radioButtonいいね件数50.Location = new System.Drawing.Point(6, 26);
            this.radioButtonいいね件数50.Name = "radioButtonいいね件数50";
            this.radioButtonいいね件数50.Size = new System.Drawing.Size(60, 23);
            this.radioButtonいいね件数50.TabIndex = 0;
            this.radioButtonいいね件数50.TabStop = true;
            this.radioButtonいいね件数50.Text = "50件";
            this.radioButtonいいね件数50.UseVisualStyleBackColor = true;
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
            // tabPageツイート
            // 
            this.tabPageツイート.Controls.Add(this.groupBox1);
            this.tabPageツイート.Location = new System.Drawing.Point(4, 28);
            this.tabPageツイート.Name = "tabPageツイート";
            this.tabPageツイート.Size = new System.Drawing.Size(760, 605);
            this.tabPageツイート.TabIndex = 3;
            this.tabPageツイート.Text = "ツイート";
            this.tabPageツイート.UseVisualStyleBackColor = true;
            // 
            // groupBox1
            // 
            this.groupBox1.Controls.Add(this.groupBox6);
            this.groupBox1.Controls.Add(this.dataGridViewComment);
            this.groupBox1.Location = new System.Drawing.Point(13, 14);
            this.groupBox1.Name = "groupBox1";
            this.groupBox1.Size = new System.Drawing.Size(731, 572);
            this.groupBox1.TabIndex = 5;
            this.groupBox1.TabStop = false;
            this.groupBox1.Text = "コメント";
            // 
            // groupBox6
            // 
            this.groupBox6.Controls.Add(this.textBoxコメント_AccountId);
            this.groupBox6.Controls.Add(this.textBoxコメント_UserID);
            this.groupBox6.Controls.Add(this.textBoxコメント_コメントID);
            this.groupBox6.Controls.Add(this.buttonコメント保存);
            this.groupBox6.Controls.Add(this.buttonコメント_Debug);
            this.groupBox6.Controls.Add(this.buttonコメント追加);
            this.groupBox6.Controls.Add(this.buttonコメント削除);
            this.groupBox6.Controls.Add(this.checkBoxコメント_全アカウント共通);
            this.groupBox6.Controls.Add(this.checkBoxコメント有効);
            this.groupBox6.Controls.Add(this.textBoxコメント);
            this.groupBox6.Location = new System.Drawing.Point(6, 26);
            this.groupBox6.Name = "groupBox6";
            this.groupBox6.Size = new System.Drawing.Size(719, 217);
            this.groupBox6.TabIndex = 5;
            this.groupBox6.TabStop = false;
            this.groupBox6.Text = "編集";
            // 
            // textBoxコメント_コメントID
            // 
            this.textBoxコメント_コメントID.Enabled = false;
            this.textBoxコメント_コメントID.Location = new System.Drawing.Point(383, 22);
            this.textBoxコメント_コメントID.Name = "textBoxコメント_コメントID";
            this.textBoxコメント_コメントID.Size = new System.Drawing.Size(106, 27);
            this.textBoxコメント_コメントID.TabIndex = 8;
            // 
            // buttonコメント保存
            // 
            this.buttonコメント保存.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonコメント保存.Location = new System.Drawing.Point(607, 157);
            this.buttonコメント保存.Name = "buttonコメント保存";
            this.buttonコメント保存.Size = new System.Drawing.Size(106, 45);
            this.buttonコメント保存.TabIndex = 7;
            this.buttonコメント保存.Text = "保存";
            this.buttonコメント保存.UseVisualStyleBackColor = true;
            this.buttonコメント保存.Click += new System.EventHandler(this.buttonコメント保存_Click);
            // 
            // buttonコメント_Debug
            // 
            this.buttonコメント_Debug.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonコメント_Debug.Location = new System.Drawing.Point(456, 172);
            this.buttonコメント_Debug.Name = "buttonコメント_Debug";
            this.buttonコメント_Debug.Size = new System.Drawing.Size(106, 45);
            this.buttonコメント_Debug.TabIndex = 4;
            this.buttonコメント_Debug.Text = "コメント";
            this.buttonコメント_Debug.UseVisualStyleBackColor = true;
            this.buttonコメント_Debug.Click += new System.EventHandler(this.buttonコメント_Debug_Click);
            // 
            // buttonコメント追加
            // 
            this.buttonコメント追加.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonコメント追加.Location = new System.Drawing.Point(607, 106);
            this.buttonコメント追加.Name = "buttonコメント追加";
            this.buttonコメント追加.Size = new System.Drawing.Size(106, 45);
            this.buttonコメント追加.TabIndex = 6;
            this.buttonコメント追加.Text = "追加";
            this.buttonコメント追加.UseVisualStyleBackColor = true;
            this.buttonコメント追加.Click += new System.EventHandler(this.buttonコメント追加_Click);
            // 
            // buttonコメント削除
            // 
            this.buttonコメント削除.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonコメント削除.Location = new System.Drawing.Point(607, 55);
            this.buttonコメント削除.Name = "buttonコメント削除";
            this.buttonコメント削除.Size = new System.Drawing.Size(106, 45);
            this.buttonコメント削除.TabIndex = 5;
            this.buttonコメント削除.Text = "削除";
            this.buttonコメント削除.UseVisualStyleBackColor = true;
            this.buttonコメント削除.Click += new System.EventHandler(this.buttonコメント削除_Click);
            // 
            // checkBoxコメント_全アカウント共通
            // 
            this.checkBoxコメント_全アカウント共通.AutoSize = true;
            this.checkBoxコメント_全アカウント共通.Location = new System.Drawing.Point(105, 26);
            this.checkBoxコメント_全アカウント共通.Name = "checkBoxコメント_全アカウント共通";
            this.checkBoxコメント_全アカウント共通.Size = new System.Drawing.Size(128, 23);
            this.checkBoxコメント_全アカウント共通.TabIndex = 2;
            this.checkBoxコメント_全アカウント共通.Text = "全アカウント共通";
            this.checkBoxコメント_全アカウント共通.UseVisualStyleBackColor = true;
            // 
            // checkBoxコメント有効
            // 
            this.checkBoxコメント有効.AutoSize = true;
            this.checkBoxコメント有効.Location = new System.Drawing.Point(26, 26);
            this.checkBoxコメント有効.Name = "checkBoxコメント有効";
            this.checkBoxコメント有効.Size = new System.Drawing.Size(58, 23);
            this.checkBoxコメント有効.TabIndex = 1;
            this.checkBoxコメント有効.Text = "有効";
            this.checkBoxコメント有効.UseVisualStyleBackColor = true;
            // 
            // textBoxコメント
            // 
            this.textBoxコメント.Location = new System.Drawing.Point(26, 55);
            this.textBoxコメント.Multiline = true;
            this.textBoxコメント.Name = "textBoxコメント";
            this.textBoxコメント.Size = new System.Drawing.Size(575, 147);
            this.textBoxコメント.TabIndex = 0;
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
            this.dataGridViewComment.Location = new System.Drawing.Point(6, 249);
            this.dataGridViewComment.Name = "dataGridViewComment";
            this.dataGridViewComment.RowHeadersVisible = false;
            this.dataGridViewComment.RowTemplate.Height = 21;
            this.dataGridViewComment.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridViewComment.Size = new System.Drawing.Size(719, 317);
            this.dataGridViewComment.TabIndex = 4;
            this.dataGridViewComment.SelectionChanged += new System.EventHandler(this.dataGridViewComment_SelectionChanged);
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
            // tabPageデバッグ
            // 
            this.tabPageデバッグ.Controls.Add(this.button1);
            this.tabPageデバッグ.Controls.Add(this.buttonDebugGetBearerToken);
            this.tabPageデバッグ.Controls.Add(this.buttonDebugGetAccessToken);
            this.tabPageデバッグ.Controls.Add(this.groupBox2);
            this.tabPageデバッグ.Controls.Add(this.dataGridViewAccount);
            this.tabPageデバッグ.Location = new System.Drawing.Point(4, 28);
            this.tabPageデバッグ.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabPageデバッグ.Name = "tabPageデバッグ";
            this.tabPageデバッグ.Padding = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabPageデバッグ.Size = new System.Drawing.Size(760, 605);
            this.tabPageデバッグ.TabIndex = 0;
            this.tabPageデバッグ.Text = "デバッグ";
            this.tabPageデバッグ.UseVisualStyleBackColor = true;
            // 
            // button1
            // 
            this.button1.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.button1.Location = new System.Drawing.Point(228, 10);
            this.button1.Name = "button1";
            this.button1.Size = new System.Drawing.Size(139, 27);
            this.button1.TabIndex = 9;
            this.button1.Text = "更新";
            this.button1.UseVisualStyleBackColor = true;
            this.button1.Click += new System.EventHandler(this.button1_Click);
            // 
            // buttonDebugGetBearerToken
            // 
            this.buttonDebugGetBearerToken.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonDebugGetBearerToken.Location = new System.Drawing.Point(518, 9);
            this.buttonDebugGetBearerToken.Name = "buttonDebugGetBearerToken";
            this.buttonDebugGetBearerToken.Size = new System.Drawing.Size(229, 27);
            this.buttonDebugGetBearerToken.TabIndex = 8;
            this.buttonDebugGetBearerToken.Text = "Bearer/RefreshToken取得";
            this.buttonDebugGetBearerToken.UseVisualStyleBackColor = true;
            this.buttonDebugGetBearerToken.Click += new System.EventHandler(this.buttonDebugGetBearerToken_Click);
            // 
            // buttonDebugGetAccessToken
            // 
            this.buttonDebugGetAccessToken.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonDebugGetAccessToken.Location = new System.Drawing.Point(373, 9);
            this.buttonDebugGetAccessToken.Name = "buttonDebugGetAccessToken";
            this.buttonDebugGetAccessToken.Size = new System.Drawing.Size(139, 27);
            this.buttonDebugGetAccessToken.TabIndex = 7;
            this.buttonDebugGetAccessToken.Text = "AccessToken取得";
            this.buttonDebugGetAccessToken.UseVisualStyleBackColor = true;
            this.buttonDebugGetAccessToken.Click += new System.EventHandler(this.buttonDebugGetAccessToken_Click);
            // 
            // groupBox2
            // 
            this.groupBox2.Controls.Add(this.buttonリプライ_Debug);
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
            // buttonリプライ_Debug
            // 
            this.buttonリプライ_Debug.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonリプライ_Debug.Location = new System.Drawing.Point(265, 62);
            this.buttonリプライ_Debug.Name = "buttonリプライ_Debug";
            this.buttonリプライ_Debug.Size = new System.Drawing.Size(106, 45);
            this.buttonリプライ_Debug.TabIndex = 4;
            this.buttonリプライ_Debug.Text = "リプライ";
            this.buttonリプライ_Debug.UseVisualStyleBackColor = true;
            this.buttonリプライ_Debug.Click += new System.EventHandler(this.buttonリプライ_Debug_Click);
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
            this.dataGridViewAccount.Size = new System.Drawing.Size(731, 400);
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
            // tabPage履歴
            // 
            this.tabPage履歴.Controls.Add(this.dataGridViewTweetHistory);
            this.tabPage履歴.Location = new System.Drawing.Point(4, 28);
            this.tabPage履歴.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabPage履歴.Name = "tabPage履歴";
            this.tabPage履歴.Padding = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabPage履歴.Size = new System.Drawing.Size(760, 605);
            this.tabPage履歴.TabIndex = 1;
            this.tabPage履歴.Text = "履歴";
            this.tabPage履歴.UseVisualStyleBackColor = true;
            // 
            // dataGridViewTweetHistory
            // 
            this.dataGridViewTweetHistory.AllowUserToAddRows = false;
            this.dataGridViewTweetHistory.AllowUserToDeleteRows = false;
            this.dataGridViewTweetHistory.AllowUserToResizeRows = false;
            this.dataGridViewTweetHistory.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.AllCells;
            this.dataGridViewTweetHistory.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridViewTweetHistory.Location = new System.Drawing.Point(7, 8);
            this.dataGridViewTweetHistory.Name = "dataGridViewTweetHistory";
            this.dataGridViewTweetHistory.RowHeadersVisible = false;
            this.dataGridViewTweetHistory.RowTemplate.Height = 21;
            this.dataGridViewTweetHistory.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridViewTweetHistory.Size = new System.Drawing.Size(631, 626);
            this.dataGridViewTweetHistory.TabIndex = 0;
            // 
            // comboBoxUserMaster
            // 
            this.comboBoxUserMaster.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.comboBoxUserMaster.FormattingEnabled = true;
            this.comboBoxUserMaster.Location = new System.Drawing.Point(111, 14);
            this.comboBoxUserMaster.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.comboBoxUserMaster.Name = "comboBoxUserMaster";
            this.comboBoxUserMaster.Size = new System.Drawing.Size(180, 27);
            this.comboBoxUserMaster.TabIndex = 0;
            this.comboBoxUserMaster.SelectedIndexChanged += new System.EventHandler(this.comboBoxUserMaster_SelectedIndexChanged);
            // 
            // textBoxRenew
            // 
            this.textBoxRenew.Font = new System.Drawing.Font("Meiryo UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(128)));
            this.textBoxRenew.Location = new System.Drawing.Point(798, 42);
            this.textBoxRenew.Multiline = true;
            this.textBoxRenew.Name = "textBoxRenew";
            this.textBoxRenew.ScrollBars = System.Windows.Forms.ScrollBars.Both;
            this.textBoxRenew.Size = new System.Drawing.Size(606, 589);
            this.textBoxRenew.TabIndex = 1;
            // 
            // buttonクリアlog
            // 
            this.buttonクリアlog.Location = new System.Drawing.Point(798, 637);
            this.buttonクリアlog.Name = "buttonクリアlog";
            this.buttonクリアlog.Size = new System.Drawing.Size(103, 44);
            this.buttonクリアlog.TabIndex = 4;
            this.buttonクリアlog.Text = "クリア";
            this.buttonクリアlog.UseVisualStyleBackColor = true;
            this.buttonクリアlog.Click += new System.EventHandler(this.buttonクリアlog_Click);
            // 
            // textBoxコメント_UserID
            // 
            this.textBoxコメント_UserID.Enabled = false;
            this.textBoxコメント_UserID.Location = new System.Drawing.Point(495, 22);
            this.textBoxコメント_UserID.Name = "textBoxコメント_UserID";
            this.textBoxコメント_UserID.Size = new System.Drawing.Size(106, 27);
            this.textBoxコメント_UserID.TabIndex = 9;
            // 
            // textBoxコメント_AccountId
            // 
            this.textBoxコメント_AccountId.Enabled = false;
            this.textBoxコメント_AccountId.Location = new System.Drawing.Point(607, 22);
            this.textBoxコメント_AccountId.Name = "textBoxコメント_AccountId";
            this.textBoxコメント_AccountId.Size = new System.Drawing.Size(106, 27);
            this.textBoxコメント_AccountId.TabIndex = 10;
            // 
            // Form
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 19F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1416, 712);
            this.Controls.Add(this.buttonクリアlog);
            this.Controls.Add(this.textBoxRenew);
            this.Controls.Add(this.tabControl);
            this.Controls.Add(this.comboBoxUserMaster);
            this.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.Name = "Form";
            this.Text = "Form1";
            this.Load += new System.EventHandler(this.MainForm_Load);
            this.tabControl.ResumeLayout(false);
            this.tabPageいいねブックマーク.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewいいねリスト)).EndInit();
            this.groupBox3.ResumeLayout(false);
            this.groupBox3.PerformLayout();
            this.groupBox5.ResumeLayout(false);
            this.groupBox5.PerformLayout();
            this.groupBox4.ResumeLayout(false);
            this.groupBox4.PerformLayout();
            this.tabPageツイート.ResumeLayout(false);
            this.groupBox1.ResumeLayout(false);
            this.groupBox6.ResumeLayout(false);
            this.groupBox6.PerformLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewComment)).EndInit();
            this.tabPageデバッグ.ResumeLayout(false);
            this.groupBox2.ResumeLayout(false);
            this.groupBox2.PerformLayout();
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
        private System.Windows.Forms.TextBox textBoxRenew;
        private System.Windows.Forms.TabPage tabPageいいねブックマーク;
        private System.Windows.Forms.GroupBox groupBox3;
        private System.Windows.Forms.Button buttonいいねリスト作成;
        private System.Windows.Forms.CheckBox checkBox_15分以内に履歴のある無料アカウントを除外する;
        private System.Windows.Forms.GroupBox groupBox4;
        private System.Windows.Forms.TextBox textBoxいいね件数;
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
        private System.Windows.Forms.Button buttonいいねブックマーク実行;
        private System.Windows.Forms.Button buttonクリアlog;
        private System.Windows.Forms.Button buttonDebugGetBearerToken;
        private System.Windows.Forms.Button buttonDebugGetAccessToken;
        private System.Windows.Forms.CheckBox checkBoxブックマーク;
        private System.Windows.Forms.CheckBox checkBoxいいね;
        private System.Windows.Forms.CheckBox checkBoxリプライ;
        private System.Windows.Forms.Button button1;
        private System.Windows.Forms.Button buttonリプライ_Debug;
        private System.Windows.Forms.TabPage tabPageツイート;
        private System.Windows.Forms.GroupBox groupBox6;
        private System.Windows.Forms.Button buttonコメント保存;
        private System.Windows.Forms.Button buttonコメント追加;
        private System.Windows.Forms.Button buttonコメント削除;
        private System.Windows.Forms.CheckBox checkBoxコメント_全アカウント共通;
        private System.Windows.Forms.CheckBox checkBoxコメント有効;
        private System.Windows.Forms.TextBox textBoxコメント;
        private System.Windows.Forms.TextBox textBoxコメント_コメントID;
        private System.Windows.Forms.TextBox textBoxコメント_AccountId;
        private System.Windows.Forms.TextBox textBoxコメント_UserID;
    }
}

