using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class ReserveScheduleView
    {
        public string UserName { get; set; }
        public int AccountId { get; set; }
        public string AccountName { get; set; }
        public string Comment { get; set; }
        public DateTime? ReserveTime { get; set; }
        public bool Result { get; set; }
        public string ReserveId { get; set; }

    }
}
