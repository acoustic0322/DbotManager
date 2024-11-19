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
        public string AccessToken { get; set; }
        public string AccessTokenSecret { get; set; }
        public string BearerToken { get; set; }
        public string RefreshToken { get; set; }
        public bool Enable { get; set; }
        public bool LikeEnable { get; set; }
        public bool BookMarkEnable { get; set; }
        public bool RetweetEnable { get; set; }
        public bool TweetEnable { get; set; }
        public bool Paid { get; set; }
    }
}
