using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager.Table
{
    public enum MediaTypes
    {
        None,
        Photo,
        Movie
    }

    public class MediaMaster
    {
        public int MediaId {get; set; }
        public int UserId { get; set; }
        public int AccountId { get; set; }
        public string Name { get; set; }
        public DateTime RegisterDate { get; set; }
        public MediaTypes MediaType { get; set; }

    }
}
