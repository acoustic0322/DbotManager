namespace ChildTweet
{
    partial class ChildTweet
    {
        /// <summary>
        ///  Required designer variable.
        /// </summary>
        private System.ComponentModel.IContainer components = null;

        /// <summary>
        ///  Clean up any resources being used.
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
        ///  Required method for Designer support - do not modify
        ///  the contents of this method with the code editor.
        /// </summary>
        private void InitializeComponent()
        {
            logListBox = new ListBox();
            buttonStop = new Button();
            buttonStart = new Button();
            label1 = new Label();
            textBoxPort = new TextBox();
            SuspendLayout();
            // 
            // logListBox
            // 
            logListBox.Anchor = AnchorStyles.Top | AnchorStyles.Bottom | AnchorStyles.Left | AnchorStyles.Right;
            logListBox.FormattingEnabled = true;
            logListBox.ItemHeight = 15;
            logListBox.Location = new Point(12, 12);
            logListBox.Name = "logListBox";
            logListBox.Size = new Size(920, 574);
            logListBox.TabIndex = 0;
            logListBox.KeyDown += logListBox_KeyDown;
            // 
            // buttonStop
            // 
            buttonStop.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            buttonStop.Location = new Point(859, 608);
            buttonStop.Name = "buttonStop";
            buttonStop.Size = new Size(75, 23);
            buttonStop.TabIndex = 1;
            buttonStop.Text = "停止";
            buttonStop.UseVisualStyleBackColor = true;
            buttonStop.Click += buttonStop_Click;
            // 
            // buttonStart
            // 
            buttonStart.Anchor = AnchorStyles.Bottom | AnchorStyles.Right;
            buttonStart.Location = new Point(778, 608);
            buttonStart.Name = "buttonStart";
            buttonStart.Size = new Size(75, 23);
            buttonStart.TabIndex = 2;
            buttonStart.Text = "開始";
            buttonStart.UseVisualStyleBackColor = true;
            buttonStart.Click += buttonStart_Click;
            // 
            // label1
            // 
            label1.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
            label1.AutoSize = true;
            label1.Location = new Point(12, 612);
            label1.Name = "label1";
            label1.Size = new Size(36, 15);
            label1.TabIndex = 3;
            label1.Text = "PORT";
            // 
            // textBoxPort
            // 
            textBoxPort.Anchor = AnchorStyles.Bottom | AnchorStyles.Left;
            textBoxPort.Location = new Point(54, 608);
            textBoxPort.Name = "textBoxPort";
            textBoxPort.Size = new Size(72, 23);
            textBoxPort.TabIndex = 4;
            textBoxPort.Text = "5001";
            // 
            // ChildTweet
            // 
            AutoScaleDimensions = new SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(946, 643);
            Controls.Add(textBoxPort);
            Controls.Add(label1);
            Controls.Add(buttonStart);
            Controls.Add(buttonStop);
            Controls.Add(logListBox);
            MinimizeBox = false;
            Name = "ChildTweet";
            Text = "ChildTweet";
            Load += ChildTweet_Load;
            ResumeLayout(false);
            PerformLayout();
        }

        #endregion

        private ListBox logListBox;
        private Button buttonStop;
        private Button buttonStart;
        private Label label1;
        private TextBox textBoxPort;
    }
}