using DbotManager.Table;
using MySqlX.XDevAPI.Common;
using System;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;

namespace DbotManager
{
    public enum TweetProcTypes
    {
        LIKE,
        BOOKMARK,
        RETWEET,
        TWEET,
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
        public bool RetweetEnable { get; set; }

        public int 件数 { get; set; }
        public string TargetTweetID { get; set; }
        public bool 制限時間以内に履歴ありの無料アカウントを排除 { get; set; }

        public List<AccountMaster> TweetAccountList { get; set; }

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

            // 過去TargetTweetID宛に処理済みだった場合は省くため、リスト抽出
            /*
            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistoryView()
                .Where(x => x.TargetTweetID == TargetTweetID 
                && x.Result
                && x.TweetMode == GetTweetMode(TweetProcType))
                .ToList();
            */

            // accountMasterListからskipAccountIdListに含まれないアカウントを抽出
            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster().Where(x => x.Enable).ToList();
            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistoryView();

            DateTime now = DateTime.Now;
            List<string> 無料制限中アカウント = new List<string>();

            if(制限時間以内に履歴ありの無料アカウントを排除)
            {
                無料制限中アカウント = tweetHistoryList.Where(th => th.Paid == false && (now - th.UpdateTime).TotalMinutes <= 15 && th.Result).Select(x => x.AccountId).ToList();
            }

            List<string> ツイート済アカウント = new List<string>();

            if(LikeEnable)
            {
                ツイート済アカウント.AddRange(tweetHistoryList
                .Where(x => x.TargetTweetID == TargetTweetID
                && x.Result
                && x.TweetMode == GetTweetMode(TweetProcTypes.LIKE))
                .Select(x => x.AccountId)
                .ToList());
            }
            if (BookmarkEnable)
            {
                ツイート済アカウント.AddRange(tweetHistoryList
                .Where(x => x.TargetTweetID == TargetTweetID
                && x.Result
                && x.TweetMode == GetTweetMode(TweetProcTypes.BOOKMARK))
                .Select(x => x.AccountId)
                .ToList());
            }
            if (RetweetEnable)
            {
                ツイート済アカウント.AddRange(tweetHistoryList
                .Where(x => x.TargetTweetID == TargetTweetID
                && x.Result
                && x.TweetMode == GetTweetMode(TweetProcTypes.RETWEET))
                .Select(x => x.AccountId)
                .ToList());
            }

            // AccountMaster から条件に合う AccountId を除外
            var 除外対象アカウント = 無料制限中アカウント.Concat(ツイート済アカウント).Distinct().ToList();

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
                case TweetProcTypes.RETWEET:
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
            if (RetweetEnable)
            {
                TweetProc(TweetProcTypes.RETWEET, userId, accountId, commentId, tweetId);
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
                case TweetProcTypes.RETWEET:
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
