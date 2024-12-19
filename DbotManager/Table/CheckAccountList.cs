using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class CheckAccountList
    {
        public int Id { get; set; }
        public int AccountId { get; set; }
        public bool Enable { get; set; }
        public TweetProcTypes Mode { get; set; }
        public string CheckAccount { get; set; }


        public List<int> ExeAccountIdList { get; set; }
        public string ExeAccountNameList { get; set; }
        public DateTime? SinceDatetime { get; set; }
        public string SinceTweetId { get; set; }



    }
}
