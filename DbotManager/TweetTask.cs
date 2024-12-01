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
        MONOMANE,
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
        public int UserId { get; set; }

        public bool LikeEnable { get; set; }
        public bool BookmarkEnable { get; set; }
        public bool RepostEnable { get; set; }
        public bool ReplyEnable { get; set; }

        public int 件数 { get; set; }
        public string TargetTweetID { get; set; }
        public bool 制限時間以内に履歴ありの無料アカウントを排除 { get; set; }

        public List<AccountMaster> LikeAccountList { get; set; }
        public List<AccountMaster> BookmarkAccountList { get; set; }
        public List<AccountMaster> RepostAccountList { get; set; }
        public List<AccountMaster> ReplyAccountList { get; set; }
        public int いいね件数 { get; set; }
        public int ブックマーク件数 { get; set; }
        public int リポスト件数 { get; set; }
        public int リプライ件数 { get; set; }

        public void StartTask()
        {
            int maxLength = Math.Max(ReplyAccountList.Count,
                            Math.Max(LikeAccountList.Count,
                             Math.Max(BookmarkAccountList.Count, RepostAccountList.Count)));

            for (int i = 0; i < maxLength; i++)
            {
                // LIKE処理
                if (i < LikeAccountList.Count)
                {
                    var likeItem = LikeAccountList[i];
                    TweetProc(TweetProcTypes.LIKE, likeItem.UserId, likeItem.Id, 1, TargetTweetID);
                }

                // REPLY処理
                if (i < ReplyAccountList.Count)
                {
                    var replyItem = ReplyAccountList[i];
                    TweetProc(TweetProcTypes.REPLY, replyItem.UserId, replyItem.Id, replyItem.CommentId, TargetTweetID);
                }

                // BOOKMARK処理
                if (i < BookmarkAccountList.Count)
                {
                    var bookmarkItem = BookmarkAccountList[i];
                    TweetProc(TweetProcTypes.BOOKMARK, bookmarkItem.UserId, bookmarkItem.Id, 1, TargetTweetID);
                }

                // REPOST処理
                if (i < RepostAccountList.Count)
                {
                    var replyItem = RepostAccountList[i];
                    TweetProc(TweetProcTypes.REPOST, replyItem.UserId, replyItem.Id, 1, TargetTweetID);
                }
            }
        }


        public void InitAccountList()
        {
            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);

            // accountMasterListからskipAccountIdListに含まれないアカウントを抽出
            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistoryView().Where(x => x.Result && x.Mode != TweetProcTypes.GET_ACCESSTOKEN && x.Mode == TweetProcTypes.GET_REFRESHTOKEN).ToList();
            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster();
            List<CommentMaster> commenttMasterList = dataAccess.GetCommentMaster();

            if(UserId != 0)
            {
                accountMasterList = accountMasterList.Where(x => x.UserId == UserId).ToList();
            }

            List<AccountMaster> likeList = FilterAccountList(accountMasterList , tweetHistoryList , commenttMasterList, TweetProcTypes.LIKE);
            List<AccountMaster> replyList = FilterAccountList(accountMasterList, tweetHistoryList, commenttMasterList,TweetProcTypes.REPLY);
            List<AccountMaster> bookMarkList = FilterAccountList(accountMasterList, tweetHistoryList, commenttMasterList,TweetProcTypes.BOOKMARK);
            List<AccountMaster> repostList = FilterAccountList(accountMasterList, tweetHistoryList, commenttMasterList,TweetProcTypes.REPOST);

            var selectedItems = SelectBalancedItems(likeList, replyList , bookMarkList, repostList, いいね件数, リプライ件数 , ブックマーク件数, リポスト件数);

            LikeAccountList = selectedItems.Item1;
            ReplyAccountList = selectedItems.Item2;
            BookmarkAccountList = selectedItems.Item3;
            RepostAccountList = selectedItems.Item4;
        }

        static (List<AccountMaster>, List<AccountMaster>, List<AccountMaster>, List<AccountMaster>) SelectBalancedItems(
            List<AccountMaster> likeList,
            List<AccountMaster> replyList,
            List<AccountMaster> bookmarkList,
            List<AccountMaster> repostList,
            int likeCount,
            int replyCount,
            int bookmarkCount,
            int repostCount)
        {
            var selectedLike = new List<AccountMaster>();
            var selectedReply = new List<AccountMaster>();
            var selectedBookmark = new List<AccountMaster>();
            var selectedRepost = new List<AccountMaster>();

            var excludedIds = new HashSet<int>(); // 除外対象の Id を追跡
            var random = new Random();

            // 最大回数ループ（test1, test2, test3 の中で最も多く選ぶ件数）
            int maxCount = Math.Max(likeCount, Math.Max(replyCount, Math.Max(bookmarkCount, repostCount)));

            for (int i = 0; i < maxCount; i++)
            {
                if (selectedLike.Count < likeCount)
                {
                    var candidate = SelectRandomNonExcluded(likeList, excludedIds, random);
                    if (candidate != null) // 候補が見つかれば追加
                    {
                        selectedLike.Add(candidate);
                        excludedIds.Add(candidate.Id); // Id を除外リストに追加
                    }
                }

                if (selectedReply.Count < replyCount)
                {
                    var candidate = SelectRandomNonExcluded(replyList, excludedIds, random);
                    if (candidate != null) // 候補が見つかれば追加
                    {
                        selectedReply.Add(candidate);
                        excludedIds.Add(candidate.Id); // Id を除外リストに追加
                    }
                }

                if (selectedBookmark.Count < bookmarkCount)
                {
                    var candidate = SelectRandomNonExcluded(bookmarkList, excludedIds, random);
                    if (candidate != null)
                    {
                        selectedBookmark.Add(candidate);
                        excludedIds.Add(candidate.Id);
                    }
                }

                if (selectedRepost.Count < repostCount)
                {
                    var candidate = SelectRandomNonExcluded(repostList, excludedIds, random);
                    if (candidate != null)
                    {
                        selectedRepost.Add(candidate);
                        excludedIds.Add(candidate.Id);
                    }
                }
            }

            return (selectedLike, selectedReply , selectedBookmark, selectedRepost);
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

        private List<AccountMaster> FilterAccountList(List<AccountMaster> accountMasterList, List<TweetHistory> tweetHistoryList, List<CommentMaster> commentMasterList , TweetProcTypes tweetProcType)
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
                else if (tweetProcType == TweetProcTypes.REPLY && !account.ReplyEnable) continue;

                var myHistory = tweetHistoryList.Where(x => x.AccountId == account.Id && x.Result == true).ToList();

                // 対象ツイートIDで処理済みの場合はスルー
                if (myHistory.Where(x => x.TargetTweetID == TargetTweetID).Count() > 0) continue;

                var lastMyHistoryList = myHistory.OrderByDescending(x => x.UpdateTime).ToList();
                if (lastMyHistoryList.Count() > 0)
                {
                    // 最期の処理が同じだった場合はスルー
                    if (lastMyHistoryList.FirstOrDefault().Mode == tweetProcType)
                    {
                        // 3時間以上時間が空いている場合は許可
                        if ((dateNow - lastMyHistoryList.FirstOrDefault().UpdateTime).TotalHours < 3)
                        {
                            continue;
                        }
                    }

                    // 無料アカウントは制限時間内の取引を中止
                    if (制限時間以内に履歴ありの無料アカウントを排除)
                    {
                        if (tweetProcType == TweetProcTypes.LIKE)
                        {
                            // 無料アカウント or 有料アカウントの無料いいね
                            if(!account.Paid || !account.PaidLike)
                            {
                                var lastHistory = lastMyHistoryList.Where(x => x.Mode == TweetProcTypes.LIKE).ToList();
                                if (lastHistory.Count > 0)
                                {
                                    if ((dateNow - lastHistory.FirstOrDefault().UpdateTime).TotalDays < 1) continue;
                                }
                            }
                        }
                        else if (tweetProcType == TweetProcTypes.BOOKMARK || tweetProcType == TweetProcTypes.REPOST || tweetProcType == TweetProcTypes.REPLY)
                        {
                            // 無料アカウント or 有料アカウントの無料ブックマーク
                            if (!account.Paid || !account.PaidBookmark)
                            {
                                var lastHistory = lastMyHistoryList.Where(x => x.Mode == tweetProcType).ToList();
                                if (lastHistory.Count > 0)
                                {
                                    if ((dateNow - lastHistory.FirstOrDefault().UpdateTime).TotalMinutes < 15) continue;
                                }
                            }
                        }
                    }

                }

                if(tweetProcType == TweetProcTypes.REPLY)
                {
                    var commentMasterListWk = commentMasterList.Where(x => x.AccountId == account.Id && x.TweetModeType == TweetModeTypes.Replay).ToList();
                    if (commentMasterListWk.Count == 0) continue;
                    account.CommentId = SupportUtil.GetRandomItem(commentMasterListWk).Id;
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
                case TweetProcTypes.REPLY:
                    return "reply";
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
                case TweetProcTypes.MONOMANE:
                    return "monomane";
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
                case TweetProcTypes.MONOMANE:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId} tweet_id={tweetId}";
                    break;

                case TweetProcTypes.REPLY:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId} comment_id={commentId} tweet_id={tweetId}";
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
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId} comment_id={commentId}";
                    break;
                case TweetProcTypes.LIKE:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId} tweet_id={tweetId}";
                    break;
                case TweetProcTypes.BOOKMARK:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId} tweet_id={tweetId}";
                    break;
                case TweetProcTypes.GET_ACCESSTOKEN:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId}";
                    break;
                case TweetProcTypes.GET_REFRESHTOKEN:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId}";
                    break;
            }

            return pythonScriptPath;

        }


    }
}
