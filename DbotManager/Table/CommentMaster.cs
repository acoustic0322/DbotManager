using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public enum TweetModeTypes
    {
        Tweet,
        Replay
    }


    public class CommentMaster
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public int AccountId { get; set; }
        public string Comment { get; set; }
        public bool Enable { get; set; }
        public bool ChatGpt { get; set; }
        public TweetModeTypes TweetModeType { get; set; }
        //        public int PhotoId { get; set; }
        //        public int MovieId { get; set; }
        public bool PhotoEnable { get; set; }
        public bool MovieEnable { get; set; }
    }
}
