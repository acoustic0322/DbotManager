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
            this.tabPage予約 = new System.Windows.Forms.TabPage();
            this.dataGridViewReserveSchedule = new System.Windows.Forms.DataGridView();
            this.dataGridViewReserveSchedule_ReserveId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewReserveSchedule_UserName = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewReserveSchedule_AccountId = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewReserveSchedule_AccountName = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewReserveSchedule_Comment = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewReserveSchedule_ReserveTime = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.dataGridViewReserveSchedule_Result = new System.Windows.Forms.DataGridViewTextBoxColumn();
            this.button予約作成 = new System.Windows.Forms.Button();
            this.tabPage履歴 = new System.Windows.Forms.TabPage();
            this.dataGridViewTweetHistory = new System.Windows.Forms.DataGridView();
            this.textBoxRenew = new System.Windows.Forms.TextBox();
            this.buttonクリアlog = new System.Windows.Forms.Button();
            this.buttonアカウント設定 = new System.Windows.Forms.Button();
            this.tabControl.SuspendLayout();
            this.tabPageいいねブックマーク.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewいいねリスト)).BeginInit();
            this.groupBox3.SuspendLayout();
            this.groupBox5.SuspendLayout();
            this.groupBox4.SuspendLayout();
            this.tabPage予約.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewReserveSchedule)).BeginInit();
            this.tabPage履歴.SuspendLayout();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewTweetHistory)).BeginInit();
            this.SuspendLayout();
            // 
            // tabControl
            // 
            this.tabControl.Controls.Add(this.tabPageいいねブックマーク);
            this.tabControl.Controls.Add(this.tabPage予約);
            this.tabControl.Controls.Add(this.tabPage履歴);
            this.tabControl.Font = new System.Drawing.Font("Meiryo UI", 11.25F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(128)));
            this.tabControl.Location = new System.Drawing.Point(13, 14);
            this.tabControl.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.tabControl.Name = "tabControl";
            this.tabControl.SelectedIndex = 0;
            this.tabControl.Size = new System.Drawing.Size(768, 674);
            this.tabControl.TabIndex = 0;
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
            this.tabPageいいねブックマーク.Text = "いいね・ブックマーク・リプライ機能";
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
            // tabPage予約
            // 
            this.tabPage予約.Controls.Add(this.dataGridViewReserveSchedule);
            this.tabPage予約.Controls.Add(this.button予約作成);
            this.tabPage予約.Location = new System.Drawing.Point(4, 28);
            this.tabPage予約.Name = "tabPage予約";
            this.tabPage予約.Size = new System.Drawing.Size(760, 642);
            this.tabPage予約.TabIndex = 4;
            this.tabPage予約.Text = "予約機能";
            this.tabPage予約.UseVisualStyleBackColor = true;
            // 
            // dataGridViewReserveSchedule
            // 
            this.dataGridViewReserveSchedule.AllowUserToAddRows = false;
            this.dataGridViewReserveSchedule.AllowUserToDeleteRows = false;
            this.dataGridViewReserveSchedule.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridViewReserveSchedule.Columns.AddRange(new System.Windows.Forms.DataGridViewColumn[] {
            this.dataGridViewReserveSchedule_ReserveId,
            this.dataGridViewReserveSchedule_UserName,
            this.dataGridViewReserveSchedule_AccountId,
            this.dataGridViewReserveSchedule_AccountName,
            this.dataGridViewReserveSchedule_Comment,
            this.dataGridViewReserveSchedule_ReserveTime,
            this.dataGridViewReserveSchedule_Result});
            this.dataGridViewReserveSchedule.Location = new System.Drawing.Point(14, 60);
            this.dataGridViewReserveSchedule.Name = "dataGridViewReserveSchedule";
            this.dataGridViewReserveSchedule.RowHeadersVisible = false;
            this.dataGridViewReserveSchedule.RowTemplate.Height = 21;
            this.dataGridViewReserveSchedule.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridViewReserveSchedule.Size = new System.Drawing.Size(719, 524);
            this.dataGridViewReserveSchedule.TabIndex = 5;
            // 
            // dataGridViewReserveSchedule_ReserveId
            // 
            this.dataGridViewReserveSchedule_ReserveId.DataPropertyName = "ReserveId";
            this.dataGridViewReserveSchedule_ReserveId.HeaderText = "予約ID";
            this.dataGridViewReserveSchedule_ReserveId.Name = "dataGridViewReserveSchedule_ReserveId";
            // 
            // dataGridViewReserveSchedule_UserName
            // 
            this.dataGridViewReserveSchedule_UserName.DataPropertyName = "UserName";
            this.dataGridViewReserveSchedule_UserName.HeaderText = "ユーザー名";
            this.dataGridViewReserveSchedule_UserName.Name = "dataGridViewReserveSchedule_UserName";
            // 
            // dataGridViewReserveSchedule_AccountId
            // 
            this.dataGridViewReserveSchedule_AccountId.DataPropertyName = "AccountId";
            this.dataGridViewReserveSchedule_AccountId.HeaderText = "アカウントID";
            this.dataGridViewReserveSchedule_AccountId.Name = "dataGridViewReserveSchedule_AccountId";
            // 
            // dataGridViewReserveSchedule_AccountName
            // 
            this.dataGridViewReserveSchedule_AccountName.DataPropertyName = "AccountName";
            this.dataGridViewReserveSchedule_AccountName.HeaderText = "アカウント名";
            this.dataGridViewReserveSchedule_AccountName.Name = "dataGridViewReserveSchedule_AccountName";
            // 
            // dataGridViewReserveSchedule_Comment
            // 
            this.dataGridViewReserveSchedule_Comment.DataPropertyName = "Comment";
            this.dataGridViewReserveSchedule_Comment.HeaderText = "コメント";
            this.dataGridViewReserveSchedule_Comment.Name = "dataGridViewReserveSchedule_Comment";
            // 
            // dataGridViewReserveSchedule_ReserveTime
            // 
            this.dataGridViewReserveSchedule_ReserveTime.DataPropertyName = "ReserveTime";
            this.dataGridViewReserveSchedule_ReserveTime.HeaderText = "投稿時間";
            this.dataGridViewReserveSchedule_ReserveTime.Name = "dataGridViewReserveSchedule_ReserveTime";
            this.dataGridViewReserveSchedule_ReserveTime.Resizable = System.Windows.Forms.DataGridViewTriState.True;
            this.dataGridViewReserveSchedule_ReserveTime.SortMode = System.Windows.Forms.DataGridViewColumnSortMode.NotSortable;
            // 
            // dataGridViewReserveSchedule_Result
            // 
            this.dataGridViewReserveSchedule_Result.DataPropertyName = "Result";
            this.dataGridViewReserveSchedule_Result.HeaderText = "状況";
            this.dataGridViewReserveSchedule_Result.Name = "dataGridViewReserveSchedule_Result";
            // 
            // button予約作成
            // 
            this.button予約作成.Location = new System.Drawing.Point(14, 7);
            this.button予約作成.Name = "button予約作成";
            this.button予約作成.Size = new System.Drawing.Size(125, 47);
            this.button予約作成.TabIndex = 0;
            this.button予約作成.Text = "予約作成";
            this.button予約作成.UseVisualStyleBackColor = true;
            this.button予約作成.Click += new System.EventHandler(this.button予約作成_Click);
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
            // textBoxRenew
            // 
            this.textBoxRenew.Font = new System.Drawing.Font("Meiryo UI", 9F, System.Drawing.FontStyle.Regular, System.Drawing.GraphicsUnit.Point, ((byte)(128)));
            this.textBoxRenew.Location = new System.Drawing.Point(788, 46);
            this.textBoxRenew.Multiline = true;
            this.textBoxRenew.Name = "textBoxRenew";
            this.textBoxRenew.ScrollBars = System.Windows.Forms.ScrollBars.Both;
            this.textBoxRenew.Size = new System.Drawing.Size(635, 638);
            this.textBoxRenew.TabIndex = 1;
            // 
            // buttonクリアlog
            // 
            this.buttonクリアlog.Location = new System.Drawing.Point(788, 12);
            this.buttonクリアlog.Name = "buttonクリアlog";
            this.buttonクリアlog.Size = new System.Drawing.Size(103, 28);
            this.buttonクリアlog.TabIndex = 4;
            this.buttonクリアlog.Text = "クリア";
            this.buttonクリアlog.UseVisualStyleBackColor = true;
            this.buttonクリアlog.Click += new System.EventHandler(this.buttonクリアlog_Click);
            // 
            // buttonアカウント設定
            // 
            this.buttonアカウント設定.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonアカウント設定.Location = new System.Drawing.Point(1317, 12);
            this.buttonアカウント設定.Name = "buttonアカウント設定";
            this.buttonアカウント設定.Size = new System.Drawing.Size(106, 28);
            this.buttonアカウント設定.TabIndex = 10;
            this.buttonアカウント設定.Text = "アカウント設定";
            this.buttonアカウント設定.UseVisualStyleBackColor = true;
            this.buttonアカウント設定.Click += new System.EventHandler(this.buttonアカウント設定_Click);
            // 
            // Form
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(9F, 19F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1468, 712);
            this.Controls.Add(this.buttonアカウント設定);
            this.Controls.Add(this.buttonクリアlog);
            this.Controls.Add(this.textBoxRenew);
            this.Controls.Add(this.tabControl);
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
            this.tabPage予約.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewReserveSchedule)).EndInit();
            this.tabPage履歴.ResumeLayout(false);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewTweetHistory)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.TabControl tabControl;
        private System.Windows.Forms.TabPage tabPage履歴;
        private System.Windows.Forms.DataGridView dataGridViewTweetHistory;
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
        private System.Windows.Forms.CheckBox checkBoxブックマーク;
        private System.Windows.Forms.CheckBox checkBoxいいね;
        private System.Windows.Forms.CheckBox checkBoxリプライ;
        private System.Windows.Forms.TabPage tabPage予約;
        private System.Windows.Forms.Button button予約作成;
        private System.Windows.Forms.DataGridView dataGridViewReserveSchedule;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewReserveSchedule_ReserveId;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewReserveSchedule_UserName;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewReserveSchedule_AccountId;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewReserveSchedule_AccountName;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewReserveSchedule_Comment;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewReserveSchedule_ReserveTime;
        private System.Windows.Forms.DataGridViewTextBoxColumn dataGridViewReserveSchedule_Result;
        private System.Windows.Forms.Button buttonアカウント設定;
    }
}

