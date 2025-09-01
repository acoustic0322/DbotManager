using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{

    public class CheckTweetAccountList
    {
        public string AccountName { get; set; }
        public long UserId { get; set; }
        public DateTime CheckTime { get; set; }
        public DateTime UpdateTime { get; set; }
        public string TweetId { get; set; }
        public string TweetText { get; set; }
        public TweetProcTypes Type { get; set; }
        public string ReplyToTweetId { get; set; }
    }
}
