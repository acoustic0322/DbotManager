using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Entity
{
    public class WebCommand
    {
        public bool Enable { get; set; }
        public string TargetTweetId { get; set; }
        public int UserId { get; set; }
        public bool Like { get; set; }
        public bool Bookmark { get; set; }
        public bool Reply { get; set; }
        public bool Repost { get; set; }
        public int LikeCount { get; set; }
        public int BookmarkCount { get; set; }
        public int ReplyCount { get; set; }
        public int RepostCount { get; set; }
        public bool Duplicate { get; set; }

    }
}
