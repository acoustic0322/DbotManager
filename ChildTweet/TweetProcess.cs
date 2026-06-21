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
        いいねブックマーク,
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

            // 各カテゴリを並行で実行（中身は順次処理）
            var likebookmarkTask = 順次処理2(req, TweetProcTypes.いいねブックマーク);

            var likeTask = 順次処理(req, TweetProcTypes.いいね);
            var bookmarkTask = 順次処理(req, TweetProcTypes.ブックマーク);
            var repostTask = 順次処理(req, TweetProcTypes.リポスト);
            var replyTask = 順次処理(req, TweetProcTypes.リプライ);

            await Task.WhenAll(likebookmarkTask, likeTask, bookmarkTask, repostTask, replyTask);

            _log("✔ 全ての処理が完了しました。");
        }

        private async Task 順次処理(TweetRequest req, TweetProcTypes type)
        {

            string symbol = type switch
            {
                TweetProcTypes.いいねブックマーク => "❤️・🔖",
                TweetProcTypes.いいね => "❤️",
                TweetProcTypes.ブックマーク => "🔖",
                TweetProcTypes.リポスト => "🔁",
                _ => "💬"
            };

            string name = type switch
            {
                TweetProcTypes.いいねブックマーク => "likebookmark",
                TweetProcTypes.いいね => "like",
                TweetProcTypes.ブックマーク => "bookmark",
                TweetProcTypes.リポスト => "repost",
                _ => "reply"
            };

            var orderLikeList = req.like_list == null ? null : req.like_list.OrderBy(_ => _rand.Value.Next()).ToList();
            var orderBookmarkList = req.bookmark_list == null ? null : req.bookmark_list.OrderBy(_ => _rand.Value.Next()).ToList();
            // いいね、ブックマーク共通リスト
            var orderLikeBookmarkList =
                orderLikeList == null || orderBookmarkList == null
                    ? new List<int>()
                    : orderLikeList.Intersect(orderBookmarkList).ToList();

            {
                var likeOriginal = orderLikeList?.ToList();
                var bookmarkOriginal = orderBookmarkList?.ToList();

                if (likeOriginal != null && bookmarkOriginal != null)
                {
                    orderLikeList = likeOriginal.Except(bookmarkOriginal).ToList();
                    orderBookmarkList = bookmarkOriginal.Except(likeOriginal).ToList();
                }
            }

            var orderRepostList = req.repost_list == null ? null : req.repost_list.OrderBy(_ => _rand.Value.Next()).ToList();
            var orderReplyList = req.reply_list == null ? null : req.reply_list.OrderBy(_ => _rand.Value.Next()).ToList();

            /*
            List<int> accountIdList = type switch
            {
                TweetProcTypes.いいね => orderLikeList,
                TweetProcTypes.ブックマーク => orderBookmarkList,
                TweetProcTypes.リポスト => orderRepostList,
                _ => orderReplyList.OrderBy(_ => _rand.Value.Next()).ToList().Select(x => x.AccountId).ToList()
            };
            */

            List<int> accountIdList = type switch
            {
                TweetProcTypes.いいねブックマーク => orderLikeBookmarkList ?? new List<int>(),
                TweetProcTypes.いいね => orderLikeList ?? new List<int>(),
                TweetProcTypes.ブックマーク => orderBookmarkList ?? new List<int>(),
                TweetProcTypes.リポスト => orderRepostList ?? new List<int>(),
                _ => orderReplyList == null ? new List<int>() : orderReplyList.OrderBy(_ => _rand.Value.Next()).ToList().Select(x => x.AccountId).ToList()
            };

            int max_count = type switch
            {
                TweetProcTypes.いいねブックマーク => (req.like_count > req.bookmark_count ? req.bookmark_count : req.like_count),
                TweetProcTypes.いいね => req.like_count,
                TweetProcTypes.ブックマーク => req.bookmark_count,
                TweetProcTypes.リポスト => req.repost_count,
                TweetProcTypes.リプライ => req.reply_count,
            };

            if (max_count == 0) return;

            List<int> commmentIdList = type switch
            {
                TweetProcTypes.リプライ => orderReplyList == null ? null : orderReplyList.Select(x => x.CommentId).ToList(),
                _ => null
            };

            bool retryFlag = type switch
            {
                TweetProcTypes.いいねブックマーク => true,
                TweetProcTypes.いいね => true,
                TweetProcTypes.ブックマーク => true,
                TweetProcTypes.リポスト => false,
                TweetProcTypes.リプライ => false,
            };

            _log($"全{accountIdList.Count}件 {symbol}{name}");

            try
            {
                int resultCount = 0;

                for (int i = 0; i < accountIdList.Count; i++)
                {


                    int accountId = accountIdList[i];

                    int commentId = 0;
                    if (req.reply_list != null)
                    {
                        if (req.reply_list.Where(x => x.AccountId == accountIdList[i]).Count() > 0)
                        {
                            commentId = req.reply_list.Where(x => x.AccountId == accountIdList[i]).FirstOrDefault().CommentId;
                        }
                    }

                    int delay = _rand.Value.Next(waitMin, waitMax);

                    _log($"┗{symbol} [{i + 1}/{accountIdList.Count}] AccountId={accountId} 待機={delay}mSec ({name}) [{DateTime.Now:HH:mm:ss.fff}]");
                    await Task.Delay(delay);

                    var result = await TweetProc(new TweetCommand
                    {
                        AccountId = accountId,
                        TweetId = req.tweet_id,
                        TweetProcType = type,
                        CommentId = commentId
                    });

                    if (result is not null)
                    {
                        if (type == TweetProcTypes.いいねブックマーク)
                        {
                            if (result.result1 == true && result.result2 == true)
                            {
                                _log($"　┗【成功】 {symbol} [{i + 1}/{accountIdList.Count}] AccountId={accountId} 待機={delay}mSec ({name}) [{DateTime.Now:HH:mm:ss.fff}]");
                                resultCount++;
                            }
                            else
                            {
                                _log($"　┗【エラー】 {symbol} [{i + 1}/{accountIdList.Count}] AccountId={accountId} 待機={delay}mSec ({name}) [{DateTime.Now:HH:mm:ss.fff}]");
                            }
                        }
                        else
                        {
                            if (result.result1 == true)
                            {
                                _log($"　┗【成功】 {symbol} [{i + 1}/{accountIdList.Count}] AccountId={accountId} 待機={delay}mSec ({name}) [{DateTime.Now:HH:mm:ss.fff}]");
                                resultCount++;
                            }
                            else
                            {
                                _log($"　┗【エラー】 {symbol} [{i + 1}/{accountIdList.Count}] AccountId={accountId} 待機={delay}mSec ({name}) [{DateTime.Now:HH:mm:ss.fff}]");
                            }
                        }
                    }
                    else
                    {
                        int a = 1;
                    }


                    if (resultCount >= max_count)
                    {
                        _log($"{symbol}件数が上限 ({resultCount}件)に達したため、処理を終了します");
                        break;
                    }
                }

            }
            catch (Exception ex)
            {
                _log(ex.ToString());
            }
        }

        private async Task 順次処理2(TweetRequest req, TweetProcTypes type)
        {

            string symbol = "❤️・🔖";

            string name = "likebookmark";

            var orderLikeList = req.like_list == null ? null : req.like_list.OrderBy(_ => _rand.Value.Next()).ToList();
            var orderBookmarkList = req.bookmark_list == null ? null : req.bookmark_list.OrderBy(_ => _rand.Value.Next()).ToList();
            // いいね、ブックマーク共通リスト
            var orderLikeBookmarkList =
                orderLikeList == null || orderBookmarkList == null
                    ? new List<int>()
                    : orderLikeList.Intersect(orderBookmarkList).ToList();

            List<int> accountIdList = orderLikeBookmarkList;

            int max_count =(req.like_count > req.bookmark_count ? req.bookmark_count : req.like_count);

            if (max_count == 0) return;


            bool retryFlag = true;

            _log($"全{accountIdList.Count}件 {symbol}{name}");

            try
            {
                int resultCount_like = 0;
                int resultCount_bookmark = 0;

                for (int i = 0; i < accountIdList.Count; i++)
                {
                    int accountId = accountIdList[i];

                    int delay = _rand.Value.Next(waitMin, waitMax);

                    await Task.Delay(delay);

                    // いいね・ブクマ未達
                    if(resultCount_like < max_count && resultCount_bookmark < max_count)
                    {
                        var result = await TweetProc(new TweetCommand
                        {
                            AccountId = accountId,
                            TweetId = req.tweet_id,
                            TweetProcType = type,
                        });

                        if (result is not null)
                        {
                            if (result.result1 == true)
                            {
                                resultCount_like++;
                                _log($"❤️ 成功({resultCount_like}/{max_count}) AccountId={accountId} 待機={delay}mSec ({name}) 処理カウント={i + 1}/{accountIdList.Count} [{DateTime.Now:HH:mm:ss.fff}]");
                            }
                            else
                            {
                                _log($"❤️ エラー({resultCount_like}/{max_count}) AccountId={accountId} 待機={delay}mSec ({name}) 処理カウント={i + 1}/{accountIdList.Count} [{DateTime.Now:HH:mm:ss.fff}]");
                            }

                            if (result.result2 == true)
                            {
                                resultCount_bookmark++;
                                _log($"🔖 成功({resultCount_bookmark}/{max_count}) AccountId={accountId} 待機={delay}mSec ({name}) 処理カウント={i + 1}/{accountIdList.Count} [{DateTime.Now:HH:mm:ss.fff}]");
                            }
                            else
                            {
                                _log($"🔖 エラー({resultCount_bookmark}/{max_count}) AccountId={accountId} 待機={delay}mSec ({name}) 処理カウント={i + 1}/{accountIdList.Count} [{DateTime.Now:HH:mm:ss.fff}]");
                            }
                        }
                        else
                        {
                            int a = 1;
                        }
                    }
                    // いいね到達
                    else if (resultCount_like >= max_count && resultCount_bookmark < max_count)
                    {
                        var result = await TweetProc(new TweetCommand
                        {
                            AccountId = accountId,
                            TweetId = req.tweet_id,
                            TweetProcType = TweetProcTypes.ブックマーク,
                        });

                        if (result is not null)
                        {
                            if (result.result1 == true)
                            {
                                resultCount_bookmark++;
                                _log($"🔖 成功({resultCount_bookmark}/{max_count}) AccountId={accountId} 待機={delay}mSec ({name}) 処理カウント={i + 1}/{accountIdList.Count} [{DateTime.Now:HH:mm:ss.fff}]");
                            }
                            else
                            {
                                _log($"🔖 エラー({resultCount_bookmark}/{max_count}) AccountId={accountId} 待機={delay}mSec ({name}) 処理カウント={i + 1}/{accountIdList.Count} [{DateTime.Now:HH:mm:ss.fff}]");
                            }
                        }
                        else
                        {
                            int a = 1;
                        }
                    }
                    // ブックマーク到達
                    else if (resultCount_like < max_count && resultCount_bookmark >= max_count)
                    {
                        var result = await TweetProc(new TweetCommand
                        {
                            AccountId = accountId,
                            TweetId = req.tweet_id,
                            TweetProcType = TweetProcTypes.いいね,
                        });

                        if (result is not null)
                        {
                            if (result.result1 == true)
                            {
                                resultCount_like++;
                                _log($"❤️ 成功({resultCount_like}/{max_count}) AccountId={accountId} 待機={delay}mSec ({name}) 処理カウント={i + 1}/{accountIdList.Count} [{DateTime.Now:HH:mm:ss.fff}]");
                            }
                            else
                            {
                                _log($"❤️ エラー({resultCount_like}/{max_count}) AccountId={accountId} 待機={delay}mSec ({name}) 処理カウント={i + 1}/{accountIdList.Count} [{DateTime.Now:HH:mm:ss.fff}]");
                            }
                        }
                        else
                        {
                            int a = 1;
                        }
                    }
                    else
                    {
                        _log($"{symbol}件数が上限 ({max_count}件)に達したため、処理を終了します");
                        break;
                    }

                }

            }
            catch (Exception ex)
            {
                _log(ex.ToString());
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
                    waitMin = int.Parse(settings["Tweet"]["wait_min"]);
                    waitMax = int.Parse(settings["Tweet"]["wait_max"]);
                }
            }
        }

        public async Task<TweetResult> TweetProc(TweetCommand tweetCommand)
        {
            // Pythonファイルへの相対パス
            string pythonScriptPath = @"python\tweet.py";

            // 実行ディレクトリ（ChildTweet.exe と同じ場所想定）
            string baseDir = AppContext.BaseDirectory;
            string fullScriptPath = Path.Combine(baseDir, pythonScriptPath);

            // 引数を組み立て
            string arguments = $"\"{fullScriptPath}\"";
            switch (tweetCommand.TweetProcType)
            {
                case TweetProcTypes.いいねブックマーク:
                case TweetProcTypes.いいね:
                case TweetProcTypes.ブックマーク:
                case TweetProcTypes.リポスト:
                    arguments += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} tweet_id={tweetCommand.TweetId}";
                    break;
                case TweetProcTypes.リプライ:
                    arguments += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} comment_id={tweetCommand.CommentId} tweet_id={tweetCommand.TweetId}";
                    break;
            }
            arguments += " debug=False";

            string pythonExePath = "python";

            var psi = new ProcessStartInfo
            {
                FileName = pythonExePath,
                Arguments = arguments,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true,
                WorkingDirectory = baseDir,
            };

            var process = new Process { StartInfo = psi, EnableRaisingEvents = false };

            _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} > {arguments}");

            TweetResult tweetResult = null;

            try
            {
                process.Start();

                // 非同期で同時読取（デッドロック回避）
                Task<string> readOutTask = process.StandardOutput.ReadToEndAsync();
                Task<string> readErrTask = process.StandardError.ReadToEndAsync();

                // タイムアウト（状況に応じて調整：例 60秒）
                using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(60));

                Task waitTask = Task.Run(async () =>
                {
                    await process.WaitForExitAsync(cts.Token).ConfigureAwait(false);
                }, cts.Token);

                Task finished = await Task.WhenAny(waitTask, Task.Delay(Timeout.Infinite, cts.Token).ContinueWith(_ => Task.CompletedTask));

                // タイムアウト時は Kill
                if (!waitTask.IsCompleted)
                {
                    try
                    {
                        _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} TweetProc TIMEOUT -> Kill()");
                        if (!process.HasExited) process.Kill(entireProcessTree: true);
                    }
                    catch { /* ignore */ }
                }

                // 出力の取得（プロセス終了後でもOK）
                string stdout = await readOutTask.ConfigureAwait(false);
                string stderr = await readErrTask.ConfigureAwait(false);

                //                TweetResult tweetResult = null;

                // まず stderr をログ（長すぎる場合は先頭／末尾だけ）
                if (!string.IsNullOrWhiteSpace(stderr))
                {
                    string errShort = stderr.Length > 4000
                        ? stderr[..2000] + "\n...(truncated)...\n" + stderr[^2000..]
                        : stderr;
                    _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} [stderr]\n{errShort}");
                }

                // stdout から JSON を復元（最後の { 以降に限定すると混入対策になる）
                // もし tweet.py が余計な出力を混ぜる可能性がある場合に備えて、最後の '{' を探す
                string json = stdout;
                int lastBrace = stdout.LastIndexOf('{');
                if (lastBrace >= 0)
                {
                    json = stdout.Substring(lastBrace);
                }


                // 出力の取得
                //                string stdout = await readOutTask.ConfigureAwait(false);
                //              string stderr = await readErrTask.ConfigureAwait(false);

                // ... stderr はログへ

                try
                {
                    // 余計な切り出し禁止。素の stdout をそのまま使う
                    var jsonText = stdout.Trim();

                    // 先頭が { じゃなければパースしない（誤検知回避）
                    if (!string.IsNullOrEmpty(jsonText) && jsonText[0] == '{')
                    {
                        tweetResult = JsonConvert.DeserializeObject<TweetResult>(jsonText);
                    }
                    else
                    {
                        _log($"Stdout doesn't look like a JSON object. head={jsonText?.Substring(0, Math.Min(80, jsonText.Length))}");
                    }
                }
                catch (Exception jex)
                {
                    // 失敗時は生stdoutもログ
                    string outShort = stdout.Length > 4000
                        ? stdout[..2000] + "\n...(truncated)...\n" + stdout[^2000..]
                        : stdout;
                    //                  _log($"JSON Deserialize Error: {jex.Message}\n[stdout]\n{(stdout.Length > 4000 ? stdout[..2000] +\"\\n...(truncated)...\\n\"+stdout[^2000..]: stdout)}");
                    _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} JSON Deserialize Error: {jex.Message}\n[stdout]\n{outShort}");
                }

                /*
                try
                {
                    tweetResult = JsonConvert.DeserializeObject<TweetResult>(json);
                }
                catch (Exception jex)
                {
                    // 失敗時は生stdoutもログ
                    string outShort = stdout.Length > 4000
                        ? stdout[..2000] + "\n...(truncated)...\n" + stdout[^2000..]
                        : stdout;

                    _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} JSON Deserialize Error: {jex.Message}\n[stdout]\n{outShort}");
                }
                */

                if (tweetResult != null)
                {
                    _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} < [{tweetResult.result1}]{tweetResult.contents1} [{tweetResult.result2}]{tweetResult.contents2}");
                }
                else
                {
                    _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} TweetProc Python script returned invalid or empty JSON.");
                }
            }
            catch (OperationCanceledException)
            {
                _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} TweetProc canceled by timeout.");
            }
            catch (Exception ex)
            {
                _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} TweetProc Exception: {ex}");
            }
            finally
            {
                try { if (!process.HasExited) process.Kill(entireProcessTree: true); } catch { }
                process.Dispose();
            }

            return tweetResult;
        }
        private string GetTweetMode(TweetProcTypes type)
        {
            switch (type)
            {
                case TweetProcTypes.いいねブックマーク:
                    return "likebookmark";
                    break;
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
