using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace ChildTweet
{
    internal class TweetProcess
    {
        private readonly Action<string> _log;

        public TweetProcess(Action<string> logger)
        {
            _log = logger ?? Console.WriteLine;
        }

        public void Execute(TweetRequest req)
        {
            _log($"▶ tweet_id: {req.tweet_id}");
            _log($"┗いいね処理");

            foreach (var id in req.like_list)
            {
                _log($"　┗🖤 いいね実行 ID={id}");
                Thread.Sleep(100); // 擬似処理
            }

            _log($"┗ブックマーク処理");
            foreach (var id in req.bookmark_list)
            {
                _log($"　┗🔖 ブックマーク実行 ID={id}");
                Thread.Sleep(100);
            }

            // TODO: repost, reply も追加
        }
    }
}
