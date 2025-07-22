using Newtonsoft.Json;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ChildTweet
{
    public class TweetCommand
    {
        public TweetProcTypes TweetProcType { get; set; }
        public int? UserId { get; set; }
        public int? AccountId { get; set; }
        public int? AccountId2 { get; set; }
        public int? CommentId { get; set; }
        public string TweetId { get; set; }
        public string TweetName { get; set; }
        public int Quantity { get; set; }
        public bool AiEnable { get; set; }
        public int AiMode { get; set; }

        public int? SearchId { get; set; }
        public string CheckAccountName { get; set; }
        public DateTime DateTime { get; set; }

        public MediaTypes MediaType { get; set; }
        public int? MediaId { get; set; }

        public bool DebugMode { get; set; }
        public bool CheckAiRepMode { get; set; }
    }

    public enum MediaTypes
    {
        None,
        Photo,
        Movie
    }

    public enum TweetProcTypes
    {
        いいね,
        ブックマーク,
        リポスト,
        ポスト,
        リプライ,
        ｱｸｾｽﾄｰｸﾝ取得,
        ﾘﾌﾚｯｼｭﾄｰｸﾝ更新,
        モノマネ,
        NONE,
        ポスト監視,
        リプ監視,
        AIリプ監視,
        JAPいいね,
        JAPブックマーク,
        JAPリポスト,
        フォロー追加,
        フォロー解除
    }

    public class TweetResult
    {
        public bool result1 { get; set; }
        public string contents1 { get; set; }
        public bool result2 { get; set; }
        public string contents2 { get; set; }
    }


    internal class TweetProcess
    {
        private string pythonWorkingPath;
        private int waitMin;
        private int waitMax;

        private readonly Action<string> _log;

        public TweetProcess(Action<string> logger)
        {
            _log = logger ?? Console.WriteLine;
        }

        private static readonly ThreadLocal<Random> _rand = new(() => new Random(Guid.NewGuid().GetHashCode()));

        public async Task ExecuteAsync(TweetRequest req)
        {
            ReadIniファイル();

            _log($"▶ tweet_id: {req.tweet_id}");

            await 処理実行("いいね", req.tweet_id, req.like_list, TweetProcTypes.いいね);
            await 処理実行("ブックマーク", req.tweet_id, req.bookmark_list, TweetProcTypes.ブックマーク);
            await 処理実行("リポスト", req.tweet_id, req.repost_list, TweetProcTypes.リポスト);

            _log($"┗リプライ処理");
            foreach (var item in req.reply_list)
            {
                int delay = new Random(Guid.NewGuid().GetHashCode()).Next(waitMin, waitMax);
                _log($"　┗リプライ AccountID={item.AccountId} CommentID={item.CommentId} 待機={delay}mSec - {DateTime.Now:HH:mm:ss.fff}");
                await Task.Delay(delay);

                await TweetProc(new TweetCommand
                {
                    AccountId = item.AccountId,
                    TweetId = req.tweet_id,
                    CommentId = item.CommentId,
                    TweetProcType = TweetProcTypes.リプライ
                });
            }

            _log("✔ 全ての処理が完了しました。");
        }

        private async Task 処理実行(string name, string tweet_id, List<int> ids, TweetProcTypes type)
        {
            _log($"┗{name}処理");
            foreach (var id in ids)
            {
                int delay = new Random(Guid.NewGuid().GetHashCode()).Next(waitMin, waitMax);
                _log($"　┗{name} ID={id} 待機={delay}mSec - {DateTime.Now:HH:mm:ss.fff}");
                await Task.Delay(delay);

                await TweetProc(new TweetCommand
                {
                    AccountId = id,
                    TweetId = tweet_id,
                    TweetProcType = type
                });
            }
        }

        private void ReadIniファイル()
        {
            string baseDir = @"C:\DBotManager\ChildTweet";
            string filePath = Path.Combine(baseDir, "config_tweet.ini");

            // ファイルを読み込み
            if (File.Exists(filePath))
            {
                var lines = File.ReadAllLines(filePath);
                var settings = new Dictionary<string, Dictionary<string, string>>();
                string currentSection = "";

                foreach (var line in lines)
                {
                    if (line.StartsWith("[") && line.EndsWith("]"))
                    {
                        currentSection = line.Trim('[', ']');
                        if (!settings.ContainsKey(currentSection))
                        {
                            settings[currentSection] = new Dictionary<string, string>();
                        }
                    }
                    else if (!string.IsNullOrWhiteSpace(line) && line.Contains('='))
                    {
                        var keyValue = line.Split(new[] { '=' }, 2);
                        if (!string.IsNullOrEmpty(currentSection) && keyValue.Length == 2)
                        {
                            settings[currentSection][keyValue[0].Trim()] = keyValue[1].Trim();
                        }
                    }
                }

                // 設定を確認
                if (settings.ContainsKey("Tweet") && settings["Tweet"].ContainsKey("working"))
                {
                    pythonWorkingPath = settings["Tweet"]["working"];
                    var test = settings["Tweet"]["wait_min"];
                    waitMin = int.Parse(settings["Tweet"]["wait_min"]);
                    waitMax = int.Parse(settings["Tweet"]["wait_max"]);
                }
            }
        }

        public async Task<TweetResult> TweetProc(TweetCommand tweetCommand)
        {
#if DEBUG
            return null;
#endif

            // Pythonスクリプトのパスを指定
            string pythonScriptPath = $@"{pythonWorkingPath}\tweet.py";

            switch (tweetCommand.TweetProcType)
            {
                case TweetProcTypes.いいね:
                case TweetProcTypes.ブックマーク:
                case TweetProcTypes.リポスト:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} tweet_id={tweetCommand.TweetId}";
                    break;

                case TweetProcTypes.リプライ:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} comment_id={tweetCommand.CommentId} tweet_id={tweetCommand.TweetId}";
                    break;
            }

            pythonScriptPath += " debug=False";

            // Pythonの実行ファイルのパスを指定（通常 "python" または "python3" でOK）
            string pythonExePath = "python";

            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = pythonExePath,
                    Arguments = pythonScriptPath,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true,
                    WorkingDirectory = pythonWorkingPath

                }
            };
            // 環境変数を設定
            //            StartInfo.EnvironmentVariables["RUNNING_FROM_CSHARP"] = "1";

            _log($"{DateTime.Now.ToString()} > {pythonScriptPath}");

            TweetResult tweetResult = null;

            try
            {
                process.Start();
                string output = process.StandardOutput.ReadToEnd(); // Pythonスクリプトの標準出力
                string debugMessage = process.StandardError.ReadToEnd();   // Pythonスクリプトの標準エラー
                process.WaitForExit();

                // PythonスクリプトからのJSON結果をデシリアライズ (Newtonsoft.Json)
                tweetResult = JsonConvert.DeserializeObject<TweetResult>(output);

                if (tweetResult != null)
                {
                    Console.WriteLine($"{DateTime.Now.ToString()} < [{tweetResult.result1}]{tweetResult.contents1} [{tweetResult.result2}]{tweetResult.contents2}");

                    _log($"{DateTime.Now.ToString()} < [{tweetResult.result1}]{tweetResult.contents1} [{tweetResult.result2}]{tweetResult.contents2}");
                }
                else
                {
                    Console.WriteLine("Python script returned invalid output.");
                    _log($"{DateTime.Now.ToString()} TweetProc Python script returned invalid output.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception: {ex.Message}");
                _log($"{DateTime.Now.ToString()} TweetProc Exception: {ex.Message}");
            }

            return tweetResult;
        }

        private string GetTweetMode(TweetProcTypes type)
        {
            switch (type)
            {
                case TweetProcTypes.いいね:
                    return "like";
                    break;
                case TweetProcTypes.JAPいいね:
                    return "jap_like";
                    break;
                case TweetProcTypes.リプライ:
                    return "reply";
                    break;
                case TweetProcTypes.ブックマーク:
                    return "bookmark";
                    break;
                case TweetProcTypes.JAPブックマーク:
                    return "jap_bookmark";
                    break;
                case TweetProcTypes.リポスト:
                    return "repost";
                    break;
                case TweetProcTypes.JAPリポスト:
                    return "jap_repost";
                    break;
                case TweetProcTypes.ポスト:
                    return "post";
                    break;
                case TweetProcTypes.ｱｸｾｽﾄｰｸﾝ取得:
                    return "get_access_token";
                    break;
                case TweetProcTypes.ﾘﾌﾚｯｼｭﾄｰｸﾝ更新:
                    return "get_refresh_token";
                    break;
                case TweetProcTypes.モノマネ:
                    return "monomane";
                    break;
                case TweetProcTypes.ポスト監視:
                    return "check";
                    break;
                case TweetProcTypes.リプ監視:
                    return "checkrep";
                    break;

                case TweetProcTypes.AIリプ監視:
                    return "checkairep";
                    break;

                case TweetProcTypes.フォロー追加:
                    return "follow";
                    break;

                case TweetProcTypes.フォロー解除:
                    return "unfollow";
                    break;
            }
            return string.Empty;
        }


    }
}
