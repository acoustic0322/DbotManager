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
            this.checkBox1 = new System.Windows.Forms.CheckBox();
            this.comboBox1 = new System.Windows.Forms.ComboBox();
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
            this.dataGridViewTweetHistory.Size = new System.Drawing.Size(1059, 591);
            this.dataGridViewTweetHistory.TabIndex = 1;
            // 
            // buttonSearch
            // 
            this.buttonSearch.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.buttonSearch.Location = new System.Drawing.Point(944, 9);
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
            // checkBox1
            // 
            this.checkBox1.AutoSize = true;
            this.checkBox1.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.checkBox1.Location = new System.Drawing.Point(503, 16);
            this.checkBox1.Name = "checkBox1";
            this.checkBox1.Size = new System.Drawing.Size(62, 23);
            this.checkBox1.TabIndex = 9;
            this.checkBox1.Text = "モード";
            this.checkBox1.UseVisualStyleBackColor = true;
            // 
            // comboBox1
            // 
            this.comboBox1.DropDownStyle = System.Windows.Forms.ComboBoxStyle.DropDownList;
            this.comboBox1.Font = new System.Drawing.Font("Meiryo UI", 11.25F);
            this.comboBox1.FormattingEnabled = true;
            this.comboBox1.Location = new System.Drawing.Point(593, 14);
            this.comboBox1.Margin = new System.Windows.Forms.Padding(4, 5, 4, 5);
            this.comboBox1.Name = "comboBox1";
            this.comboBox1.Size = new System.Drawing.Size(151, 27);
            this.comboBox1.TabIndex = 8;
            // 
            // HistoryDialog
            // 
            this.AutoScaleDimensions = new System.Drawing.SizeF(6F, 12F);
            this.AutoScaleMode = System.Windows.Forms.AutoScaleMode.Font;
            this.ClientSize = new System.Drawing.Size(1083, 659);
            this.Controls.Add(this.checkBox1);
            this.Controls.Add(this.comboBox1);
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
        private System.Windows.Forms.CheckBox checkBox1;
        private System.Windows.Forms.ComboBox comboBox1;
    }
}