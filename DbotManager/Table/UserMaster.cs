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
        public bool PhotoEnable { get; set; }

        public bool MovieEnable { get; set; }


    }
}
