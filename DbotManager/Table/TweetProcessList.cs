using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{

    /*

  `id` int NOT NULL AUTO_INCREMENT,
  `user_id` int DEFAULT NULL,
  `updatetime` datetime DEFAULT NULL,
  `tweet_id` varchar(45) DEFAULT NULL,
  `like_enable` tinyint DEFAULT NULL,
  `bookmark_enable` tinyint DEFAULT NULL,
  `reply_enable` tinyint DEFAULT NULL,
  `repost_enable` tinyint DEFAULT NULL,
  `like_count` int DEFAULT NULL,
  `bookmark_count` int DEFAULT NULL,
  `reply_count` int DEFAULT NULL,
  `repost_count` int DEFAULT NULL,
  `dumplicate` tinyint DEFAULT '1',
  `exe_flag` tinyint DEFAULT '0',     
     * */


    public class TweetProcessList
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public DateTime UpdateTime { get; set; }
        public string TweetId { get; set; }
        public bool LikeEnable { get; set; }
        public bool BookmarkEnable { get; set; }
        public bool ReplyEnable { get; set; }
        public bool RepToRep { get; set; }
        public bool RepostEnable { get; set; }
        public int LikeCount { get; set; }
        public int JapLikeCount { get; set; }
        public int BookmarkCount { get; set; }
        public int ReplyCount { get; set; }
        public int RepostCount { get; set; }
        public int SensyukenMode { get; set; }
        public bool Dumplicate { get; set; }
        public bool ExeFlag { get; set; }
    }
}
