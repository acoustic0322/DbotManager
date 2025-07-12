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
            SuspendLayout();
            // 
            // logListBox
            // 
            logListBox.FormattingEnabled = true;
            logListBox.ItemHeight = 15;
            logListBox.Location = new Point(12, 12);
            logListBox.Name = "logListBox";
            logListBox.Size = new Size(390, 424);
            logListBox.TabIndex = 0;
            // 
            // buttonStop
            // 
            buttonStop.Location = new Point(327, 447);
            buttonStop.Name = "buttonStop";
            buttonStop.Size = new Size(75, 23);
            buttonStop.TabIndex = 1;
            buttonStop.Text = "停止";
            buttonStop.UseVisualStyleBackColor = true;
            buttonStop.Click += buttonStop_Click;
            // 
            // buttonStart
            // 
            buttonStart.Location = new Point(246, 447);
            buttonStart.Name = "buttonStart";
            buttonStart.Size = new Size(75, 23);
            buttonStart.TabIndex = 2;
            buttonStart.Text = "開始";
            buttonStart.UseVisualStyleBackColor = true;
            buttonStart.Click += buttonStart_Click;
            // 
            // ChildTweet
            // 
            AutoScaleDimensions = new SizeF(7F, 15F);
            AutoScaleMode = AutoScaleMode.Font;
            ClientSize = new Size(416, 482);
            Controls.Add(buttonStart);
            Controls.Add(buttonStop);
            Controls.Add(logListBox);
            MaximizeBox = false;
            MinimizeBox = false;
            Name = "ChildTweet";
            Text = "ChildTweet";
            Load += ChildTweet_Load;
            ResumeLayout(false);
        }

        #endregion

        private ListBox logListBox;
        private Button buttonStop;
        private Button buttonStart;
    }
}