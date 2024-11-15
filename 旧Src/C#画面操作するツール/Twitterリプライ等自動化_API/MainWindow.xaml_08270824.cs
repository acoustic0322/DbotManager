using Microsoft.WindowsAPICodePack.Dialogs;
using System;
using System.Collections.Generic;
using System.Collections.ObjectModel;
using System.ComponentModel;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Windows;
using System.Windows.Forms;
using System.Windows.Input;
using System.Text.RegularExpressions;
using System.Net.Http;
using System.Net.Http.Headers;
using System.Net;
using System.Web;
using CsvHelper.Configuration.Attributes;
using CsvHelper.Configuration;
using CsvHelper;
using System.Security.Policy;
using System.Globalization;
using static ICSharpCode.SharpZipLib.Zip.ZipEntryFactory;
using System.Windows.Controls;
using static System.Windows.Forms.VisualStyles.VisualStyleElement.TaskbarClock;
using System.Net.WebSockets;

#if 認証
using CommonLibrary;
#endif

namespace Twitterリプライ等自動化_API
{
    /// <summary>
    /// MainWindow.xaml の相互作用ロジック
    /// </summary>
    public partial class MainWindow : System.Windows.Window
    {
        private ClientWebSocket _client;

        private static string ck = "SBd4tiZXE2w65cquDEWHLuqHi";
        private static string cs = "K7f1EfMmPkRWXCQYz4HREbPrvunTk4h3ymZtG1RoMwZcBfBUYC";
        private static string ct = "S0o0T2dOU3ZESDByR0ZTcW9vcE86MTpjaQ";
        private static string ctk = "is6iQmgF4k29fEQiKX8TzEXGlThSg9Wo3pPt4Eu5UM6nB3QgBR";

        private static string DefaultDirectory;
        public MainWindow()
        {
            InitializeComponent();

            //UpgradeSettingsIfNecessary();

            try
            {
#if DEBUG
    中断.Visibility = Visibility.Visible;
#else
                中断.Visibility = Visibility.Hidden;
#endif
                アカウント毎の設定.ItemsSource = info;
                リプライ対象URL.Text = Properties.Settings.Default.リプライ対象URL;
                キー入力.Text = Properties.Settings.Default.キー入力;
                if (キー入力.Text == "")
                {
                    キー入力.Text = ck + "\n" + cs + "\n" + ct + "\n" + ctk;
                }
                デフォルトフォルダ.Text = Properties.Settings.Default.デフォルトフォルダ;

                いいねcheck.IsChecked = Properties.Settings.Default.いいねcheck;
                ブックマークcheck.IsChecked = Properties.Settings.Default.ブックマークcheck;
                リツイートcheck.IsChecked = Properties.Settings.Default.リツイートcheck;
                ファイル削除.IsChecked = Properties.Settings.Default.ファイル削除;

                var list = Properties.Settings.Default.info;
                foreach (var item in list)
                {
                    var d = new Data();
                    d.実行確認 = item[0] == "True" ? true : false;
                    d.アカウント名 = item[1];
                    d.カスタマーキー = item[2];
                    d.カスタマーシークレット = item[3];
                    d.アクセストークン = item[4];
                    d.アクセストークンシークレット = item[5];
                    d.ベアラトークン = item[6];
                    d.リフレッシュトークン = item[7];
                    d.クライアントID = item[8];
                    d.クライアントシークレットID = item[9];
                    d.カスタマーキー = ck;
                    d.カスタマーシークレット = cs;
                    d.クライアントID = ct;
                    d.クライアントシークレットID = ctk;
                    d.コメント = item[10];
                    d.画像 = item[11];
                    d.動画 = item[12];
                    d.メモ = item[13];
                    d.監視アカウント = item[14];

                    string times = item[15];
                    var time_sp = times.Split('\n');
                    List<string> tmplist = new List<string>();
                    foreach (var time in time_sp)
                    {
                        var tmptime = time.Replace("終了", "").Trim();
                        tmplist.Add(tmptime);
                    }
                    d.予約投稿時間 = string.Join("\n", tmplist);
                    d.プロキシURL = item[16];
                    d.DMMID = item[17];
                    info.Add(d);
                }

                リプライラベル.Content = "リプライ対象投稿URL\nhttps://x.com/*/status/*";
                キー説明.Content = "上から\nカスタマーキー\nカスタマーシークレットキー\nクライアントキー\nクライアントシークレットキー\nを入力してください";

                StartWebSocketClient();
            }
            catch
            {
                exportCSV();
                Properties.Settings.Default.Reset();
                Close();
            }
        }
        private void UpgradeSettingsIfNecessary()
        {
            // アプリケーション設定に 'IsUpgraded' という名前のブール値フラグを追加していると仮定します
            if (!Properties.Settings.Default.IsUpgraded)
            {
                try
                {
                    string pastVersionDir = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile) + @"\AppData\Local\Twitterリプライ等自動化_API";
                    string[] versionDirectories = Directory.GetDirectories(pastVersionDir);
                    if (versionDirectories.Length == 0)
                    {
                        return;
                    }

                    string latestDirectory = versionDirectories
                        .Select(d => new DirectoryInfo(d))
                        .OrderByDescending(d => d.CreationTime)
                        .First()
                        .FullName;
                    if (string.IsNullOrEmpty(latestDirectory))
                    {
                        return;
                    }
                    string[] versionDirectories2 = Directory.GetDirectories(latestDirectory);
                    if (versionDirectories.Length == 0)
                    {
                        return;
                    }
                    string latestDirectory2 = versionDirectories2
                        .Select(d => new DirectoryInfo(d))
                        .OrderByDescending(d => d.CreationTime)
                        .First()
                        .FullName;
                    if (string.IsNullOrEmpty(latestDirectory2))
                    {
                        return;
                    }

                    // user.configを読み込む
                    // Path to the user.config file
                    string userConfigFilePath = Path.Combine(latestDirectory2, "user.config");

                    if (!File.Exists(userConfigFilePath))
                    {
                        return;
                    }
                    File.Copy(userConfigFilePath, "user.config");

                }
                catch { }
                finally
                {
                    Properties.Settings.Default.IsUpgraded = true;  // フラグを true に設定
                    Properties.Settings.Default.Save();  // 設定を保存

                    if (File.Exists("user.config"))
                    {
                        string pastVersionDir = Environment.GetFolderPath(Environment.SpecialFolder.UserProfile) + @"\AppData\Local\Twitterリプライ等自動化_API";
                        string[] versionDirectories = Directory.GetDirectories(pastVersionDir);

                        string latestDirectory = versionDirectories
                            .Select(d => new DirectoryInfo(d))
                            .OrderByDescending(d => d.CreationTime)
                            .First()
                            .FullName;
                        string[] versionDirectories2 = Directory.GetDirectories(latestDirectory);
                        string latestDirectory2 = versionDirectories2
                            .Select(d => new DirectoryInfo(d))
                            .OrderByDescending(d => d.CreationTime)
                            .First()
                            .FullName;
                        File.Copy("user.config", latestDirectory2 + "\\user.config", true);
                        File.Delete("user.config");
                        Properties.Settings.Default.Reload();
                        Properties.Settings.Default.Save();
                    }
                }
            }
        }
        private static ObservableCollection<Data> info = new ObservableCollection<Data>();
        public class Data : INotifyPropertyChanged
        {
            public event PropertyChangedEventHandler PropertyChanged;

            public bool 実行確認 { get; set; }
            public string アカウント名 { get; set; }
            public string コメント { get; set; }
            public string 画像 { get; set; }
            public string 動画 { get; set; }
            public string メモ { get; set; }
            public string カスタマーキー { get; set; }
            public string カスタマーシークレット { get; set; }
            public string アクセストークン { get; set; }
            public string アクセストークンシークレット { get; set; }
            public string ベアラトークン { get; set; }
            public string リフレッシュトークン { get; set; }
            public string クライアントID { get; set; }
            public string クライアントシークレットID { get; set; }
            public string 監視アカウント { get; set; }
            public string 予約投稿時間 { get; set; }
            public string プロキシURL { get; set; }
            public string DMMID { get; set; }
        }

        static DirectoryInfo GetLatestFolder(string rootDirectory)
        {
            DirectoryInfo rootDirInfo = new DirectoryInfo(rootDirectory);

            if (!rootDirInfo.Exists)
            {
                return null;
            }

            DirectoryInfo latestFolder = null;
            DateTime latestCreationTime = DateTime.MinValue;

            foreach (var folder in rootDirInfo.GetDirectories())
            {
                DateTime folderCreationTime = folder.CreationTime;

                if (folderCreationTime > latestCreationTime)
                {
                    latestCreationTime = folderCreationTime;
                    latestFolder = folder;
                }
            }

            return latestFolder;
        }

        private void アカウント追加_Click(object sender, RoutedEventArgs e)
        {
            // プロファイルをフォルダから選択
            using (var cofd = new CommonOpenFileDialog()
            {
                Title = "プロファイルフォルダを選択してください",
                // フォルダ選択モードにする
                IsFolderPicker = true,
                Multiselect = true,
                InitialDirectory = System.Environment.GetFolderPath(Environment.SpecialFolder.UserProfile) + @"\AppData\Local\Google\Chrome\User Data"
            })
            {
                if (cofd.ShowDialog() != CommonFileDialogResult.Ok)
                {
                    return;
                }

                foreach (var p in cofd.FileNames)
                {
                    var folder = Path.GetFileName(p);

                    if (info.Count == 0 || !info.Any(v => v.アカウント名 == folder))
                    {
                        var d = new Data();
                        d.実行確認 = true;
                        d.アカウント名 = folder;
                        d.カスタマーキー = ck;
                        d.カスタマーシークレット = cs;
                        d.クライアントID = ct;
                        d.クライアントシークレットID = ctk;
                        info.Add(d);
                    }
                }
            }

        }


