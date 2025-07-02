using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class TweetWatch
    {
        public string UserName { get; set; }
        public string PostId { get; set; }
        public string PostText { get; set; }
        public DateTime PostDateTime { get; set; }
        public string ReplyId { get; set; }
        public string ReplyText { get; set; }
        public DateTime ReplyDateTime { get; set; }
        public DateTime WatchDateTime { get; set; }

        public string ReplyToUser { get; set; }

    }
}
