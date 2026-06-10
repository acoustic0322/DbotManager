using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public enum RegistTypes
    {
        Normal,
        React
    }

    public class AccountMaster
    {
        public int Id { get; set; }
        public int VpsId { get; set; }
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
        public bool? Reserve1Ai { get; set; }
        public bool? Reserve2Ai { get; set; }
        public bool? Reserve3Ai { get; set; }
        public bool? Reserve4Ai { get; set; }

        public int CheckInterval { get; set; }
        public int CheckRepInterval { get; set; }
        public int MonomaneInterval { get; set; }

        public bool? SearchEnable { get; set; }



        public string GROQ_API_KEY { get; set; }
        public string OPENAI_API_KEY { get; set; }
        public int? AiMode { get; set; }
        public bool? AiPostEnable { get; set; }
        public bool? AiReplyEnable { get; set; }
        public string AiPostPrompt { get; set; }
        public string AiReplyPrompt { get; set; }

        public bool? AiPhotoEnable { get; set; }
        public bool? AiMovieEnable { get; set; }
        public int AiMediaSelectionRate { get; set; }

        // TweetTask用
        public int? CommentId { get; set; }
        public int? PhotoId { get; set; }
        public int? MovieId { get; set; }

        // 表示用プロパティ
        public string DisplayText => $"{Id}:{Name}";

        public bool UseAdminApi { get; set; }
        public int ApiMasterId { get; set; }

        public bool IsLocked { get; set; }
        public bool IsSuspended { get; set; }
        public bool IsUnauthorized { get; set; }

        public string BearerToken_1 { get; set; }
        public string RefreshToken_1 { get; set; }
        public string BearerToken_2 { get; set; }
        public string RefreshToken_2 { get; set; }
        public string BearerToken_3 { get; set; }
        public string RefreshToken_3 { get; set; }
        public RegistTypes RegistType { get; set; }

        public string AuthToken { get; set; }
        public string Cookies { get; set; }
        public string UserAgent { get; set; }
        public string SecChUa { get; set; }
        public string Inpersonate { get; set; }
        public string GroupId { get; set; }
        public string GroupName { get; set; }
        public string Category { get; set; }


    }
}
