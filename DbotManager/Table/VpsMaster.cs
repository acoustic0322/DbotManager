using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class VpsMaster
    {
        public int Id { get; set; }
        public string IpAddress { get; set; }
        public string Port { get; set; }
        public string Name { get; set; }
        public string Username { get; set; }
        public string Pass { get; set; }
        public string Memo { get; set; }

    }
}
