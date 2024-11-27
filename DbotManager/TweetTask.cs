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
        REPOST,
        POST,
        REPLY,
        GET_ACCESSTOKEN,
        GET_REFRESHTOKEN,
        NONE
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

        public List<AccountMaster> LikeAccountList { get; set; }
        public List<AccountMaster> BookmarkAccountList { get; set; }
        public List<AccountMaster> ReplyAccountList { get; set; }
        public int いいね件数 { get; set; }
        public int ブックマーク件数 { get; set; }
        public int リプライ件数 { get; set; }

        public void StartTask()
        {
            int maxLength = Math.Max(LikeAccountList.Count,
                             Math.Max(BookmarkAccountList.Count, ReplyAccountList.Count));

            for (int i = 0; i < maxLength; i++)
            {
                // LIKE処理
                if (i < LikeAccountList.Count)
                {
                    var likeItem = LikeAccountList[i];
                    TweetProc(TweetProcTypes.LIKE, likeItem.UserId, likeItem.Id, 1, TargetTweetID);
                }

                // BOOKMARK処理
                if (i < BookmarkAccountList.Count)
                {
                    var bookmarkItem = BookmarkAccountList[i];
                    TweetProc(TweetProcTypes.BOOKMARK, bookmarkItem.UserId, bookmarkItem.Id, 1, TargetTweetID);
                }

                // REPOST処理
                if (i < ReplyAccountList.Count)
                {
                    var replyItem = ReplyAccountList[i];
                    TweetProc(TweetProcTypes.REPOST, replyItem.UserId, replyItem.Id, 1, TargetTweetID);
                }
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
            List<AccountMaster> replyList = FilterAccountList(accountMasterList, tweetHistoryList, TweetProcTypes.REPOST);

            var selectedItems = SelectBalancedItems(likeList, bookMarkList, replyList, いいね件数, ブックマーク件数, リプライ件数);

            LikeAccountList = selectedItems.Item1;
            BookmarkAccountList = selectedItems.Item2;
            ReplyAccountList = selectedItems.Item3;
        }

        static (List<AccountMaster>, List<AccountMaster>, List<AccountMaster>) SelectBalancedItems(
            List<AccountMaster> test1,
            List<AccountMaster> test2,
            List<AccountMaster> test3,
            int count1,
            int count2,
            int count3)
        {
            var selected1 = new List<AccountMaster>();
            var selected2 = new List<AccountMaster>();
            var selected3 = new List<AccountMaster>();

            var excludedIds = new HashSet<int>(); // 除外対象の Id を追跡
            var random = new Random();

            // 最大回数ループ（test1, test2, test3 の中で最も多く選ぶ件数）
            int maxCount = Math.Max(count1, Math.Max(count2, count3));

            for (int i = 0; i < maxCount; i++)
            {
                if (selected1.Count < count1)
                {
                    var candidate = SelectRandomNonExcluded(test1, excludedIds, random);
                    if (candidate != null) // 候補が見つかれば追加
                    {
                        selected1.Add(candidate);
                        excludedIds.Add(candidate.Id); // Id を除外リストに追加
                    }
                }

                if (selected2.Count < count2)
                {
                    var candidate = SelectRandomNonExcluded(test2, excludedIds, random);
                    if (candidate != null)
                    {
                        selected2.Add(candidate);
                        excludedIds.Add(candidate.Id);
                    }
                }

                if (selected3.Count < count3)
                {
                    var candidate = SelectRandomNonExcluded(test3, excludedIds, random);
                    if (candidate != null)
                    {
                        selected3.Add(candidate);
                        excludedIds.Add(candidate.Id);
                    }
                }
            }

            return (selected1, selected2, selected3);
        }
        static AccountMaster SelectRandomNonExcluded(List<AccountMaster> source, HashSet<int> excludedIds, Random random)
        {
            // Id が excludedIds に含まれない候補を取得
            var candidates = source.Where(x => !excludedIds.Contains(x.Id)).ToList();

            if (candidates.Count == 0)
                return null; // 候補が無ければ null を返す

            // ランダムに選択して返す
            return candidates[random.Next(candidates.Count)];
        }

        static List<int> SelectFixedCountFromList(List<int> source, HashSet<int> excluded, int count)
        {
            Random random = new Random();
            // 除外された要素を取り除いたリストを作成
            var filteredSource = source.Where(x => !excluded.Contains(x)).ToList();

            if (filteredSource.Count < count)
            {
                throw new InvalidOperationException("Not enough unique items to select the required count.");
            }

            // ランダムに要素を選ぶ
            var selected = filteredSource.OrderBy(x => random.Next()).Take(count).ToList();
            // 選択済みの要素を追跡
            excluded.UnionWith(selected);
            return selected;
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
                else if (tweetProcType == TweetProcTypes.REPOST && !account.RepostEnable) continue;

                var myHistory = tweetHistoryList.Where(x => x.AccountId == account.Id && x.Result == true).ToList();

                // 対象ツイートIDで処理済みの場合はスルー
                if (myHistory.Where(x => x.TargetTweetID == TargetTweetID).Count() > 0) continue;

                var lastMyHistoryList = myHistory.OrderByDescending(x => x.UpdateTime).ToList();
                if (lastMyHistoryList.Count() > 0)
                {
                    // 最期の処理が同じだった場合はスルー
                    if (lastMyHistoryList.FirstOrDefault().Mode == tweetProcType)
                    {
                        continue;
                    }

                    // 無料アカウントは制限時間内の取引を中止
                    if (制限時間以内に履歴ありの無料アカウントを排除 && account.Paid == false)
                    {
                        if (tweetProcType == TweetProcTypes.LIKE)
                        {
                            var lastHistory = lastMyHistoryList.Where(x => x.Mode == TweetProcTypes.LIKE).ToList();
                            if(lastHistory.Count > 0)
                            {
                                if ((dateNow - lastHistory.FirstOrDefault().UpdateTime).TotalDays < 1) continue;
                            }
                        }
                        else if (tweetProcType == TweetProcTypes.BOOKMARK || tweetProcType == TweetProcTypes.REPOST)
                        {
                            var lastHistory = lastMyHistoryList.Where(x => x.Mode == tweetProcType).ToList();
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
                case TweetProcTypes.REPOST:
                    return "repost";
                    break;
                case TweetProcTypes.POST:
                    return "post";
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

        public void TweetProc(TweetProcTypes tweetProcType, int userId, int accountId, int commentId, string tweetId)
        {


            // Pythonスクリプトのパスを指定
            string pythonScriptPath = @"python\tweet.py";

            switch (tweetProcType)
            {
                case TweetProcTypes.POST:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId} comment_id={commentId}";
                    break;
                case TweetProcTypes.LIKE:
                case TweetProcTypes.BOOKMARK:
                case TweetProcTypes.REPOST:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId} tweet_id={tweetId}";
                    break;
                case TweetProcTypes.GET_ACCESSTOKEN:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId}";
                    break;
                case TweetProcTypes.GET_REFRESHTOKEN:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId}";
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
                case TweetProcTypes.POST:
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