        private void アカウント削除_Click(object sender, RoutedEventArgs e)
        {
            // データソースを取得（Assuming DataContext has the collection）
            ObservableCollection<Data> dataCollection = アカウント毎の設定.ItemsSource as ObservableCollection<Data>;
            if (dataCollection != null)
            {
                // 選択された項目を削除
                List<Data> selectedItems = new List<Data>(アカウント毎の設定.SelectedItems.Cast<Data>());
                foreach (Data selectedItem in selectedItems)
                {
                    dataCollection.Remove(selectedItem);
                }
                info = dataCollection;
            }
        }

        public static bool IsUrl(string input)
        {
            if (string.IsNullOrEmpty(input))
            {
                return false;
            }
            string pattern = @"^https:\/\/x\.com\/.*\/status\/.*$";
            return Regex.IsMatch(
               input,
               pattern
            );
        }

        private string ランダムな画像(string path)
        {
            List<string> list = new List<string>();
            if (Directory.Exists(path))
            {
                IEnumerable<string> files = System.IO.Directory.EnumerateFiles(path, "*", System.IO.SearchOption.TopDirectoryOnly);

                //ファイルを列挙する
                foreach (string f in files)
                {
                    if (System.IO.Path.GetExtension(f).ToLower() == ".png" || System.IO.Path.GetExtension(f).ToLower() == ".jpeg" || System.IO.Path.GetExtension(f).ToLower() == ".jpg" ||
                        System.IO.Path.GetExtension(f).ToLower() == ".webp" || System.IO.Path.GetExtension(f).ToLower() == ".gif")
                    {
                        list.Add(f);
                    }
                }
            }
            else if (File.Exists(path))
            {
                return path;
            }
            if (list.Count > 0)
            {
                Random rand = new Random();
                Thread.Sleep(1);
                int randomIndex = rand.Next(0, list.Count);
                return list[randomIndex];
            }
            else
            {
                return "";
            }
        }

        private string ランダムな動画(string path)
        {
            List<string> list = new List<string>();
            if (Directory.Exists(path))
            {
                IEnumerable<string> files = System.IO.Directory.EnumerateFiles(path, "*", System.IO.SearchOption.TopDirectoryOnly);

                //ファイルを列挙する
                foreach (string f in files)
                {
                    if (System.IO.Path.GetExtension(f).ToLower() == ".mp4" || System.IO.Path.GetExtension(f).ToLower() == ".quicktime")
                    {
                        list.Add(f);
                    }
                }
            }
            else if (File.Exists(path))
            {
                return path;
            }

            if (list.Count > 0)
            {
                Random rand = new Random();
                Thread.Sleep(1);
                int randomIndex = rand.Next(0, list.Count);
                return list[randomIndex];
            }
            else
            {
                return "";
            }
        }

        private string randomコメント(string text)
        {
            var sp = text.Replace("\r\n", "\n").Trim().Split('\n').Where(item => !string.IsNullOrWhiteSpace(item.Trim())).ToList();
            Random rand = new Random();
            Thread.Sleep(1);
            int randomIndex = rand.Next(0, sp.Count);
            var tmp = sp[randomIndex];
            tmp = tmp.Replace("【改行】", "\n");
            return tmp;
        }

        private void BAN書き込み(string name)
        {
            if (File.Exists("BANリスト.txt"))
            {
                string line = "";

                using (StreamReader sr = new StreamReader(
                    "BANリスト.txt", Encoding.GetEncoding("Shift_JIS")))
                {

                    while ((line = sr.ReadLine()) != null)
                    {
                        if (line == name)
                        {
                            return;
                        }
                    }
                }
            }

            // Append text to the file
            using (StreamWriter sw = new StreamWriter("BANリスト.txt", true))
            {
                sw.WriteLine(name);
            }
        }

        private string getid(string url)
        {
            // 正規表現パターンを定義
            string pattern = @"status/(\d+)";
            Regex regex = new Regex(pattern);

            // URLに対して正規表現を適用
            Match match = regex.Match(url);

            // 一致する部分を取得
            if (match.Success)
            {
                string tweetId = match.Groups[1].Value;
                return tweetId;
            }
            else if (url.All(char.IsDigit))
            {
                return url;
            }
            return null;
        }

        // ランダムな待機時間を生成して待機する関数
        private static CancellationTokenSource cts = new CancellationTokenSource();
        static async Task WaitRandomTime(int minDelay, int maxDelay)
        {
            Random random = new Random();
            int delay = random.Next(minDelay, maxDelay);

            try
            {
                await Task.Delay(delay, cts.Token);
            }
            catch (TaskCanceledException)
            {
            }
        }

        private static bool remove = true;
        private void 投稿(string comment, string image, string movie, string url, string account, string proxy)
        {
            var random_image = ランダムな画像(image);
            var random_movie = ランダムな動画(movie);

            ProcessStartInfo startInfo = new ProcessStartInfo();
            startInfo.CreateNoWindow = true;  // ウィンドウを表示しない
            startInfo.UseShellExecute = false;  // シェルを使用しない
            startInfo.FileName = "create_tweet.exe";
            startInfo.RedirectStandardError = true;
            startInfo.Arguments = $"\"{Path.Combine(DefaultDirectory, account)}\" \"{HttpUtility.UrlEncode(randomコメント(comment))}\" \"{random_image}\" \"{random_movie}\" \"{getid(url)}\" \"{proxy}\"";
            using (Process process = new Process())
            {
                process.StartInfo = startInfo;

                // プロセスを開始
                process.Start();
                string error = process.StandardError.ReadToEnd();

                // プロセスの終了を待つ
                process.WaitForExit();
                int exitCode = process.ExitCode;
                if (exitCode != 0)
                {
                    throw new Exception(error);
                }
            }

            if (remove)
            {
                try
                {
                    var imagefolder = Path.GetDirectoryName(random_image);
                    if (!Directory.Exists(Path.Combine(imagefolder, "finish")))
                    {
                        Directory.CreateDirectory(Path.Combine(imagefolder, "finish"));
                    }
                    File.Copy(random_image, Path.Combine(imagefolder, "finish", Path.GetFileName(random_image)), true);
                    File.Delete(random_image);
                }
                catch { }

                try
                {
                    var moviefolder = Path.GetDirectoryName(random_movie);
                    if (!Directory.Exists(Path.Combine(moviefolder, "finish")))
                    {
                        Directory.CreateDirectory(Path.Combine(moviefolder, "finish"));
                    }
                    File.Copy(random_movie, Path.Combine(moviefolder, "finish", Path.GetFileName(random_movie)), true);
                    File.Delete(random_movie);
                }
                catch { }
            }
        }

        static string SanitizeFilename(string filename)
        {
            // ファイル名に使えない文字を取得
            char[] invalidChars = Path.GetInvalidFileNameChars();
            // ファイル名から使えない文字を削除
            string sanitized = new string(filename.Where(ch => !invalidChars.Contains(ch)).ToArray());
            return sanitized;
        }

        private static bool finishflag = false;
        private static bool interruption = false;
        private async void 開始_PreviewMouseDown(object sender, MouseButtonEventArgs e)
        {
            bool can_good = (bool)いいねcheck.IsChecked;
            bool can_bokmark = (bool)ブックマークcheck.IsChecked;
            bool can_retweet = (bool)リツイートcheck.IsChecked;

            var url_sp = リプライ対象URL.Text.Split('\n');

            開始処理(can_good, can_bokmark, can_retweet, url_sp, true);

        }

