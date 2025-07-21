using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ChildTweet
{
    using System;
    using System.Net;
    using System.Text;
    using System.Text.Json;
    using System.Threading.Tasks;

    public class TweetHttpServer
    {
        private HttpListener _listener;
        private bool _isRunning;

        public Action<string> LogOutput { get; set; }  // ログ出力先
        public int Port { get; set; }

        public void Start()
        {
            _listener = new HttpListener();

            // 変更前（これだと+:5000で全ポートを要求するのでNG）
//            _listener.Prefixes.Add("http://+:5000/");
            // 変更後（localhost:5000 だけを対象とする。通常ユーザーでOK）
            _listener.Prefixes.Add($"http://localhost:{Port}/");

            _listener.Start();
            _isRunning = true;

            Log($"✅ サーバー起動中 (http://localhost:{Port})");

            Task.Run(() => ListenLoop());
//            Console.WriteLine("✅ サーバー起動中 (http://localhost:5000)");
        }

        public void Stop()
        {
            _isRunning = false;
            _listener?.Stop();
            Log("🛑 サーバー停止");
        }

        private void Log(string message)
        {
            LogOutput?.Invoke($"[{DateTime.Now:MM/dd HH:mm:ss}] {message}");
        }

        private async Task ListenLoop()
        {
            while (_isRunning)
            {
                try
                {
                    var context = await _listener.GetContextAsync();
                    _ = Task.Run(() => HandleRequest(context));
                }
                catch (HttpListenerException) { break; }
            }
        }

        private async Task HandleRequest(HttpListenerContext context)
        {
            string path = context.Request.Url.AbsolutePath;
            if (context.Request.HttpMethod == "POST" && path == "/run")
            {
                using var reader = new StreamReader(context.Request.InputStream, context.Request.ContentEncoding);
                string body = await reader.ReadToEndAsync();
                var data = JsonSerializer.Deserialize<TweetRequest>(body);

                // 非同期でバックグラウンド処理を開始
                //                Task.Run(() => ProcessTweet(data));

                //                Task.Run(() =>
                //                {
                //                    var processor = new TweetProcess(Log);
                //                    processor.Execute(data);
                //                });

                var processor = new TweetProcess(Log);
                await processor.ExecuteAsync(data); // 呼び出し側が async メソッドである必要があります

                // レスポンス
                string responseText = JsonSerializer.Serialize(new { status = "success", message = "Received" });
                byte[] buffer = Encoding.UTF8.GetBytes(responseText);
                context.Response.ContentType = "application/json";
                context.Response.ContentEncoding = Encoding.UTF8;
                await context.Response.OutputStream.WriteAsync(buffer, 0, buffer.Length);
                context.Response.Close();
            }
            else
            {
                context.Response.StatusCode = 404;
                context.Response.Close();
            }
        }

        private void ProcessTweet(TweetRequest req)
        {
            Console.WriteLine($"▶ tweet_id: {req.tweet_id}");
            Log($"ChildTweetweet実行 TweetId={req.tweet_id}");

            Log($"┗いいね処理");
            foreach (var id in req.like_list)
            {
                Log($"　┗🖤 いいね実行 ID={id}");
                Thread.Sleep(100); // 擬似処理
            }

            Log($"┗ブックマーク処理");
            foreach (var id in req.bookmark_list)
            {
                Log($"　┗🔖 ブックマーク実行 ID={id}");
                Thread.Sleep(100);
            }
            // 以降、repost や reply 処理も同様に記述
        }
    }

    public class TweetRequest
    {
        public string tweet_id { get; set; }
        public List<int> like_list { get; set; }
        public List<int> bookmark_list { get; set; }
        public List<int> repost_list { get; set; }
        public List<ReplyItem> reply_list { get; set; }
        public bool rep_to_rep { get; set; }
    }

    public class ReplyItem
    {
        public int AccountId { get; set; }
        public int CommentId { get; set; }
    }

}
