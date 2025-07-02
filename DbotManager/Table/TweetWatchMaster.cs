using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class TweetWatchMaster
    {
        public int AccountId { get; set; }
        public string WatchUserName { get; set; }
        public bool CommentEnable_Tweet { get; set; }
        public bool CommentEnable_Reply { get; set; }
        public bool MonomaneEnable_Tweet { get; set; }
    }
}