        private async void 開始処理(bool can_good, bool can_bokmark, bool can_retweet, string[] url_sp , bool いいね強制 = false)
        {
            if (開始.Content.ToString() == "開始")
            {
                bool replymode = (bool)リプライラジオボタン.IsChecked;
                bool postmode = (bool)単純投稿ラジオボタン.IsChecked;
                bool bookgoodmode = (bool)ブックマークいいねラジオボタン.IsChecked;


                bool kansimode = (bool)監視ラジオボタン.IsChecked;
                bool kansimode2 = (bool)監視2ラジオボタン.IsChecked;
                bool yoyaku = (bool)予約投稿ラジオボタン.IsChecked;
                bool monomane = (bool)モノマネ投稿.IsChecked;

                if (いいね強制)
                {
                    replymode = false;
                    postmode = false;
                    bookgoodmode = true;
                    kansimode = false;
                    kansimode2 = false;
                    kansimode2 = false;
                    yoyaku = false;
                    monomane = false;
                }



                remove = (bool)ファイル削除.IsChecked;

                if (!Directory.Exists(DefaultDirectory))
                {
                    System.Windows.Forms.MessageBox.Show("デフォルトのフォルダ設定ができていません", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }

                if (bookgoodmode && !can_good && !can_bokmark && !can_retweet)
                {
                    System.Windows.Forms.MessageBox.Show("いいね、ブックマーク、リツイートのチェックが全て外れています", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }

                if (replymode && string.IsNullOrWhiteSpace(リプライ対象URL.Text))
                {
                    System.Windows.Forms.MessageBox.Show("リプライ対象URLが空です", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                    return;
                }


                開始.Content = "強制終了";
                cts = new CancellationTokenSource();
                finishflag = false;
                infosave();
                System.Windows.Forms.Application.DoEvents();

                await Task.Run(async () =>
                {
                    try
                    {
                        if (kansimode)
                        {
                            try
                            {
                                // アカウント分繰り返す 監視アカウントを取り出す
                                while (!finishflag)
                                {
                                    // 1分おきに実行
                                    int settime = 60;
                                    foreach (var item in info)
                                    {
                                        string account = item.監視アカウント;
                                        if (!string.IsNullOrWhiteSpace(account) && item.実行確認)
                                        {
                                            // 実行確認
                                            if (string.IsNullOrWhiteSpace(item.カスタマーキー) || string.IsNullOrWhiteSpace(item.カスタマーシークレット) || string.IsNullOrWhiteSpace(item.アクセストークン) || string.IsNullOrWhiteSpace(item.アクセストークンシークレット) || string.IsNullOrWhiteSpace(item.ベアラトークン) || string.IsNullOrWhiteSpace(item.リフレッシュトークン) || string.IsNullOrWhiteSpace(item.クライアントID) || string.IsNullOrWhiteSpace(item.クライアントシークレットID))
                                            {
                                                continue;
                                            }

                                            if (!Directory.Exists(Path.Combine(DefaultDirectory, item.アカウント名)))
                                            {
                                                Directory.CreateDirectory(Path.Combine(DefaultDirectory, item.アカウント名));
                                            }

                                            // キーを書き込む
                                            if (!File.Exists(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt")))
                                            {
                                                File.WriteAllText(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt"), item.カスタマーキー.Trim() + "\n" + item.カスタマーシークレット.Trim() + "\n" + item.アクセストークン.Trim() + "\n" + item.アクセストークンシークレット.Trim() + "\n" + item.ベアラトークン.Trim() + "\n" + item.リフレッシュトークン.Trim() + "\n" + item.クライアントID.Trim() + "\n" + item.クライアントシークレットID.Trim());
                                            }

                                            var tmp_account = account.Trim();
                                            var sp = tmp_account.Replace("\r\n", "\n").Split('\n');
                                            Dictionary<string, DateTime?> accountLastWriteTimes = new Dictionary<string, DateTime?>();

                                            // 各アカウントに対して処理を行う
                                            foreach (var s in sp)
                                            {
                                                string path_tmp_account = SanitizeFilename(s.Replace("@", "").Trim());
                                                DateTime? d_lastWriteTime = null;
                                                string filePath = Path.Combine(DefaultDirectory, item.アカウント名, path_tmp_account + ".txt");

                                                // ファイルの存在を確認し、最終更新日時を取得
                                                if (File.Exists(filePath))
                                                {
                                                    FileInfo d_fileInfo = new FileInfo(filePath);
                                                    d_lastWriteTime = d_fileInfo.LastWriteTime;
                                                }

                                                // アカウントと最終更新日時を辞書に追加
                                                if (!accountLastWriteTimes.ContainsKey(path_tmp_account))
                                                {
                                                    accountLastWriteTimes[path_tmp_account] = d_lastWriteTime;
                                                }
                                            }
                                            if (finishflag)
                                            {
                                                return;
                                            }
                                            if (interruption)
                                            {
                                                while (interruption && !finishflag)
                                                {
                                                    Thread.Sleep(1);
                                                }
                                            }

                                            // search_tweet.exe プロセスを開始
                                            ProcessStartInfo startInfo = new ProcessStartInfo
                                            {
                                                CreateNoWindow = true,  // ウィンドウを表示しない
                                                UseShellExecute = false,  // シェルを使用しない
                                                FileName = "search_tweet.exe",
                                                RedirectStandardError = true,
                                                Arguments = $"\"{tmp_account}\" \"{Path.Combine(DefaultDirectory, item.アカウント名)}\" \"{item.プロキシURL}\""
                                            };

                                            using (Process process = new Process { StartInfo = startInfo })
                                            {
                                                process.Start();  // プロセスを開始
                                                string error = process.StandardError.ReadToEnd();
                                                process.WaitForExit();  // プロセスの終了を待つ
                                                int exitCode = process.ExitCode;
                                                if (exitCode != 0)
                                                {
                                                    try
                                                    {
                                                        string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                        string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                        // ファイルにテキストを書き込む
                                                        using (var writer = File.AppendText(filePath))
                                                        {
                                                            writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "の監視モード１でエラーです。" + error);
                                                        }
                                                    }
                                                    catch { }
                                                }
                                            }

                                            // key.txt の内容を読み込み、item に設定
                                            string keyFilePath = Path.Combine(DefaultDirectory, item.アカウント名, "key.txt");
                                            string fileContent = File.ReadAllText(keyFilePath);
                                            var f_sp = fileContent.Replace("\r\n", "\n").Split('\n');
                                            item.カスタマーキー = f_sp[0].Trim();
                                            item.カスタマーシークレット = f_sp[1].Trim();
                                            item.アクセストークン = f_sp[2].Trim();
                                            item.アクセストークンシークレット = f_sp[3].Trim();
                                            item.ベアラトークン = f_sp[4].Trim();
                                            item.リフレッシュトークン = f_sp[5].Trim();
                                            item.クライアントID = f_sp[6].Trim();
                                            item.クライアントシークレットID = f_sp[7].Trim();

                                            await WaitRandomTime(2000, 4000);  // ランダムに待機

                                            if (finishflag)
                                            {
                                                break;  // finishflag が true の場合、ループを抜ける
                                            }
                                            if (interruption)
                                            {
                                                while (interruption && !finishflag)
                                                {
                                                    Thread.Sleep(1);
                                                }
                                            }

                                            // 各アカウントの最終更新日時を確認し、必要に応じて投稿を行う
                                            foreach (var path_tmp_account in accountLastWriteTimes)
                                            {
                                                if (finishflag)
                                                {
                                                    break;
                                                }
                                                if (interruption)
                                                {
                                                    while (interruption && !finishflag)
                                                    {
                                                        Thread.Sleep(1);
                                                    }
                                                }
                                                string accountFilePath = Path.Combine(DefaultDirectory, item.アカウント名, path_tmp_account.Key + ".txt");
                                                //System.Windows.Forms.MessageBox.Show(accountFilePath);
                                                if (File.Exists(accountFilePath))
                                                {
                                                    FileInfo fileInfo = new FileInfo(accountFilePath);
                                                    DateTime lastWriteTime = fileInfo.LastWriteTime;
                                                    //System.Windows.Forms.MessageBox.Show(lastWriteTime+":"+path_tmp_account.Value);

                                                    // 最終更新日時が異なる場合、または初回の場合
                                                    if (path_tmp_account.Value == null || lastWriteTime != path_tmp_account.Value)
                                                    {
                                                        string[] lines = File.ReadAllLines(accountFilePath, Encoding.UTF8);

                                                        // 各行に対してリプライを投稿
                                                        foreach (var line in lines)
                                                        {
                                                            if (!string.IsNullOrWhiteSpace(line.Trim()))
                                                            {
                                                                try
                                                                {
                                                                    投稿(item.コメント, item.画像, item.動画, line.Trim(), item.アカウント名, item.プロキシURL);
                                                                }
                                                                catch (Exception ex)
                                                                {
                                                                    try
                                                                    {
                                                                        string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                                        string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                                        // ファイルにテキストを書き込む
                                                                        using (var writer = File.AppendText(filePath))
                                                                        {
                                                                            writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "でエラーです。" + ex.Message);
                                                                        }
                                                                    }
                                                                    catch { }
                                                                }
                                                                await WaitRandomTime(3000, 5000);  // ランダムに待機
                                                                if (path_tmp_account.Value == null)
                                                                {
                                                                    break;  // 最初のリプライ投稿後にループを抜ける
                                                                }
                                                            }
                                                            if (finishflag)
                                                            {
                                                                break;
                                                            }
                                                            if (interruption)
                                                            {
                                                                while (interruption && !finishflag)
                                                                {
                                                                    Thread.Sleep(1);
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    for (int i = 0; i < settime; i++)
                                    {
                                        if (finishflag)
                                            break;
                                        if (interruption)
                                        {
                                            while (interruption && !finishflag)
                                            {
                                                Thread.Sleep(1);
                                            }
                                        }
                                        await Task.Delay(1000); // 1秒待機
                                    }
                                }
                            }
                            catch { }
                            finally
                            {
                                this.Dispatcher.Invoke((Action)(() =>
                                {
                                    開始.Content = "開始";
                                    開始.IsEnabled = true;
                                }));
                            }
                        }
                        else if (kansimode2)
                        {
                            try
                            {
                                // アカウント分繰り返す 監視アカウントを取り出す
                                while (!finishflag)
                                {
                                    // 1分おきに実行
                                    int settime = 60;
                                    foreach (var item in info)
                                    {
                                        string account = item.監視アカウント;
                                        if (!string.IsNullOrWhiteSpace(account) && item.実行確認)
                                        {
                                            // 実行確認
                                            if (string.IsNullOrWhiteSpace(item.カスタマーキー) || string.IsNullOrWhiteSpace(item.カスタマーシークレット) || string.IsNullOrWhiteSpace(item.アクセストークン) || string.IsNullOrWhiteSpace(item.アクセストークンシークレット) || string.IsNullOrWhiteSpace(item.ベアラトークン) || string.IsNullOrWhiteSpace(item.リフレッシュトークン) || string.IsNullOrWhiteSpace(item.クライアントID) || string.IsNullOrWhiteSpace(item.クライアントシークレットID))
                                            {
                                                continue;
                                            }

                                            if (!Directory.Exists(Path.Combine(DefaultDirectory, item.アカウント名)))
                                            {
                                                Directory.CreateDirectory(Path.Combine(DefaultDirectory, item.アカウント名));
                                            }

                                            // キーを書き込む
                                            if (!File.Exists(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt")))
                                            {
                                                File.WriteAllText(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt"), item.カスタマーキー.Trim() + "\n" + item.カスタマーシークレット.Trim() + "\n" + item.アクセストークン.Trim() + "\n" + item.アクセストークンシークレット.Trim() + "\n" + item.ベアラトークン.Trim() + "\n" + item.リフレッシュトークン.Trim() + "\n" + item.クライアントID.Trim() + "\n" + item.クライアントシークレットID.Trim());
                                            }

                                            var tmp_account = account.Trim();
                                            var sp = tmp_account.Replace("\r\n", "\n").Split('\n');
                                            Dictionary<string, DateTime?> accountLastWriteTimes = new Dictionary<string, DateTime?>();

                                            // 各アカウントに対して処理を行う
                                            foreach (var s in sp)
                                            {
                                                string path_tmp_account = SanitizeFilename(s.Replace("@", "").Trim());
                                                DateTime? d_lastWriteTime = null;
                                                string filePath = Path.Combine(DefaultDirectory, item.アカウント名, path_tmp_account + "_sinceid2.txt");

                                                // ファイルの存在を確認し、最終更新日時を取得
                                                if (File.Exists(filePath))
                                                {
                                                    FileInfo d_fileInfo = new FileInfo(filePath);
                                                    d_lastWriteTime = d_fileInfo.LastWriteTime;
                                                }

                                                // アカウントと最終更新日時を辞書に追加
                                                if (!accountLastWriteTimes.ContainsKey(path_tmp_account))
                                                {
                                                    accountLastWriteTimes[path_tmp_account] = d_lastWriteTime;
                                                }
                                            }

                                            if (finishflag)
                                            {
                                                return;
                                            }
                                            if (interruption)
                                            {
                                                while (interruption && !finishflag)
                                                {
                                                    Thread.Sleep(1);
                                                }
                                            }

                                            // search_tweet.exe プロセスを開始
                                            ProcessStartInfo startInfo = new ProcessStartInfo
                                            {
                                                CreateNoWindow = true,  // ウィンドウを表示しない
                                                UseShellExecute = false,  // シェルを使用しない
                                                RedirectStandardError = true,
                                                FileName = "search_tweet2.exe",
                                                Arguments = $"\"{tmp_account}\" \"{Path.Combine(DefaultDirectory, item.アカウント名)}\" \"{item.プロキシURL}\""
                                            };

                                            using (Process process = new Process { StartInfo = startInfo })
                                            {
                                                process.Start();  // プロセスを開始
                                                string error = process.StandardError.ReadToEnd();
                                                process.WaitForExit();  // プロセスの終了を待つ
                                                int exitCode = process.ExitCode;
                                                if (exitCode != 0)
                                                {
                                                    try
                                                    {
                                                        string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                        string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                        // ファイルにテキストを書き込む
                                                        using (var writer = File.AppendText(filePath))
                                                        {
                                                            writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "の監視モード（リプ）でエラーです。" + error);
                                                        }
                                                    }
                                                    catch { }
                                                }
                                            }

                                            // key.txt の内容を読み込み、item に設定
                                            string keyFilePath = Path.Combine(DefaultDirectory, item.アカウント名, "key.txt");
                                            string fileContent = File.ReadAllText(keyFilePath);
                                            var f_sp = fileContent.Replace("\r\n", "\n").Split('\n');
                                            item.カスタマーキー = f_sp[0].Trim();
                                            item.カスタマーシークレット = f_sp[1].Trim();
                                            item.アクセストークン = f_sp[2].Trim();
                                            item.アクセストークンシークレット = f_sp[3].Trim();
                                            item.ベアラトークン = f_sp[4].Trim();
                                            item.リフレッシュトークン = f_sp[5].Trim();
                                            item.クライアントID = f_sp[6].Trim();
                                            item.クライアントシークレットID = f_sp[7].Trim();

                                            await WaitRandomTime(2000, 4000);  // ランダムに待機

                                            if (finishflag)
                                            {
                                                break;  // finishflag が true の場合、ループを抜ける
                                            }
                                            if (interruption)
                                            {
                                                while (interruption && !finishflag)
                                                {
                                                    Thread.Sleep(1);
                                                }
                                            }

                                            // 各アカウントの最終更新日時を確認し、必要に応じて投稿を行う
                                            foreach (var path_tmp_account in accountLastWriteTimes)
                                            {
                                                if (finishflag)
                                                {
                                                    break;
                                                }
                                                if (interruption)
                                                {
                                                    while (interruption && !finishflag)
                                                    {
                                                        Thread.Sleep(1);
                                                    }
                                                }
                                                string accountFilePath = Path.Combine(DefaultDirectory, item.アカウント名, path_tmp_account.Key + "_sinceid2.txt");
                                                //System.Windows.Forms.MessageBox.Show(accountFilePath);
                                                if (File.Exists(accountFilePath))
                                                {
                                                    FileInfo fileInfo = new FileInfo(accountFilePath);
                                                    DateTime lastWriteTime = fileInfo.LastWriteTime;
                                                    //System.Windows.Forms.MessageBox.Show(lastWriteTime+":"+path_tmp_account.Value);

                                                    // 最終更新日時が異なる場合、または初回の場合
                                                    if (path_tmp_account.Value == null || lastWriteTime != path_tmp_account.Value)
                                                    {
                                                        string[] lines = File.ReadAllLines(accountFilePath, Encoding.UTF8);

                                                        // 各行に対してリプライを投稿
                                                        foreach (var line in lines)
                                                        {
                                                            if (!string.IsNullOrWhiteSpace(line.Trim()))
                                                            {
                                                                try
                                                                {
                                                                    投稿(item.コメント, item.画像, item.動画, line.Trim(), item.アカウント名, item.プロキシURL);
                                                                }
                                                                catch (Exception ex)
                                                                {
                                                                    try
                                                                    {
                                                                        string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                                        string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                                        // ファイルにテキストを書き込む
                                                                        using (var writer = File.AppendText(filePath))
                                                                        {
                                                                            writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "でエラーです。" + ex.Message);
                                                                        }
                                                                    }
                                                                    catch { }
                                                                }
                                                                await WaitRandomTime(3000, 5000);  // ランダムに待機
                                                                if (path_tmp_account.Value == null)
                                                                {
                                                                    break;  // 最初のリプライ投稿後にループを抜ける
                                                                }
                                                            }
                                                            if (finishflag)
                                                            {
                                                                break;
                                                            }
                                                            if (interruption)
                                                            {
                                                                while (interruption && !finishflag)
                                                                {
                                                                    Thread.Sleep(1);
                                                                }
                                                            }
                                                        }
                                                    }
                                                }
                                            }
                                        }
                                    }

                                    for (int i = 0; i < settime; i++)
                                    {
                                        if (finishflag)
                                            break;
                                        if (interruption)
                                        {
                                            while (interruption && !finishflag)
                                            {
                                                Thread.Sleep(1);
                                            }
                                        }
                                        await Task.Delay(1000); // 1秒待機
                                    }
                                }
                            }
                            catch { }
                            finally
                            {
                                this.Dispatcher.Invoke((Action)(() =>
                                {
                                    開始.Content = "開始";
                                    開始.IsEnabled = true;
                                }));
                            }
                        }
                        else if (yoyaku)
                        {
                            try
                            {
                                var now = DateTime.Now;
                                TimeSpan timeSpan;
                                string format = "hh\\:mm\\:ss";
                                // アカウント分繰り返す 予約時間を確認
                                while (!finishflag)
                                {
                                    // 時価を格納
                                    var timelist = new List<List<string>>();
                                    foreach (var item in info)
                                    {
                                        try
                                        {
                                            // 実行確認
                                            if (!item.実行確認 || string.IsNullOrWhiteSpace(item.カスタマーキー) || string.IsNullOrWhiteSpace(item.カスタマーシークレット) || string.IsNullOrWhiteSpace(item.アクセストークン) || string.IsNullOrWhiteSpace(item.アクセストークンシークレット) || string.IsNullOrWhiteSpace(item.ベアラトークン) || string.IsNullOrWhiteSpace(item.リフレッシュトークン) || string.IsNullOrWhiteSpace(item.クライアントID) || string.IsNullOrWhiteSpace(item.クライアントシークレットID))
                                            {
                                                continue;
                                            }

                                            var tmp_timelist = new List<string>();
                                            var tmptime = item.予約投稿時間.Replace("\r\n", "\n").Replace("終了", "").Trim();
                                            var sp_tmptime = tmptime.Split('\n');
                                            foreach (var s in sp_tmptime)
                                            {
                                                if (TimeSpan.TryParseExact(s + ":00", format, CultureInfo.CurrentCulture, out timeSpan))
                                                {
                                                    var d = now.Date;
                                                    DateTime todayTime = d.Add(timeSpan); // 現在の日付に時間を追加
                                                                                          // 過ぎてるなら
                                                    if (DateTime.Now > todayTime)
                                                    {
                                                        tmp_timelist.Add(s + " 終了");
                                                    }
                                                    else
                                                    {
                                                        tmp_timelist.Add(s);
                                                    }
                                                }
                                            }

                                            timelist.Add(tmp_timelist);
                                        }
                                        catch { }
                                    }

                                    while (!finishflag)
                                    {
                                        // 格納した時間で処理
                                        int i = 0;
                                        foreach (var item in info)
                                        {
                                            try
                                            {
                                                if (finishflag)
                                                {
                                                    break;
                                                }
                                                if (interruption)
                                                {
                                                    while (interruption && !finishflag)
                                                    {
                                                        Thread.Sleep(1);
                                                    }
                                                }
                                                // 実行確認
                                                if (!item.実行確認 || string.IsNullOrWhiteSpace(item.カスタマーキー) || string.IsNullOrWhiteSpace(item.カスタマーシークレット) || string.IsNullOrWhiteSpace(item.アクセストークン) || string.IsNullOrWhiteSpace(item.アクセストークンシークレット) || string.IsNullOrWhiteSpace(item.ベアラトークン) || string.IsNullOrWhiteSpace(item.リフレッシュトークン) || string.IsNullOrWhiteSpace(item.クライアントID) || string.IsNullOrWhiteSpace(item.クライアントシークレットID))
                                                {
                                                    continue;
                                                }

                                                if (!Directory.Exists(Path.Combine(DefaultDirectory, item.アカウント名)))
                                                {
                                                    Directory.CreateDirectory(Path.Combine(DefaultDirectory, item.アカウント名));
                                                }

                                                // キーを書き込む
                                                if (!File.Exists(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt")))
                                                {
                                                    File.WriteAllText(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt"), item.カスタマーキー.Trim() + "\n" + item.カスタマーシークレット.Trim() + "\n" + item.アクセストークン.Trim() + "\n" + item.アクセストークンシークレット.Trim() + "\n" + item.ベアラトークン.Trim() + "\n" + item.リフレッシュトークン.Trim() + "\n" + item.クライアントID.Trim() + "\n" + item.クライアントシークレットID.Trim());
                                                }
                                            }
                                            catch { }

                                            if (finishflag)
                                            {
                                                break;
                                            }
                                            if (interruption)
                                            {
                                                while (interruption && !finishflag)
                                                {
                                                    Thread.Sleep(1);
                                                }
                                            }
                                            for (var j = 0; j < timelist[i].Count; j++)
                                            {
                                                try
                                                {
                                                    if (TimeSpan.TryParseExact(timelist[i][j] + ":00", format, CultureInfo.CurrentCulture, out timeSpan) && !timelist[i][j].EndsWith("終了"))
                                                    {
                                                        var d = now.Date;
                                                        DateTime todayTime = d.Add(timeSpan); // 現在の日付に時間を追加

                                                        // 過ぎてるなら
                                                        if (DateTime.Now > todayTime)
                                                        {
                                                            // 投稿
                                                            try
                                                            {
                                                                投稿(item.コメント, item.画像, item.動画, "", item.アカウント名, item.プロキシURL);
                                                            }
                                                            catch (Exception ex)
                                                            {
                                                                try
                                                                {
                                                                    string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                                    string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                                    // ファイルにテキストを書き込む
                                                                    using (var writer = File.AppendText(filePath))
                                                                    {
                                                                        writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "でエラーです。" + ex.Message);
                                                                    }
                                                                }
                                                                catch { }
                                                            }
                                                            timelist[i][j] += " 終了";
                                                        }

                                                        if (finishflag)
                                                        {
                                                            break;
                                                        }
                                                        if (interruption)
                                                        {
                                                            while (interruption && !finishflag)
                                                            {
                                                                Thread.Sleep(1);
                                                            }
                                                        }
                                                    }
                                                }
                                                catch { }
                                            }
                                            i++;
                                            System.Windows.Forms.Application.DoEvents();
                                            if (finishflag)
                                            {
                                                break;
                                            }
                                            if (interruption)
                                            {
                                                while (interruption && !finishflag)
                                                {
                                                    Thread.Sleep(1);
                                                }
                                            }
                                        }

                                        if (now.Date != DateTime.Now.Date)
                                        {
                                            break;
                                        }

                                        await WaitRandomTime(5000, 10000);
                                    }

                                    now = DateTime.Now;
                                }
                            }
                            catch { }
                            finally
                            {
                                this.Dispatcher.Invoke((Action)(() =>
                                {
                                    開始.Content = "開始";
                                    開始.IsEnabled = true;
                                }));
                            }
                        }
                        else if (monomane)
                        {
                            try
                            {
                                // アカウント分繰り返す 監視アカウントを取り出す
                                while (!finishflag)
                                {
                                    // 1分おきに実行
                                    int settime = 60;
                                    foreach (var item in info)
                                    {
                                        string account = item.監視アカウント;
                                        if (!string.IsNullOrWhiteSpace(account) && item.実行確認)
                                        {
                                            // 実行確認
                                            if (string.IsNullOrWhiteSpace(item.カスタマーキー) || string.IsNullOrWhiteSpace(item.カスタマーシークレット) || string.IsNullOrWhiteSpace(item.アクセストークン) || string.IsNullOrWhiteSpace(item.アクセストークンシークレット) || string.IsNullOrWhiteSpace(item.ベアラトークン) || string.IsNullOrWhiteSpace(item.リフレッシュトークン) || string.IsNullOrWhiteSpace(item.クライアントID) || string.IsNullOrWhiteSpace(item.クライアントシークレットID))
                                            {
                                                continue;
                                            }

                                            if (!Directory.Exists(Path.Combine(DefaultDirectory, item.アカウント名)))
                                            {
                                                Directory.CreateDirectory(Path.Combine(DefaultDirectory, item.アカウント名));
                                            }

                                            // キーを書き込む
                                            if (!File.Exists(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt")))
                                            {
                                                File.WriteAllText(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt"), item.カスタマーキー.Trim() + "\n" + item.カスタマーシークレット.Trim() + "\n" + item.アクセストークン.Trim() + "\n" + item.アクセストークンシークレット.Trim() + "\n" + item.ベアラトークン.Trim() + "\n" + item.リフレッシュトークン.Trim() + "\n" + item.クライアントID.Trim() + "\n" + item.クライアントシークレットID.Trim());
                                            }

                                            var tmp_account = account.Trim();
                                            var sp = tmp_account.Replace("\r\n", "\n").Split('\n');

                                            // 各アカウントに対して処理を行う
                                            foreach (var s in sp)
                                            {
                                                string path_tmp_account = SanitizeFilename(s.Replace("@", "").Trim());
                                                // search_tweet3.exe プロセスを開始
                                                ProcessStartInfo startInfo = new ProcessStartInfo
                                                {
                                                    CreateNoWindow = true,  // ウィンドウを表示しない
                                                    UseShellExecute = false,  // シェルを使用しない
                                                    FileName = "search_tweet3.exe",
                                                    RedirectStandardError = true,
                                                    Arguments = $"\"{path_tmp_account}\" \"{Path.Combine(DefaultDirectory, item.アカウント名)}\" \"{item.プロキシURL}\" \"{item.DMMID}\""
                                                };

                                                using (Process process = new Process { StartInfo = startInfo })
                                                {
                                                    process.Start();  // プロセスを開始
                                                    string error = process.StandardError.ReadToEnd();
                                                    process.WaitForExit();  // プロセスの終了を待つ
                                                    int exitCode = process.ExitCode;
                                                    if (exitCode != 0)
                                                    {
                                                        try
                                                        {
                                                            string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                            string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                            // ファイルにテキストを書き込む
                                                            using (var writer = File.AppendText(filePath))
                                                            {
                                                                writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "のモノマネ投稿でエラーです。" + error);
                                                            }
                                                        }
                                                        catch { }
                                                    }
                                                }
                                            }

                                            // key.txt の内容を読み込み、item に設定
                                            string keyFilePath = Path.Combine(DefaultDirectory, item.アカウント名, "key.txt");
                                            string fileContent = File.ReadAllText(keyFilePath);
                                            var f_sp = fileContent.Replace("\r\n", "\n").Split('\n');
                                            item.カスタマーキー = f_sp[0].Trim();
                                            item.カスタマーシークレット = f_sp[1].Trim();
                                            item.アクセストークン = f_sp[2].Trim();
                                            item.アクセストークンシークレット = f_sp[3].Trim();
                                            item.ベアラトークン = f_sp[4].Trim();
                                            item.リフレッシュトークン = f_sp[5].Trim();
                                            item.クライアントID = f_sp[6].Trim();
                                            item.クライアントシークレットID = f_sp[7].Trim();

                                            await WaitRandomTime(2000, 4000);  // ランダムに待機

                                            if (finishflag)
                                            {
                                                break;  // finishflag が true の場合、ループを抜ける
                                            }
                                        }
                                    }

                                    for (int i = 0; i < settime; i++)
                                    {
                                        if (finishflag)
                                            break;
                                        if (interruption)
                                        {
                                            while (interruption && !finishflag)
                                            {
                                                Thread.Sleep(1);
                                            }
                                        }
                                        await Task.Delay(1000); // 1秒待機
                                    }
                                }
                            }
                            catch { }
                            finally
                            {
                                this.Dispatcher.Invoke((Action)(() =>
                                {
                                    開始.Content = "開始";
                                    開始.IsEnabled = true;
                                }));
                            }
                        }
                        else
                        {
                            try
                            {
                                // アカウント分繰り返す
                                foreach (var item in info)
                                {
                                    try
                                    {
                                        if (finishflag)
                                        {
                                            return;
                                        }
                                        if (interruption)
                                        {
                                            while (interruption && !finishflag)
                                            {
                                                Thread.Sleep(1);
                                            }
                                        }

                                        // 実行確認
                                        if (!item.実行確認 || string.IsNullOrWhiteSpace(item.カスタマーキー) || string.IsNullOrWhiteSpace(item.カスタマーシークレット) || string.IsNullOrWhiteSpace(item.アクセストークン) || string.IsNullOrWhiteSpace(item.アクセストークンシークレット) || string.IsNullOrWhiteSpace(item.ベアラトークン) || string.IsNullOrWhiteSpace(item.リフレッシュトークン) || string.IsNullOrWhiteSpace(item.クライアントID) || string.IsNullOrWhiteSpace(item.クライアントシークレットID))
                                        {
                                            continue;
                                        }

                                        if (!Directory.Exists(Path.Combine(DefaultDirectory, item.アカウント名)))
                                        {
                                            Directory.CreateDirectory(Path.Combine(DefaultDirectory, item.アカウント名));
                                        }

                                        // キーを書き込む
                                        if (!File.Exists(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt")))
                                        {
                                            File.WriteAllText(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt"), item.カスタマーキー.Trim() + "\n" + item.カスタマーシークレット.Trim() + "\n" + item.アクセストークン.Trim() + "\n" + item.アクセストークンシークレット.Trim() + "\n" + item.ベアラトークン.Trim() + "\n" + item.リフレッシュトークン.Trim() + "\n" + item.クライアントID.Trim() + "\n" + item.クライアントシークレットID.Trim());
                                        }

                                        ProcessStartInfo startInfo = new ProcessStartInfo();
                                        startInfo.CreateNoWindow = true;  // ウィンドウを表示しない
                                        startInfo.UseShellExecute = false;  // シェルを使用しない

                                        if (replymode || bookgoodmode)
                                        {
                                            try
                                            {
                                                // リプライ用URL分繰り返す
                                                foreach (var url in url_sp)
                                                {
                                                    if (!IsUrl(url))
                                                    {
                                                        continue;
                                                    }


                                                    // いいね
                                                    if (can_good)
                                                    {
                                                        startInfo.FileName = "good_tweet.exe";
                                                        startInfo.RedirectStandardError = true;
                                                        startInfo.Arguments = $"\"{getid(url)}\" \"{Path.Combine(DefaultDirectory, item.アカウント名)}\" \"{item.プロキシURL}\"";
                                                        using (Process process = new Process())
                                                        {
                                                            process.StartInfo = startInfo;

                                                            // プロセスを開始
                                                            process.Start();
                                                            string error = process.StandardError.ReadToEnd();

                                                            // プロセスの終了を待つ
                                                            process.WaitForExit();
                                                            int exitCode = process.ExitCode;
                                                            if (exitCode != 0)
                                                            {
                                                                try
                                                                {
                                                                    string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                                    string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                                    // ファイルにテキストを書き込む
                                                                    using (var writer = File.AppendText(filePath))
                                                                    {
                                                                        writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "のいいねでエラーです。" + error);
                                                                    }
                                                                }
                                                                catch { }
                                                            }
                                                        }
                                                        await WaitRandomTime(3000, 5000);
                                                    }

                                                    if (finishflag)
                                                    {
                                                        return;
                                                    }
                                                    if (interruption)
                                                    {
                                                        while (interruption && !finishflag)
                                                        {
                                                            Thread.Sleep(1);
                                                        }
                                                    }

                                                    if (can_bokmark)
                                                    {
                                                        // ブックマーク
                                                        startInfo.FileName = "bookmark_tweet.exe";
                                                        startInfo.RedirectStandardError = true;
                                                        startInfo.Arguments = $"\"{getid(url)}\" \"{Path.Combine(DefaultDirectory, item.アカウント名)}\" \"{item.プロキシURL}\"";
                                                        using (Process process = new Process())
                                                        {
                                                            process.StartInfo = startInfo;

                                                            // プロセスを開始
                                                            process.Start();
                                                            string error = process.StandardError.ReadToEnd();

                                                            // プロセスの終了を待つ
                                                            process.WaitForExit();
                                                            int exitCode = process.ExitCode;
                                                            if (exitCode != 0)
                                                            {
                                                                try
                                                                {
                                                                    string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                                    string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                                    // ファイルにテキストを書き込む
                                                                    using (var writer = File.AppendText(filePath))
                                                                    {
                                                                        writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "のブックマークでエラーです。" + error);
                                                                    }
                                                                }
                                                                catch { }
                                                            }
                                                        }

                                                        // keyを反映
                                                        string fileContent = File.ReadAllText(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt"));
                                                        var f_sp = fileContent.Replace("\r\n", "\n").Split('\n');
                                                        item.カスタマーキー = f_sp[0].Trim();
                                                        item.カスタマーシークレット = f_sp[1].Trim();
                                                        item.アクセストークン = f_sp[2].Trim();
                                                        item.アクセストークンシークレット = f_sp[3].Trim();
                                                        item.ベアラトークン = f_sp[4].Trim();
                                                        item.リフレッシュトークン = f_sp[5].Trim();
                                                        item.クライアントID = f_sp[6].Trim();
                                                        item.クライアントシークレットID = f_sp[7].Trim();

                                                        await WaitRandomTime(3000, 5000);
                                                    }

                                                    if (finishflag)
                                                    {
                                                        return;
                                                    }
                                                    if (interruption)
                                                    {
                                                        while (interruption && !finishflag)
                                                        {
                                                            Thread.Sleep(1);
                                                        }
                                                    }

                                                    if (can_retweet)
                                                    {
                                                        // リツイート
                                                        startInfo.FileName = "retweet_tweet.exe";
                                                        startInfo.RedirectStandardError = true;
                                                        startInfo.Arguments = $"\"{getid(url)}\" \"{Path.Combine(DefaultDirectory, item.アカウント名)}\" \"{item.プロキシURL}\"";
                                                        using (Process process = new Process())
                                                        {
                                                            process.StartInfo = startInfo;

                                                            // プロセスを開始
                                                            process.Start();
                                                            string error = process.StandardError.ReadToEnd();
                                                            // プロセスの終了を待つ
                                                            process.WaitForExit();
                                                            int exitCode = process.ExitCode;
                                                            if (exitCode != 0)
                                                            {
                                                                try
                                                                {
                                                                    string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                                    string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                                    // ファイルにテキストを書き込む
                                                                    using (var writer = File.AppendText(filePath))
                                                                    {
                                                                        writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "のリツイートでエラーです。" + error);
                                                                    }
                                                                }
                                                                catch { }
                                                            }
                                                        }

                                                        await WaitRandomTime(3000, 5000);
                                                    }

                                                    if (finishflag)
                                                    {
                                                        return;
                                                    }
                                                    if (interruption)
                                                    {
                                                        while (interruption && !finishflag)
                                                        {
                                                            Thread.Sleep(1);
                                                        }
                                                    }

                                                    //ブックマークといいねモード
                                                    if (bookgoodmode)
                                                    {
                                                        Thread.Sleep(1000);
                                                        continue;
                                                    }

                                                    if (finishflag)
                                                    {
                                                        return;
                                                    }
                                                    if (interruption)
                                                    {
                                                        while (interruption && !finishflag)
                                                        {
                                                            Thread.Sleep(1);
                                                        }
                                                    }

                                                    // 投稿
                                                    try
                                                    {
                                                        投稿(item.コメント, item.画像, item.動画, url, item.アカウント名, item.プロキシURL);
                                                    }
                                                    catch (Exception ex)
                                                    {
                                                        try
                                                        {
                                                            string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                            string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                            // ファイルにテキストを書き込む
                                                            using (var writer = File.AppendText(filePath))
                                                            {
                                                                writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "でエラーです。" + ex.Message);
                                                            }
                                                        }
                                                        catch { }
                                                    }

                                                    await WaitRandomTime(3000, 5000);

                                                }
                                            }
                                            catch
                                            {
                                            }
                                        }
                                        else if (postmode)
                                        {
                                            // 投稿
                                            try
                                            {
                                                投稿(item.コメント, item.画像, item.動画, "", item.アカウント名, item.プロキシURL);
                                            }
                                            catch (Exception ex)
                                            {
                                                try
                                                {
                                                    string desktopPath = Environment.GetFolderPath(Environment.SpecialFolder.Desktop);
                                                    string filePath = Path.Combine(desktopPath, "Twitter投稿errorlog.txt");

                                                    // ファイルにテキストを書き込む
                                                    using (var writer = File.AppendText(filePath))
                                                    {
                                                        writer.Write(DateTime.Now.ToString("g") + "：" + item.アカウント名 + "でエラーです。" + ex.Message);
                                                    }
                                                }
                                                catch { }
                                            }
                                            await WaitRandomTime(3000, 5000);
                                        }
                                    }
                                    catch { }
                                }
                            }
                            catch { }
                            finally
                            {
                                this.Dispatcher.Invoke((Action)(() =>
                                {
                                    開始.Content = "開始";
                                    開始.IsEnabled = true;
                                }));
                            }
                        }
                    }
                    catch (Exception ex)
                    {
                        System.Windows.Forms.MessageBox.Show(ex.Message);
                    }
                });
                開始.Content = "開始";
            }
            else
            {
                cts.Cancel();
                finishflag = true;
                開始.Content = "開始";
                開始.IsEnabled = false;
                System.Windows.Forms.Application.DoEvents();
                infosave();
            }
        }

        private void 画像選択_MouseDoubleClick(object sender, MouseButtonEventArgs e)
        {
            var result = System.Windows.Forms.MessageBox.Show("【はい】フォルダから\n【いいえ】単一ファイルから", "選択", MessageBoxButtons.YesNoCancel, MessageBoxIcon.Question);
            if (result == System.Windows.Forms.DialogResult.Yes)
            {
                using (var cofd = new CommonOpenFileDialog()
                {
                    Title = "画像フォルダを選択してください",
                    // フォルダ選択モードにする
                    IsFolderPicker = true,
                    InitialDirectory = "C:\\"
                })
                {
                    if (cofd.ShowDialog() != CommonFileDialogResult.Ok)
                    {
                        return;
                    }

                    var TB = (System.Windows.Controls.TextBox)sender;
                    TB.Text = cofd.FileName;
                }
            }
            else if (result == System.Windows.Forms.DialogResult.No)
            {
                using (var cofd = new CommonOpenFileDialog()
                {
                    Title = "画像ファイルを選択してください",
                    // ファイル選択モードにする
                    IsFolderPicker = false,
                    InitialDirectory = "C:\\"
                })
                {
                    if (cofd.ShowDialog() != CommonFileDialogResult.Ok)
                    {
                        return;
                    }

                    var TB = (System.Windows.Controls.TextBox)sender;
                    TB.Text = cofd.FileName;
                }
            }
        }

        private void 動画選択_MouseDoubleClick(object sender, MouseButtonEventArgs e)
        {
            var result = System.Windows.Forms.MessageBox.Show("【はい】フォルダから\n【いいえ】単一ファイルから", "選択", MessageBoxButtons.YesNoCancel, MessageBoxIcon.Question);
            if (result == System.Windows.Forms.DialogResult.Yes)
            {
                using (var cofd = new CommonOpenFileDialog()
                {
                    Title = "動画フォルダを選択してください",
                    // フォルダ選択モードにする
                    IsFolderPicker = true,
                    InitialDirectory = "C:\\"
                })
                {
                    if (cofd.ShowDialog() != CommonFileDialogResult.Ok)
                    {
                        return;
                    }

                    var TB = (System.Windows.Controls.TextBox)sender;
                    TB.Text = cofd.FileName;
                }
            }
            else if (result == System.Windows.Forms.DialogResult.No)
            {
                using (var cofd = new CommonOpenFileDialog()
                {
                    Title = "動画ファイルを選択してください",
                    // ファイル選択モードにする
                    IsFolderPicker = false,
                    InitialDirectory = "C:\\"
                })
                {
                    if (cofd.ShowDialog() != CommonFileDialogResult.Ok)
                    {
                        return;
                    }

                    var TB = (System.Windows.Controls.TextBox)sender;
                    TB.Text = cofd.FileName;
                }
            }
        }

        private void Chrome削除_Click(object sender, RoutedEventArgs e)
        {
            var result = System.Windows.Forms.MessageBox.Show("他のアプリに影響を及ぼす可能性がありますがよろしいですか？", "選択", MessageBoxButtons.OKCancel, MessageBoxIcon.Question);
            if (result == System.Windows.Forms.DialogResult.OK)
            {
                var result2 = System.Windows.Forms.MessageBox.Show("chromeのプロセスも削除しますか？", "選択", MessageBoxButtons.OKCancel, MessageBoxIcon.Question);
                if (result2 == System.Windows.Forms.DialogResult.OK)
                {
                    using (var p = Process.Start("chromekill2.bat"))
                    {
                        p.WaitForExit();
                    }
                }
                else
                {
                    using (var p = Process.Start("chromekill.bat"))
                    {
                        p.WaitForExit();
                    }
                }
            }
        }

        private void Window_Closed(object sender, EventArgs e)
        {
            infosave();
        }

        private void infosave()
        {
            Properties.Settings.Default.info.Clear();
            foreach (var item in info)
            {
                var list = new List<string>
                {
                    item.実行確認.ToString(),
                    item.アカウント名,
                    item.カスタマーキー,
                    item.カスタマーシークレット,
                    item.アクセストークン,
                    item.アクセストークンシークレット,
                    item.ベアラトークン,
                    item.リフレッシュトークン,
                    item.クライアントID,
                    item.クライアントシークレットID,
                    item.コメント,
                    item.画像,
                    item.動画,
                    item.メモ,
                    item.監視アカウント,
                    item.予約投稿時間,
                    item.プロキシURL,
                    item.DMMID
                };

                Properties.Settings.Default.info.Add(list);
            }

            Properties.Settings.Default.いいねcheck = (bool)いいねcheck.IsChecked;
            Properties.Settings.Default.ブックマークcheck = (bool)ブックマークcheck.IsChecked;
            Properties.Settings.Default.リツイートcheck = (bool)リツイートcheck.IsChecked;
            Properties.Settings.Default.リプライ対象URL = リプライ対象URL.Text;
            Properties.Settings.Default.キー入力 = キー入力.Text;
            Properties.Settings.Default.デフォルトフォルダ = デフォルトフォルダ.Text;
            Properties.Settings.Default.ファイル削除 = (bool)ファイル削除.IsChecked;
            Properties.Settings.Default.Save();
        }

        private void BANリスト_Click(object sender, RoutedEventArgs e)
        {
            if (!File.Exists("BANリスト.txt"))
            {
                using (StreamWriter sw = new StreamWriter("BANリスト.txt", true))
                {
                }
            }

            Process.Start("BANリスト.txt");
        }

        private static readonly HttpClient HttpClient = new HttpClient();
        private async Task<string> PostTweetAsync(string accessToken, string text)
        {
            var tweetEndpoint = "https://api.twitter.com/2/tweets";

            // JSONコンテンツを作成し、Content-Typeヘッダーを設定
            var content = new StringContent($"{{ \"text\": \"{text}\" }}", System.Text.Encoding.UTF8, "application/json");

            // Authorizationヘッダーを追加
            HttpClient.DefaultRequestHeaders.Authorization = new AuthenticationHeaderValue("Bearer", accessToken);

            // POSTリクエストを送信
            var response = await HttpClient.PostAsync(tweetEndpoint, content);

            // レスポンス内容を取得
            var result = await response.Content.ReadAsStringAsync();

            // ステータスコードが成功を示していない場合、例外をスロー
            response.EnsureSuccessStatusCode();

            return result;
        }

        private void キー保存_Click(object sender, RoutedEventArgs e)
        {
            try
            {
                // kキーを書き込む
                File.WriteAllText("first_accesskey.txt", キー入力.Text);
                System.Windows.Forms.MessageBox.Show("キーを更新しました", "", MessageBoxButtons.OK, MessageBoxIcon.Information);
            }
            catch { }
        }

        private void キー入手_Click(object sender, RoutedEventArgs e)
        {
            if (File.Exists("first_accesskey.txt"))
            {
                // プロセスを開始
                Process.Start("getaccesskey_tweet.exe");
            }
            else
            {
                System.Windows.Forms.MessageBox.Show("キーのテキストファイルがありません", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
            }
        }

        private void csvインポート_Click(object sender, RoutedEventArgs e)
        {
            // OpenFileDialog をインスタンス化
            using (OpenFileDialog openFileDialog = new OpenFileDialog())
            {

                // ダイアログのタイトルを設定
                openFileDialog.Title = "CSVファイルを選択してください";

                // 初期ディレクトリを設定（オプション）
                openFileDialog.InitialDirectory = @"C:\";

                // ファイルの種類を設定（オプション）
                openFileDialog.Filter = "CSVファイル|*.csv";

                // ダイアログを表示し、ユーザーが OK をクリックしたら選択されたファイルのパスを取得
                if (openFileDialog.ShowDialog() == System.Windows.Forms.DialogResult.OK)
                {
                    // 選択されたファイルのパスを表示
                    string filename = openFileDialog.FileName;
                    List<CsvRecord> data = ReadCsv(filename);
                    if (data.Count == 0)
                    {
                        System.Windows.Forms.MessageBox.Show("データが取得できませんでした", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                        return;
                    }

                    info.Clear();
                    foreach (var d in data)
                    {
                        Data data1 = new Data();
                        data1.実行確認 = true;
                        data1.アカウント名 = d.プロファイル名;
                        data1.コメント = d.コメント;
                        data1.画像 = d.画像;
                        data1.動画 = d.動画;
                        data1.メモ = d.メモ;
                        data1.カスタマーキー = d.カスタマーキー;
                        data1.カスタマーシークレット = d.カスタマーシークレットキー;
                        data1.アクセストークン = d.アクセスキー;
                        data1.アクセストークンシークレット = d.アクセスシークレットキー;
                        data1.ベアラトークン = d.ベアラトークン;
                        data1.リフレッシュトークン = d.リフレッシュトークン;
                        data1.クライアントID = d.クライアントID;
                        data1.クライアントシークレットID = d.クライアントシークレットID;
                        data1.監視アカウント = d.監視アカウント;
                        data1.予約投稿時間 = d.予約投稿時間;
                        data1.プロキシURL = d.プロキシURL;
                        data1.DMMID = d.DMMID;
                        info.Add(data1);
                    }
                }
            }
        }

        public class CsvRecord
        {
            [Index(0)]
            public string プロファイル名 { get; set; }

            [Index(1)]
            public string コメント { get; set; }

            [Index(2)]
            public string 画像 { get; set; }

            [Index(3)]
            public string 動画 { get; set; }

            [Index(4)]
            public string メモ { get; set; }

            [Index(5)]
            public string 監視アカウント { get; set; }

            [Index(6)]
            public string 予約投稿時間 { get; set; }

            [Index(7)]
            public string カスタマーキー { get; set; }

            [Index(8)]
            public string カスタマーシークレットキー { get; set; }

            [Index(9)]
            public string アクセスキー { get; set; }

            [Index(10)]
            public string アクセスシークレットキー { get; set; }

            [Index(11)]
            public string ベアラトークン { get; set; }

            [Index(12)]
            public string リフレッシュトークン { get; set; }

            [Index(13)]
            public string クライアントID { get; set; }

            [Index(14)]
            public string クライアントシークレットID { get; set; }

            [Index(15)]
            public string プロキシURL { get; set; }

            [Index(16)]
            public string DMMID { get; set; }
        }

        public static List<CsvRecord> ReadCsv(string filePath)
        {
            var config = new CsvConfiguration(System.Globalization.CultureInfo.InvariantCulture)
            {
                HasHeaderRecord = true,
                ShouldQuote = (context) => true,
                MissingFieldFound = null // 欠落しているフィールドを無視
            };

            var records = new List<CsvRecord>();

            try
            {
                using (var reader = new StreamReader(filePath, Encoding.GetEncoding("Shift_JIS")))
                using (var csv = new CsvReader(reader, config))
                {
                    records = csv.GetRecords<CsvRecord>().ToList();
                }

                return records;
            }
            catch
            {
                // エラーが発生した場合、エラーログを出力するなどの処理を追加することも検討してください
                return records;
            }

        }

        public static void getcsv()
        {
            string desktopDirectoryPath = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
            var config = new CsvConfiguration(System.Globalization.CultureInfo.InvariantCulture);
            config.HasHeaderRecord = true;
            if (File.Exists(desktopDirectoryPath + "\\Twitter投稿ツール用.csv"))
            {
                System.Windows.Forms.MessageBox.Show("既にデスクトップにTwitter投稿ツール用.csvがあります");
                return;
            }
            config.ShouldQuote = (context) => true;
            using (StreamWriter writer = new StreamWriter(desktopDirectoryPath + "\\Twitter投稿ツール用.csv", true, Encoding.GetEncoding("Shift_JIS")))
            using (var csv = new CsvWriter(writer, config))
            {
                csv.WriteRecords(new List<CsvRecord>());
            }
            System.Windows.Forms.MessageBox.Show("デスクトップにcsvを生成しました");
        }

        private void 専用CSV取得_Click(object sender, RoutedEventArgs e)
        {
            getcsv();
        }

        private void exportCSV()
        {
            string desktopDirectoryPath = Environment.GetFolderPath(Environment.SpecialFolder.DesktopDirectory);
            var config = new CsvConfiguration(System.Globalization.CultureInfo.InvariantCulture);
            config.HasHeaderRecord = true;
            if (File.Exists(desktopDirectoryPath + "\\Twitter投稿ツールエクスポート.csv"))
            {
                System.Windows.Forms.MessageBox.Show("既にデスクトップにTwitter投稿ツールエクスポート.csvがあります");
                return;
            }

            if (info.Count == 0)
            {
                System.Windows.Forms.MessageBox.Show("エクスポートするデータがありません");
                return;
            }

            var data = new List<CsvRecord>();
            foreach (var d in info)
            {
                CsvRecord data1 = new CsvRecord();
                data1.プロファイル名 = d.アカウント名;
                data1.コメント = d.コメント;
                data1.画像 = d.画像;
                data1.動画 = d.動画;
                data1.メモ = d.メモ;
                data1.カスタマーキー = "";
                data1.カスタマーシークレットキー = "";
                data1.アクセスキー = d.アクセストークン;
                data1.アクセスシークレットキー = d.アクセストークンシークレット;
                data1.ベアラトークン = d.ベアラトークン;
                data1.リフレッシュトークン = d.リフレッシュトークン;
                data1.クライアントID = "";
                data1.クライアントシークレットID = "";
                data1.監視アカウント = d.監視アカウント;
                data1.予約投稿時間 = d.予約投稿時間;
                data1.プロキシURL = d.プロキシURL;
                data1.DMMID = d.DMMID;
                data.Add(data1);
            }

            config.ShouldQuote = (context) => true;
            using (StreamWriter writer = new StreamWriter(desktopDirectoryPath + "\\Twitter投稿ツールエクスポート.csv", true, Encoding.GetEncoding("Shift_JIS")))
            using (var csv = new CsvWriter(writer, config))
            {
                csv.WriteRecords(new List<CsvRecord>());
                csv.WriteRecords(data);
            }
            System.Windows.Forms.MessageBox.Show("デスクトップにcsvを生成しました");
        }
        private void csvエクスポート_Click(object sender, RoutedEventArgs e)
        {
            exportCSV();
        }

        private void デフォルトフォルダ参照_Click(object sender, RoutedEventArgs e)
        {
            using (var cofd = new CommonOpenFileDialog()
            {
                Title = "デフォルトフォルダを選択してください",
                // フォルダ選択モードにする
                IsFolderPicker = true,
                InitialDirectory = "C:\\"
            })
            {
                if (cofd.ShowDialog() != CommonFileDialogResult.Ok)
                {
                    return;
                }

                デフォルトフォルダ.Text = cofd.FileName;
            }
        }

        private void デフォルトフォルダ_TextChanged(object sender, System.Windows.Controls.TextChangedEventArgs e)
        {
            DefaultDirectory = デフォルトフォルダ.Text;
        }

        private void 手動キー更新_Click(object sender, RoutedEventArgs e)
        {
            var button = sender as System.Windows.Controls.Button;
            var dataGridRow = DataGridRow.GetRowContainingElement(button);
            var item = dataGridRow.DataContext as Data; // YourDataType はデータソースの型

            if (!Directory.Exists(DefaultDirectory))
            {
                System.Windows.Forms.MessageBox.Show("デフォルトのフォルダ設定ができていません", "エラー", MessageBoxButtons.OK, MessageBoxIcon.Error);
                return;
            }

            if (!Directory.Exists(Path.Combine(DefaultDirectory, item.アカウント名)))
            {
                Directory.CreateDirectory(Path.Combine(DefaultDirectory, item.アカウント名));
            }

            if (item != null)
            {
                // ファイルに書き込む
                File.WriteAllText(Path.Combine(DefaultDirectory, item.アカウント名, "key.txt"), item.カスタマーキー.Trim() + "\n" + item.カスタマーシークレット.Trim() + "\n" + item.アクセストークン.Trim() + "\n" + item.アクセストークンシークレット.Trim() + "\n" + item.ベアラトークン.Trim() + "\n" + item.リフレッシュトークン.Trim() + "\n" + item.クライアントID.Trim() + "\n" + item.クライアントシークレットID.Trim());

                System.Windows.Forms.MessageBox.Show("更新完了");
            }
        }

        private static bool nushi = true;
        private void Window_Loaded(object sender, RoutedEventArgs e)
        {
#if 認証
            using (認証Form form = new 認証Form())
            {
                form.OptionName = AppTypes.Twitterリプライ等自動化_API.ToString();
                var result = form.ShowDialog();

                if (result == System.Windows.Forms.DialogResult.No)
                {
                    this.IsEnabled = false;
                    return;
                }
            }
#endif
            if (!nushi)
            {
                ブックマークいいねラジオボタン.Visibility = Visibility.Hidden;
                いいねcheck.Visibility = Visibility.Hidden;
                ブックマークcheck.Visibility |= Visibility.Hidden;
                リツイートcheck.Visibility = Visibility.Hidden;
            }
        }

        private async void StartWebSocketClient()
        {
            _client = new ClientWebSocket();

            try
            {
                // サーバーに接続
                await _client.ConnectAsync(new Uri("ws://203.137.95.22:5000/"), CancellationToken.None);
                UpdateMessages("Connected to the server");

                // メッセージを受信
                await ReceiveMessages();
            }
            catch (WebSocketException ex)
            {
                UpdateMessages($"WebSocket error: {ex.Message}");
            }
        }

        private async Task ReceiveMessages()
        {
            byte[] buffer = new byte[1024];
            while (_client.State == WebSocketState.Open)
            {
                WebSocketReceiveResult result;
                try
                {
                    // サーバーからのメッセージを待機
                    result = await _client.ReceiveAsync(new ArraySegment<byte>(buffer), CancellationToken.None);

                    if (result.MessageType == WebSocketMessageType.Text)
                    {
                        string message = Encoding.UTF8.GetString(buffer, 0, result.Count);
                        UpdateMessages($"Received: {message}");

                        var msgs = message.Split(';').ToList();

                        bool can_good = false;
                        bool can_bookmark = false;
                        bool can_retweet = false;
                        string[] url = { };// = string.Empty;

                        foreach (var msg in msgs)
                        {
                            if (msg.StartsWith("good="))
                            {
                                string value = msg.Substring("good=".Length);
                                if (value == "true") can_good = true;
                            }
                            else if (msg.StartsWith("bookmark="))
                            {
                                string value = msg.Substring("bookmark=".Length);
                                if (value == "true") can_good = true;
                            }
                            else if (msg.StartsWith("retweet="))
                            {
                                string value = msg.Substring("retweet=".Length);
                                if (value == "true") can_good = true;
                            }
                            else if (msg.StartsWith("url1="))
                            {
                                // 配列サイズを1つ増やす
                                Array.Resize(ref url, url.Length + 1);
                                // 配列の最後に新しい要素を追加
                                url[url.Length - 1] = msg.Substring("url1=".Length);
                            }
                            else if (msg.StartsWith("url2="))
                            {
                                // 配列サイズを1つ増やす
                                Array.Resize(ref url, url.Length + 1);
                                // 配列の最後に新しい要素を追加
                                url[url.Length - 1] = msg.Substring("url2=".Length);
                            }
                            else if (msg.StartsWith("url3="))
                            {
                                // 配列サイズを1つ増やす
                                Array.Resize(ref url, url.Length + 1);
                                // 配列の最後に新しい要素を追加
                                url[url.Length - 1] = msg.Substring("url3=".Length);
                            }
                            else if (msg.StartsWith("url4="))
                            {
                                // 配列サイズを1つ増やす
                                Array.Resize(ref url, url.Length + 1);
                                // 配列の最後に新しい要素を追加
                                url[url.Length - 1] = msg.Substring("url4=".Length);
                            }
                            else if (msg.StartsWith("url5="))
                            {
                                // 配列サイズを1つ増やす
                                Array.Resize(ref url, url.Length + 1);
                                // 配列の最後に新しい要素を追加
                                url[url.Length - 1] = msg.Substring("url5=".Length);
                            }
                            else if (msg.StartsWith("url6="))
                            {
                                // 配列サイズを1つ増やす
                                Array.Resize(ref url, url.Length + 1);
                                // 配列の最後に新しい要素を追加
                                url[url.Length - 1] = msg.Substring("url6=".Length);
                            }
                            else if (msg.StartsWith("url7="))
                            {
                                // 配列サイズを1つ増やす
                                Array.Resize(ref url, url.Length + 1);
                                // 配列の最後に新しい要素を追加
                                url[url.Length - 1] = msg.Substring("url7=".Length);
                            }
                            else if (msg.StartsWith("url=8"))
                            {
                                // 配列サイズを1つ増やす
                                Array.Resize(ref url, url.Length + 1);
                                // 配列の最後に新しい要素を追加
                                url[url.Length - 1] = msg.Substring("url8=".Length);
                            }
                            else if (msg.StartsWith("url9="))
                            {
                                // 配列サイズを1つ増やす
                                Array.Resize(ref url, url.Length + 1);
                                // 配列の最後に新しい要素を追加
                                url[url.Length - 1] = msg.Substring("url9=".Length);
                            }
                            else if (msg.StartsWith("url10="))
                            {
                                // 配列サイズを1つ増やす
                                Array.Resize(ref url, url.Length + 1);
                                // 配列の最後に新しい要素を追加
                                url[url.Length - 1] = msg.Substring("url10=".Length);
                            }
                        }

                        開始処理(can_good, can_bookmark, can_retweet, url);

                    }
                    else if (result.MessageType == WebSocketMessageType.Close)
                    {
                        UpdateMessages("Server is closing the connection...");
                        break;
                    }
                }
                catch (WebSocketException ex)
                {
                    UpdateMessages($"WebSocket error during receive: {ex.Message}");
                    break;
                }
            }

            // 接続を閉じる
            await _client.CloseAsync(WebSocketCloseStatus.NormalClosure, "Closing", CancellationToken.None);
            UpdateMessages("WebSocket connection closed");
        }

        private void UpdateMessages(string message)
        {
            if (!Dispatcher.CheckAccess())
            {
                Dispatcher.Invoke(() => txtMessages.AppendText(message + Environment.NewLine));
            }
            else
            {
                txtMessages.AppendText(message + Environment.NewLine);
            }
        }

        private void 開始_Click(object sender, RoutedEventArgs e)
        {

        }
        private void 中断切り替え()
        {
            if (interruption)
            {
                interruption = false;
            }
            else
            {
                interruption = true;
            }
        }

        private void 中断_Click(object sender, RoutedEventArgs e)
        {
            中断切り替え();
            if (interruption)
            {
                中断.Content = "中断中…";
            }
            else
            {
                中断.Content = "中断";
            }
            System.Windows.Forms.Application.DoEvents();
        }
    }
}
