using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class AccountMaster
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public string Name { get; set; }
        public string LoginId { get; set; }
        public string LoginPass { get; set; }
        public string ApiKey { get; set; }
        public string ApiKeySecret { get; set; }
        public string ClientId { get; set; }
        public string ClientSecret { get; set; }
        public string AccessToken { get; set; }
        public string AccessTokenSecret { get; set; }
        public string BearerToken { get; set; }
        public string RefreshToken { get; set; }
        public bool Enable { get; set; }
        public bool LikeEnable { get; set; }
        public bool ReplyEnable { get; set; }
        public bool BookMarkEnable { get; set; }
        public bool RepostEnable { get; set; }
        public bool PostEnable { get; set; }
        public bool Paid { get; set; }
        public bool PaidLike { get; set; }
        public bool PaidBookmark { get; set; }
        public bool Reserve1Enable { get; set; }
        public bool Reserve2Enable { get; set; }
        public bool Reserve3Enable { get; set; }
        public bool Reserve4Enable { get; set; }
        public int Reserve1StartHour { get; set; }
        public int Reserve2StartHour { get; set; }
        public int Reserve3StartHour { get; set; }
        public int Reserve4StartHour { get; set; }
        public int Reserve1EndHour { get; set; }
        public int Reserve2EndHour { get; set; }
        public int Reserve3EndHour { get; set; }
        public int Reserve4EndHour { get; set; }
        public int Reserve1Count { get; set; }
        public int Reserve2Count { get; set; }
        public int Reserve3Count { get; set; }
        public int Reserve4Count { get; set; }

        public int CheckInterval { get; set; }
        public int CheckRepInterval { get; set; }
        public int MonomaneInterval { get; set; }


        // TweetTask用
        public int? CommentId { get; set; }
        public int? PhotoId { get; set; }
        public int? MovieId { get; set; }

    }
}
