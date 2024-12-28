using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class CheckUserMaster
    {
        public int Id { get; set; }
        public string UserName { get; set; }
        public string UserId { get; set; }
        public DateTime UpdateTime { get; set; }
        public string SinceId { get; set; }
        public string SinceComment { get; set; }

    }
}
