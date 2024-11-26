using DbotManager.Table;
using MySqlX.XDevAPI.Common;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;

namespace DbotManager
{
    public enum TweetProcTypes
    {
        LIKE,
        BOOKMARK,
        REPLY,
        TWEET,
        RETWEET,
        GET_ACCESSTOKEN,
        GET_REFRESHTOKEN
    }

    public class TweetTask
    {
        private readonly Action<string> logAction;

        private DbConnectionInfo dbConnectin;

        public TweetTask(DbConnectionInfo dbConnection , Action<string> logAction = null)
        {
            this.logAction = logAction;
            dbConnectin = dbConnection;
        }



        public TweetProcTypes TweetProcType { get; set; }

        public bool LikeEnable { get; set; }
        public bool BookmarkEnable { get; set; }
        public bool ReplyEnable { get; set; }

        public int 件数 { get; set; }
        public string TargetTweetID { get; set; }
        public bool 制限時間以内に履歴ありの無料アカウントを排除 { get; set; }

        public List<AccountMaster> TweetAccountList { get; set; }
        public List<AccountMaster> LikeAccountList { get; set; }
        public List<AccountMaster> BookmarkAccountList { get; set; }
        public List<AccountMaster> ReplyAccountList { get; set; }
        public int いいね件数 { get; set; }
        public int ブックマーク件数 { get; set; }
        public int リプライ件数 { get; set; }

        public void StartTask()
        {
            foreach(var item in TweetAccountList)
            {
                TweetProc(item.UserId , item.Id, 1 ,TargetTweetID);
            }
        }

        public void InitAccountList()
        {
            List<AccountMaster> retList = new List<AccountMaster>();

            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);

            // accountMasterListからskipAccountIdListに含まれないアカウントを抽出
            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistoryView().Where(x => x.Result).ToList();
            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster();  // dataAccess.GetAccountMaster().Where(x => x.Enable).ToList();

            List<AccountMaster> likeList = FilterAccountList(accountMasterList , tweetHistoryList , TweetProcTypes.LIKE);
            List<AccountMaster> bookMarkList = FilterAccountList(accountMasterList, tweetHistoryList, TweetProcTypes.BOOKMARK);
            List<AccountMaster> replyList = FilterAccountList(accountMasterList, tweetHistoryList, TweetProcTypes.REPLY);


            // 除外対象アカウントに含まれないアカウントをフィルタリング
            var フィルタ済アカウントリスト = accountMasterList
                .Where(am => !除外対象アカウント.Contains(am.Id.ToString()))
                .ToList();

            // リストをシャッフルし、上限数を設定
            var random = new Random();
            var shuffledList = フィルタ済アカウントリスト.OrderBy(x => random.Next()).Take(件数).ToList();

            retList.AddRange(shuffledList);

            TweetAccountList = retList;

        }

