using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class ReserveMaster
    {
        public int AccountId { get; set; }
        public bool Reserve1Enable { get; set; }
        public bool Reserve2Enable { get; set; }
        public bool Reserve3Enable { get; set; }
        public int Reserve1StartHour { get; set; }
        public int Reserve2StartHour { get; set; }
        public int Reserve3StartHour { get; set; }
        public int Reserve1EndHour { get; set; }
        public int Reserve2EndHour { get; set; }
        public int Reserve3EndHour { get; set; }
        public int Reserve1Count { get; set; }
        public int Reserve2Count { get; set; }
        public int Reserve3Count { get; set; }
    }
}
