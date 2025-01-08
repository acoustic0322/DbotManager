using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class SearchList
    {
        public int Id { get; set; }

        public string SearchUserName { get; set; }
        public int SearchUserId { get; set; }
        public int SearchAccountId { get; set; }
        public int PostAccountId { get; set; }
        public int ReplyAccountId { get; set; }
        public int MonomaneAccountId { get; set; }
        public bool? Enable { get; set; }
        public bool? PostEnable { get; set; }
        public bool? ReplyEnable { get; set; }
        public bool? MonomaneEnable { get; set; }
        public string LastPostId { get; set; }
        public string LastReplyId { get; set; }
        public string LastMonomaneId { get; set; }

        public DateTime? LastPostTime { get; set; }
        public DateTime? LastReplyTime { get; set; }
        public DateTime? LastMonomaneTime { get; set; }


        // データベース非管理
        public int CheckInterval { get; set; }
        public DateTime CheckDate { get; set; }
        public bool FirstFlag { get; set; }

    }
}
