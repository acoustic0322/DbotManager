using Newtonsoft.Json;
using System;
using System.Collections.Concurrent;
using System.Collections.Generic;
using System.Diagnostics;
using System.Linq;
using System.Text;
using System.Threading;
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
        private int PARALLEL_COUNT = 5;


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
            var likebookmarkTask = 順次処理_いいねブクマ(req, TweetProcTypes.いいねブックマーク);

            var repostTask = 順次処理(req, TweetProcTypes.リポスト);

            // 2026.06.21 一旦保留
            //var likeTask = 順次処理(req, TweetProcTypes.いいね);
            //var bookmarkTask = 順次処理(req, TweetProcTypes.ブックマーク);
            //var repostTask = 順次処理(req, TweetProcTypes.リポスト);
            //var replyTask = 順次処理(req, TweetProcTypes.リプライ);
            //await Task.WhenAll(likebookmarkTask, likeTask, bookmarkTask, repostTask, replyTask);
            await Task.WhenAll(likebookmarkTask, repostTask);

            _log("✔ 全ての処理が完了しました。");
        }

        private async Task 順次処理_いいねブクマ(TweetRequest req, TweetProcTypes type)
        {
            var orderLikeList = req.like_list?
                .OrderBy(_ => _rand.Value.Next())
                .ToList() ?? new List<int>();

            var orderBookmarkList = req.bookmark_list?
                .OrderBy(_ => _rand.Value.Next())
                .ToList() ?? new List<int>();

            if (orderLikeList.Count == 0 && orderBookmarkList.Count == 0) return;

            // 共通
            var commonList = orderLikeList
                .Intersect(orderBookmarkList)
                .ToList();

            var 並列閾値list = new List<int>();
            int p = PARALLEL_COUNT; // 20
            while (p > 1)
            {
                並列閾値list.Add(p);
                p /= 2;
            }
            並列閾値list.Add(1);

            _log(
                $"❤️🔖 成功目標 ❤️={req.like_count}件 🔖={req.bookmark_count}件" +
                $"並列数初期値={PARALLEL_COUNT}件 " +
                $"いいね・ブクマ共通アカウント数={commonList.Count}件");

            int commonCount = Math.Min(req.like_count, req.bookmark_count);

            // いいね・ブクマの共通処理 共通数をカバーする
            try
            {

                if (commonCount == 0)
                    return;

                var accountQueue = new ConcurrentQueue<int>(commonList);

                var counter = new ProcCounter();
                int 処理カウント = commonCount;
                int step = 1;

                foreach (int 並列閾値 in 並列閾値list)
                {
                    int target =
                        並列閾値 == 1
                            ? 処理カウント
                            : Math.Max(0, 処理カウント - 並列閾値);

                    _log($"並列処理 STEP{step} 成功目標が{target}に到達するまで、並列数{並列閾値}で動作します");

                    await ExecuteParallelPhase(
                        TweetProcTypes.いいねブックマーク,
                        accountQueue,
                        req,
                        並列閾値,
                        target,
                        counter,
                        処理カウント);

                    step++;
                }
            }
            catch (Exception ex)
            {
                _log(ex.ToString());
            }

            // いいね単独数をカバーする
            try
            {

                // いいね専用
                var likeOnlyList = orderLikeList
                    .Except(commonList)
                    .ToList();

                var accountQueue = new ConcurrentQueue<int>(likeOnlyList);

                var counter = new ProcCounter();
                int 処理カウント = req.like_count - commonCount;

                int step = 1;

                foreach (int 並列閾値 in 並列閾値list)
                {
                    int target =
                        並列閾値 == 1
                            ? 処理カウント
                            : Math.Max(0, 処理カウント - 並列閾値);

                    _log($"並列処理 STEP{step} 成功目標が{target}に到達するまで、並列数{並列閾値}で動作します");

                    await ExecuteParallelPhase(
                        TweetProcTypes.いいね,
                        accountQueue,
                        req,
                        並列閾値,
                        target,
                        counter,
                        処理カウント);

                    step++;
                }
            }
            catch (Exception ex)
            {
                _log(ex.ToString());
            }


            // ブックマーク単独数をカバーする
            try
            {
                // ブクマ専用
                var bookmarkOnlyList = orderBookmarkList
                    .Except(commonList)
                    .ToList();

                var accountQueue = new ConcurrentQueue<int>(bookmarkOnlyList);

                var counter = new ProcCounter();
                int 処理カウント = req.bookmark_count - commonCount;

                int step = 1;

                foreach (int 並列閾値 in 並列閾値list)
                {
                    int target =
                        並列閾値 == 1
                            ? 処理カウント
                            : Math.Max(0, 処理カウント - 並列閾値);

                    if (target == 0) continue;

                    _log($"並列処理 STEP{step} 成功目標が{target}に到達するまで、並列数{並列閾値}で動作します");

                    await ExecuteParallelPhase(
                        TweetProcTypes.ブックマーク,
                        accountQueue,
                        req,
                        並列閾値,
                        target,
                        counter,
                        処理カウント);

                    step++;
                }
            }
            catch (Exception ex)
            {
                _log(ex.ToString());
            }
        }

        private async Task 順次処理(TweetRequest req, TweetProcTypes type)
        {
            var orderRepostList = req.repost_list?
                .OrderBy(_ => _rand.Value.Next())
                .ToList() ?? new List<int>();

            if (orderRepostList.Count == 0) return;

            var 並列閾値list = new List<int>();
            int p = PARALLEL_COUNT; // 20
            while (p > 1)
            {
                並列閾値list.Add(p);
                p /= 2;
            }
            並列閾値list.Add(1);

            _log(
                $"🔁 成功目標 repost={req.repost_list.Count}件" +
                $"並列数初期値={PARALLEL_COUNT}件 " +
                $"対象アカウント数={req.repost_list.Count}件");

            // リポスト単独数をカバーする
            try
            {

                // リポスト専用
                var repostOnlyList = orderRepostList
                    //                    .Except(req.repost_list)
                    .ToList();

                var accountQueue = new ConcurrentQueue<int>(repostOnlyList);

                var counter = new ProcCounter();
                int 処理カウント = req.repost_count;

                int step = 1;

                foreach (int 並列閾値 in 並列閾値list)
                {
                    int target =
                        並列閾値 == 1
                            ? 処理カウント
                            : Math.Max(0, 処理カウント - 並列閾値);

                    if (target == 0) continue;

                    _log($"並列処理 STEP{step} 成功目標が{target}に到達するまで、並列数{並列閾値}で動作します");

                    await ExecuteParallelPhase(
                        TweetProcTypes.リポスト,
                        accountQueue,
                        req,
                        並列閾値,
                        target,
                        counter,
                        処理カウント);

                    step++;
                }
            }
            catch (Exception ex)
            {
                _log(ex.ToString());
            }


        }

        class ProcCounter
        {
            public int Like;
            public int Bookmark;
            public int Repost;
        }

        private async Task ExecuteParallelPhase(
            TweetProcTypes type,
            ConcurrentQueue<int> accountQueue,
            TweetRequest req,
            int parallelCount,
            int targetCount,
            ProcCounter counter,
            int max_count)
        {

            bool useLike = type == TweetProcTypes.いいね ||
               type == TweetProcTypes.いいねブックマーク;

            bool useBookmark = type == TweetProcTypes.ブックマーク ||
                               type == TweetProcTypes.いいねブックマーク;

            bool useRepost = type == TweetProcTypes.リポスト;

            var workers = Enumerable.Range(0, parallelCount)
                .Select(_ => Task.Run(async () =>
                {
                    while (true)
                    {
                        bool likeReached =
                            !useLike || Volatile.Read(ref counter.Like) >= targetCount;

                        bool bookmarkReached =
                            !useBookmark || Volatile.Read(ref counter.Bookmark) >= targetCount;

                        bool repostReached =
                            !useRepost || Volatile.Read(ref counter.Repost) >= targetCount;

                        if (likeReached && bookmarkReached && repostReached)
                        {
                            //                            _log($"Reached Like={likeReached} Bookmark={bookmarkReached} Repost={repostReached}");
                            return;
                        }

                        /*
                        if (Volatile.Read(ref counter.Like) >= targetCount &&
                            Volatile.Read(ref counter.Bookmark) >= targetCount)
                        {
                            return;
                        }
                        */

                        if (!accountQueue.TryDequeue(out int accountId))
                        {
                            _log($"accountQueue が空です (accountId={accountId})");
                            return;
                        }

                        try
                        {
                            int delay = _rand.Value.Next(waitMin, waitMax);
                            await Task.Delay(delay);

                            TweetProcTypes procType;

                            procType = type;

                            if (type == TweetProcTypes.いいねブックマーク)
                            {
                                if (likeReached && !bookmarkReached)
                                {
                                    procType = TweetProcTypes.ブックマーク;
                                }
                                else if (!likeReached && bookmarkReached)
                                {
                                    procType = TweetProcTypes.いいね;
                                }
                            }

                            var result = await TweetProc(new TweetCommand
                            {
                                AccountId = accountId,
                                TweetId = req.tweet_id,
                                TweetProcType = procType,
                            });

                            if (result == null)
                                continue;

                            // テスト用
                            /*
                            if (_rand.Value.Next(100) >= 80)
                            {
                                result.result1 = false;
                                _log("result1=false");
                            }

                            if (_rand.Value.Next(100) >= 80)
                            {
                                result.result2 = false;
                                _log("result2=false");
                            }
                            */

                            if (procType == TweetProcTypes.いいねブックマーク)
                            {
                                if (result.result1)
                                {
                                    int count =
                                        Interlocked.Increment(ref counter.Like);

                                    _log(
                                        $"❤️ 成功({count}/{max_count}) " +
                                        $"AccountId={accountId}");
                                }

                                if (result.result2)
                                {
                                    int count =
                                        Interlocked.Increment(ref counter.Bookmark);

                                    _log(
                                        $"🔖 成功({count}/{max_count}) " +
                                        $"AccountId={accountId}");
                                }
                            }
                            else if (procType == TweetProcTypes.いいね)
                            {
                                if (result.result1)
                                {
                                    int count =
                                        Interlocked.Increment(ref counter.Like);

                                    _log(
                                        $"❤️ 成功({count}/{max_count}) " +
                                        $"AccountId={accountId}");
                                }
                            }
                            else if (procType == TweetProcTypes.ブックマーク)
                            {
                                if (result.result1)
                                {
                                    int count =
                                        Interlocked.Increment(ref counter.Bookmark);

                                    _log(
                                        $"🔖 成功({count}/{max_count}) " +
                                        $"AccountId={accountId}");
                                }
                            }
                            else if (procType == TweetProcTypes.リポスト)
                            {
                                if (result.result1)
                                {
                                    int count =
                                        Interlocked.Increment(ref counter.Repost);

                                    _log(
                                        $"🔁 成功({count}/{max_count}) " +
                                        $"AccountId={accountId}");
                                }
                            }
                        }
                        catch (Exception ex)
                        {
                            _log(
                                $"AccountId={accountId} Error={ex.Message}");
                        }
                    }
                }))
                .ToList();

            await Task.WhenAll(workers);
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
                    PARALLEL_COUNT = int.Parse(settings["Tweet"]["parallel_count"]);
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

            _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} START account={tweetCommand.AccountId} {arguments}");

            TweetResult tweetResult = null;

            var sw = System.Diagnostics.Stopwatch.StartNew();

            try
            {
                process.Start();

                // 非同期で同時読取（デッドロック回避）
                Task<string> readOutTask = process.StandardOutput.ReadToEndAsync();
                Task<string> readErrTask = process.StandardError.ReadToEndAsync();

                // タイムアウト（状況に応じて調整：例 60秒）
                using var cts = new CancellationTokenSource(TimeSpan.FromSeconds(120));

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
                        _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} TweetProcタイムアウト account={tweetCommand.AccountId} 経過時間={sw.Elapsed.TotalSeconds:F1}s -> Kill()");
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
                    _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} account={tweetCommand.AccountId}  [stderr]\n{errShort}");
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
                        _log($"Stdout doesn't look like a JSON object. account={tweetCommand.AccountId}  head={jsonText?.Substring(0, Math.Min(80, jsonText.Length))}");
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
                    _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} TweetProc account={tweetCommand.AccountId}  Python script returned invalid or empty JSON.");
                }
            }
            catch (OperationCanceledException)
            {
                _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} TweetProc account={tweetCommand.AccountId} canceled by timeout.");
            }
            catch (Exception ex)
            {
                _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} TweetProc account={tweetCommand.AccountId} Exception: {ex}");
            }
            finally
            {
                _log($"{DateTime.Now:yyyy/MM/dd HH:mm:ss} FINALLY account={tweetCommand.AccountId} elapsed={sw.Elapsed.TotalSeconds:F1}s");

                try
                {
                    if (!process.HasExited)
                        process.Kill(entireProcessTree: true);
                }
                catch { }

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
