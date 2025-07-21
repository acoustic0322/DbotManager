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
                string logDir = @"C:\DBotManager\ChildTweet\logs";
                Directory.CreateDirectory(logDir); // なければ作る


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
                server.Port = int.Parse(textBoxPort.Text);
                server.Start();

                buttonStart.Enabled = false;
                buttonStop.Enabled = true;
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

                buttonStart.Enabled = true;
                buttonStop.Enabled = false;
            }
            catch (Exception ex)
            {
                AppendLog(ex.Message);
            }
        }

        private static readonly object _logLock = new object(); // グローバルに1個定義（クラス内の上の方に）


        private void AppendLog(string message)
        {
            // 保存先を固定パスに変更
            string logDir = @"C:\DBotManager\ChildTweet\logs";

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
            Directory.CreateDirectory(logDir); // logs フォルダがなければ作る

            string logFileName = $"log_{DateTime.Now:yyyy-MM-dd}.log";
            string logFilePath = Path.Combine(logDir, logFileName);

            try
            {
                lock (_logLock) // ← ログファイル書き込みを排他制御
                {
                    File.AppendAllText(logFilePath, timestamped + Environment.NewLine);
                }
            }
            catch (Exception ex)
            {
                logListBox.Items.Add($"[ERROR] ログ書き込み失敗: {ex.Message}");
            }
        }


    }
}