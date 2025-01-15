using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class TweetHistory
    {
        public string UserName { get; set; }
        public int AccountId { get; set; }
        public string AccountName { get; set; }
        public bool Paid { get; set; }
        public TweetProcTypes Mode { get; set; }
        public string TargetTweetID { get; set; }
        public string Comment { get; set; }
        public DateTime? UpdateTime { get; set; }
        public string ErrorLog { get; set; }
        public bool Result { get; set; }
    }
}
