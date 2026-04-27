using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class UserMaster
    {
        public int Id { get; set; }
        public int GroupId { get; set; }
        public string Name { get; set; }
        public string Password { get; set; }
        public bool Admin { get; set; }
        public bool Enable { get; set; }
        public string Memo { get; set; }
        public bool LikeEnable { get; set; }
        public bool BookmarkEnable { get; set; }
        public bool ReplyEnable { get; set; }
        public bool RepostEnable { get; set; }
        public bool SensyukenEnable { get; set; }
        public bool PostEnable { get; set; }
        public bool ReserveEnable { get; set; }
        public bool MediaEnable { get; set; }
        public bool CheckEnable { get; set; }
        public bool SearchRepEnable { get; set; }
        public string JapApiKey { get; set; }
        /// <summary>
        /// 選手権モード時にAPI処理の対象となるユーザー
        /// </summary>
        public bool SensyukenExec { get; set; }
        /// <summary>
        /// 選手権モード(リプライ)時にAPI処理の対象となるユーザー
        /// </summary>
        public bool SensyukenExecReply { get; set; }


        // 表示用プロパティ
        public string DisplayText => $"{Id}:{Name}";
    }
}
