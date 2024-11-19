using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class ReserveSchedule
    {
        public DateTime? ReserveDate { get; set; }
        public DateTime? ReserveTime { get; set; }
        public int? UserId { get; set; }
        public int? AccountId { get; set; }
        public int? CommentId { get; set; }
        public string Result { get; set; }
        public string ReserveId { get; set; }
    }

}
