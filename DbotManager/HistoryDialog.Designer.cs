namespace DbotManager
{
    partial class HistoryDialog
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
            this.dataGridViewTweetHistory = new System.Windows.Forms.DataGridView();
            this.buttonSearch = new System.Windows.Forms.Button();
            this.comboBoxUserMaster = new System.Windows.Forms.ComboBox();
            this.checkBoxUser = new System.Windows.Forms.CheckBox();
            this.checkBoxAccount = new System.Windows.Forms.CheckBox();
            this.comboBoxAccount = new System.Windows.Forms.ComboBox();
            this.checkBoxモード = new System.Windows.Forms.CheckBox();
            this.comboBoxモード = new System.Windows.Forms.ComboBox();
            this.button再表示 = new System.Windows.Forms.Button();
            this.checkBoxエラー = new System.Windows.Forms.CheckBox();
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewTweetHistory)).BeginInit();
            this.SuspendLayout();
            // 
            // dataGridViewTweetHistory
            // 
            this.dataGridViewTweetHistory.AllowUserToAddRows = false;
            this.dataGridViewTweetHistory.AllowUserToDeleteRows = false;
            this.dataGridViewTweetHistory.AllowUserToResizeRows = false;
            this.dataGridViewTweetHistory.Anchor = ((System.Windows.Forms.AnchorStyles)((((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Bottom) 
            | System.Windows.Forms.AnchorStyles.Left) 
            | System.Windows.Forms.AnchorStyles.Right)));
            this.dataGridViewTweetHistory.AutoSizeColumnsMode = System.Windows.Forms.DataGridViewAutoSizeColumnsMode.AllCells;
            this.dataGridViewTweetHistory.ColumnHeadersHeightSizeMode = System.Windows.Forms.DataGridViewColumnHeadersHeightSizeMode.AutoSize;
            this.dataGridViewTweetHistory.Location = new System.Drawing.Point(12, 56);
            this.dataGridViewTweetHistory.Name = "dataGridViewTweetHistory";
            this.dataGridViewTweetHistory.RowHeadersVisible = false;
            this.dataGridViewTweetHistory.RowTemplate.Height = 21;
            this.dataGridViewTweetHistory.SelectionMode = System.Windows.Forms.DataGridViewSelectionMode.FullRowSelect;
            this.dataGridViewTweetHistory.Size = new System.Drawing.Size(1277, 591);
            this.dataGridViewTweetHistory.TabIndex = 1;
            // 
            // buttonSearch
            // 
            this.buttonSearch.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.buttonSearch.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.buttonSearch.Location = new System.Drawing.Point(1162, 14);
            this.buttonSearch.Name = "buttonSearch";
            this.buttonSearch.Size = new System.Drawing.Size(127, 32);
            this.buttonSearch.TabIndex = 2;
            this.buttonSearch.Text = "データ再取得";
            this.buttonSearch.UseVisualStyleBackColor = true;
            this.buttonSearch.Click += new System.EventHandler(this.buttonSearch_Click);
            // 
            // comboBoxUserMaster
            // 
            this.comboBoxUserMaster.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.comboBoxUserMaster.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.comboBoxUserMaster.FormattingEnabled = true;
            this.comboBoxUserMaster.Location = new System.Drawing.Point(95, 14);
            this.comboBoxUserMaster.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.comboBoxUserMaster.Name = "comboBoxUserMaster";
            this.comboBoxUserMaster.Size = new System.Drawing.Size(140, 27);
            this.comboBoxUserMaster.TabIndex = 3;
            this.comboBoxUserMaster.SelectedIndexChanged += new System.EventHandler(this.comboBoxUserMaster_SelectedIndexChanged);
            // 
            // checkBoxUser
            // 
            this.checkBoxUser.AutoSize = true;
            this.checkBoxUser.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.checkBoxUser.Location = new System.Drawing.Point(12, 16);
            this.checkBoxUser.Name = "checkBoxUser";
            this.checkBoxUser.Size = new System.Drawing.Size(76, 23);
            this.checkBoxUser.TabIndex = 5;
            this.checkBoxUser.Text = "ユーザー";
            this.checkBoxUser.UseVisualStyleBackColor = true;
            this.checkBoxUser.CheckedChanged += new System.EventHandler(this.checkBoxUser_CheckedChanged);
            // 
            // checkBoxAccount
            // 
            this.checkBoxAccount.AutoSize = true;
            this.checkBoxAccount.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.checkBoxAccount.Location = new System.Drawing.Point(250, 16);
            this.checkBoxAccount.Name = "checkBoxAccount";
            this.checkBoxAccount.Size = new System.Drawing.Size(83, 23);
            this.checkBoxAccount.TabIndex = 7;
            this.checkBoxAccount.Text = "アカウント";
            this.checkBoxAccount.UseVisualStyleBackColor = true;
            this.checkBoxAccount.CheckedChanged += new System.EventHandler(this.checkBoxAccount_CheckedChanged);
            // 
            // comboBoxAccount
            // 
            this.comboBoxAccount.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.comboBoxAccount.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.comboBoxAccount.FormattingEnabled = true;
            this.comboBoxAccount.Location = new System.Drawing.Point(340, 14);
            this.comboBoxAccount.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.comboBoxAccount.Name = "comboBoxAccount";
            this.comboBoxAccount.Size = new System.Drawing.Size(151, 27);
            this.comboBoxAccount.TabIndex = 6;
            this.comboBoxAccount.SelectedIndexChanged += new System.EventHandler(this.comboBoxAccount_SelectedIndexChanged);
            // 
            // checkBoxモード
            // 
            this.checkBoxモード.AutoSize = true;
            this.checkBoxモード.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.checkBoxモード.Location = new System.Drawing.Point(503, 16);
            this.checkBoxモード.Name = "checkBoxモード";
            this.checkBoxモード.Size = new System.Drawing.Size(62, 23);
            this.checkBoxモード.TabIndex = 9;
            this.checkBoxモード.Text = "モード";
            this.checkBoxモード.UseVisualStyleBackColor = true;
            this.checkBoxモード.CheckedChanged += new System.EventHandler(this.checkBoxモード_CheckedChanged);
            // 
            // comboBoxモード
            // 
            this.comboBoxモード.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.comboBoxモード.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.comboBoxモード.FormattingEnabled = true;
            this.comboBoxモード.Location = new System.Drawing.Point(572, 14);
            this.comboBoxモード.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.comboBoxモード.Name = "comboBoxモード";
            this.comboBoxモード.Size = new System.Drawing.Size(151, 27);
            this.comboBoxモード.TabIndex = 8;
            this.comboBoxモード.SelectedIndexChanged += new System.EventHandler(this.comboBoxモード_SelectedIndexChanged);
            // 
            // button絞込
            // 
            this.button再表示.Anchor = ((System.Windows.Forms.AnchorStyles)((System.Windows.Forms.AnchorStyles.Top | System.Windows.Forms.AnchorStyles.Right)));
            this.button再表示.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.button再表示.Location = new System.Drawing.Point(1029, 14);
            this.button再表示.Name = "button絞込";
            this.button再表示.Size = new System.Drawing.Size(127, 32);
            this.button再表示.TabIndex = 10;
            this.button再表示.Text = "再表示";
            this.button再表示.UseVisualStyleBackColor = true;
            this.button再表示.Click += new System.EventHandler(this.button絞込_Click);
            // 
            // checkBoxエラー
            // 
            this.checkBoxエラー.AutoSize = true;
            this.checkBoxエラー.Checked = true;
            this.checkBoxエラー.CheckState = System.Windows.Forms.CheckState.Checked;
            this.checkBoxエラー.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.checkBoxエラー.Location = new System.Drawing.Point(744, 16);
            this.checkBoxエラー.Name = "checkBoxエラー";
            this.checkBoxエラー.Size = new System.Drawing.Size(116, 23);
            this.checkBoxエラー.TabIndex = 11;
            this.checkBoxエラー.Text = "エラーのみ表示";
            this.checkBoxエラー.UseVisualStyleBackColor = true;
            this.checkBoxエラー.CheckedChanged += new System.EventHandler(this.checkBoxエラー_CheckedChanged);
            // 
            // HistoryDialog
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1301, 659);
            this.Controls.Add(this.checkBoxエラー);
            this.Controls.Add(this.button再表示);
            this.Controls.Add(this.checkBoxモード);
            this.Controls.Add(this.comboBoxモード);
            this.Controls.Add(this.checkBoxAccount);
            this.Controls.Add(this.comboBoxAccount);
            this.Controls.Add(this.checkBoxUser);
            this.Controls.Add(this.comboBoxUserMaster);
            this.Controls.Add(this.buttonSearch);
            this.Controls.Add(this.dataGridViewTweetHistory);
            this.Name = "HistoryDialog";
            this.Text = "HistoryDialog";
            this.Load += new System.EventHandler(this.HistoryDialog_Load);
            ((System.ComponentModel.ISupportInitialize)(this.dataGridViewTweetHistory)).EndInit();
            this.ResumeLayout(false);
            this.PerformLayout();

        }

        #endregion

        private System.Windows.Forms.DataGridView dataGridViewTweetHistory;
        private System.Windows.Forms.Button buttonSearch;
        private System.Windows.Forms.ComboBox comboBoxUserMaster;
        private System.Windows.Forms.CheckBox checkBoxUser;
        private System.Windows.Forms.CheckBox checkBoxAccount;
        private System.Windows.Forms.ComboBox comboBoxAccount;
        private System.Windows.Forms.CheckBox checkBoxモード;
        private System.Windows.Forms.ComboBox comboBoxモード;
        private System.Windows.Forms.Button button再表示;
        private System.Windows.Forms.CheckBox checkBoxエラー;
    }
}