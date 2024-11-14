using DbotManager.Table;
using System;
using System.Collections.Generic;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager
{
    public class TweetTask
    {
        private string dbMachineName;
        private string dbUser;
        private string dbRoot;
        private string dbPass;

        public TweetTask(string dbMachineName, string dbUser, string dbRoot, string dbPass)
        {
            this.dbMachineName = dbMachineName;
            this.dbUser = dbUser;
            this.dbRoot = dbRoot;
            this.dbPass = dbPass;
        }

        public enum TweetProcTypes
        {
            LIKE,
            BOOKMARK,
            TWEET
        }

        public TweetProcTypes TweetProcType { get; set; }

        public int 件数 { get; set; }
        public string TargetTweetID { get; set; }

        public List<AccountMaster> TweetAccountList { get; set; }

        public void StartTask()
        {

        }

        public void InitAccountList()
        {
            List<AccountMaster> retList = new List<AccountMaster>();

            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbMachineName, dbUser, dbRoot, dbPass);

            // 過去TargetTweetID宛に処理済みだった場合は省くため、リスト抽出
            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistoryView().Where(x => x.TargetTweetID == TargetTweetID && x.ErrorLog == "成功" && x.TweetMode == GetTweetMode(TweetProcType)).ToList();

            List<string> skipAccountIdList = tweetHistoryList.Select(x => x.AccountId).Distinct().ToList();

            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster().ToList();

            foreach(var item in accountMasterList)
            {
                if (skipAccountIdList.Contains(item.Id.ToString())) continue;
                retList.Add(item);
            }

            TweetAccountList = retList;

        }

        private string GetTweetMode(TweetProcTypes type)
        {
            switch(type)
            {
                case TweetProcTypes.LIKE:
                    return "like";
                    break;
                case TweetProcTypes.BOOKMARK:
                    return "bookmark";
                    break;
                case TweetProcTypes.TWEET:
                    return "tweet";
                    break;
            }
            return string.Empty;
        }


    }
}
