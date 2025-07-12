namespace ChildTweet
{
    public partial class ChildTweet : Form
    {
        private TweetHttpServer server = new TweetHttpServer();


        public ChildTweet()
        {
            InitializeComponent();
        }

        private void ChildTweet_Load(object sender, EventArgs e)
        {
            try
            {
                buttonStart_Click(sender, e);
            }
            catch (Exception ex)
            {
                AppendLog(ex.Message);
            }
        }

        private void buttonStart_Click(object sender, EventArgs e)
        {
            try
            {
                server.LogOutput = AppendLog;
                server.Start();
            }
            catch (Exception ex)
            {
                AppendLog(ex.Message);
            }
        }

        private void buttonStop_Click(object sender, EventArgs e)
        {
            try
            {
                server.Stop();
            }
            catch (Exception ex)
            {
                AppendLog(ex.Message);
            }
        }

        private void AppendLog(string message)
        {
            string timestamped = $"{message}";

            // ListBoxに追加（UIスレッドで）
            if (InvokeRequired)
            {
                Invoke(new Action(() => logListBox.Items.Add(timestamped)));
            }
            else
            {
                logListBox.Items.Add(timestamped);
            }

            // ログファイル名に日付を含める（例：log_2025-07-11.txt）
            string logDir = Path.Combine(AppDomain.CurrentDomain.BaseDirectory, "logs");
            Directory.CreateDirectory(logDir); // logs フォルダがなければ作る

            string logFileName = $"log_{DateTime.Now:yyyy-MM-dd}.log";
            string logFilePath = Path.Combine(logDir, logFileName);

            try
            {
                File.AppendAllText(logFilePath, timestamped + Environment.NewLine);
            }
            catch (Exception ex)
            {
                logListBox.Items.Add($"[ERROR] ログ書き込み失敗: {ex.Message}");
            }
        }


    }
}