        private List<AccountMaster> FilterAccountList(List<AccountMaster> accountMasterList, List<TweetHistory> tweetHistoryList, TweetProcTypes tweetProcType)
        {
            List<AccountMaster> retList = new List<AccountMaster>();

            DateTime dateNow = DateTime.Now;

            foreach (var account in accountMasterList)
            {
                // 無効アカウントはスルー
                if (!account.Enable) continue;

                // 処理無効アカウントはスルー
                if (tweetProcType == TweetProcTypes.LIKE && !account.LikeEnable) continue;
                else if (tweetProcType == TweetProcTypes.BOOKMARK && !account.BookMarkEnable) continue;
                else if (tweetProcType == TweetProcTypes.REPLY && !account.ReplyEnable) continue;

                var myHistory = tweetHistoryList.Where(x => x.AccountId == account.Id && x.Result == true).ToList();

                // 対象ツイートIDで処理済みの場合はスルー
                if (myHistory.Where(x => x.TargetTweetID == TargetTweetID).Count() > 0) continue;

                var lastMyHistoryList = myHistory.OrderByDescending(x => x.UpdateTime).ToList();
                if (lastMyHistoryList.Count() > 0)
                {
                    // 最期の処理が同じだった場合はスルー
                    if (lastMyHistoryList.FirstOrDefault().TweetMode == tweetProcType)
                    {
                        continue;
                    }

                    // 無料アカウントは制限時間内の取引を中止
                    if (制限時間以内に履歴ありの無料アカウントを排除 && account.Paid == false)
                    {
                        if (tweetProcType == TweetProcTypes.LIKE)
                        {
                            var lastHistory = lastMyHistoryList.Where(x => x.TweetMode == TweetProcTypes.LIKE).ToList();
                            if(lastHistory.Count > 0)
                            {
                                if ((dateNow - lastHistory.FirstOrDefault().UpdateTime).TotalDays < 1) continue;
                            }
                        }
                        else if (tweetProcType == TweetProcTypes.BOOKMARK || tweetProcType == TweetProcTypes.REPLY)
                        {
                            var lastHistory = lastMyHistoryList.Where(x => x.TweetMode == tweetProcType).ToList();
                            if (lastHistory.Count > 0)
                            {
                                if ((dateNow - lastHistory.FirstOrDefault().UpdateTime).TotalMinutes < 15 ) continue;
                            }
                        }
                    }

                }





                retList.Add(account);
            }

            return retList;
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
                case TweetProcTypes.REPLY:
                    return "retweet";
                    break;
                case TweetProcTypes.TWEET:
                    return "tweet";
                    break;
                case TweetProcTypes.GET_ACCESSTOKEN:
                    return "get_access_token";
                    break;
                case TweetProcTypes.GET_REFRESHTOKEN:
                    return "get_refresh_token";
                    break;
            }
            return string.Empty;
        }

        private void TweetProc(int userId, int accountId, int commentId, string tweetId)
        {
            if (LikeEnable)
            {
                TweetProc(TweetProcTypes.LIKE, userId, accountId, commentId, tweetId);
            }
            if (BookmarkEnable)
            {
                TweetProc(TweetProcTypes.BOOKMARK, userId, accountId, commentId, tweetId);
            }
            if (ReplyEnable)
            {
                TweetProc(TweetProcTypes.REPLY, userId, accountId, commentId, tweetId);
            }

        }

        public void TweetProc(TweetProcTypes tweetProcType, int userId, int accountId, int commentId, string tweetId)
        {


            // Pythonスクリプトのパスを指定
            string pythonScriptPath = @"python\tweet.py";

            switch (tweetProcType)
            {
                case TweetProcTypes.TWEET:
                    pythonScriptPath += $" tweet_mode={GetTweetMode(tweetProcType)} account_id={accountId} comment_id={commentId}";
                    break;
                case TweetProcTypes.LIKE:
                case TweetProcTypes.BOOKMARK:
                case TweetProcTypes.REPLY:
                    pythonScriptPath += $" tweet_mode={GetTweetMode(tweetProcType)} account_id={accountId} tweet_id={tweetId}";
                    break;
                case TweetProcTypes.GET_ACCESSTOKEN:
                    pythonScriptPath += $" tweet_mode={GetTweetMode(tweetProcType)} account_id={accountId}";
                    break;
                case TweetProcTypes.GET_REFRESHTOKEN:
                    pythonScriptPath += $" tweet_mode={GetTweetMode(tweetProcType)} account_id={accountId}";
                    break;
            }

            // Pythonの実行ファイルのパスを指定（通常 "python" または "python3" でOK）
            string pythonExePath = "python";

            

            // プロセス情報の設定
            ProcessStartInfo psi = new ProcessStartInfo
            {
                FileName = pythonExePath,
                Arguments = pythonScriptPath,
                RedirectStandardOutput = true,
                RedirectStandardError = true,
                UseShellExecute = false,
                CreateNoWindow = true
            };

            using (Process process = new Process())
            {
                process.StartInfo = psi;

                process.OutputDataReceived += (s, ea) => logAction?.Invoke(ea.Data);
                process.ErrorDataReceived += (s, ea) => logAction?.Invoke("ERROR: " + ea.Data);


                process.Start();
                process.BeginOutputReadLine();
                process.BeginErrorReadLine();

                // タイムアウトを設定して待機（例えば5秒）
                bool exited = process.WaitForExit(5000);
                if (!exited)
                {
                    logAction?.Invoke("タイムアウト: プロセスが5秒以内に終了しませんでした");
                    process.Kill();
                }

                //                process.WaitForExit();
            }

        }

        public string GetTweetCommand(TweetProcTypes tweetProcType, int userId, int accountId, int commentId, string tweetId)
        {


            // Pythonスクリプトのパスを指定
            string pythonScriptPath = @"python python\tweet.py";

            switch (tweetProcType)
            {
                case TweetProcTypes.TWEET:
                    pythonScriptPath += $" tweet_mode={GetTweetMode(tweetProcType)} account_id={accountId} comment_id={commentId}";
                    break;
                case TweetProcTypes.LIKE:
                    pythonScriptPath += $" tweet_mode={GetTweetMode(tweetProcType)} account_id={accountId} tweet_id={tweetId}";
                    break;
                case TweetProcTypes.BOOKMARK:
                    pythonScriptPath += $" tweet_mode={GetTweetMode(tweetProcType)} account_id={accountId} tweet_id={tweetId}";
                    break;
                case TweetProcTypes.GET_ACCESSTOKEN:
                    pythonScriptPath += $" tweet_mode={GetTweetMode(tweetProcType)} account_id={accountId}";
                    break;
                case TweetProcTypes.GET_REFRESHTOKEN:
                    pythonScriptPath += $" tweet_mode={GetTweetMode(tweetProcType)} account_id={accountId}";
                    break;
            }

            return pythonScriptPath;

        }


    }
}
