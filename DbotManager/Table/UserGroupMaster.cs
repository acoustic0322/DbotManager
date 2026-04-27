using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class UserGroupMaster
    {
        public int Id { get; set; }
        public string Name { get; set; }
        public bool Enable { get; set; }
        public string Memo { get; set; }
    }
}
