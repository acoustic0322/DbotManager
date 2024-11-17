using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public class CommentMaster
    {
        public int Id { get; set; }
        public int UserId { get; set; }
        public int AccountId { get; set; }
        public string Comment { get; set; }
        public bool Enable { get; set; }
        public bool Whole { get; set; }
    }
}
