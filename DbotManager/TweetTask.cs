using DbotManager.Table;
using MySqlX.XDevAPI.Common;
using System;
using System.Collections;
using System.Collections.Generic;
using System.Diagnostics;
using System.IO;
using System.Linq;
using System.Text;
using System.Threading.Tasks;
using System.Windows.Forms;
using System.Timers;

using Newtonsoft.Json;
using System.Runtime.CompilerServices;

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
        NONE,
        CHECK,
        CHECKREP
    }

    public enum CheckAccountModes
    {
        監視,
        監視toReply,
        ものまね,
        NONE
    }

    public class TweetCommand
    {
        public TweetProcTypes TweetProcType { get; set; }
        public int? UserId { get; set; }
        public int? AccountId { get; set; }
        public int? AccountId2 { get; set; }
        public int? CommentId { get; set; }
        public string TweetId { get; set; }

        public int? CheckListId { get; set; }
        public string CheckAccountName { get; set; }
        public DateTime DateTime { get; set; }

        public MediaTypes MediaType { get; set; }
        public int? MediaId { get; set; }

        public bool DebugMode { get; set; }
    }

    public class TweetResult
    {
        public bool result { get; set; }
        public string contents { get; set; }
    }

    public class TweetTask
    {
        private readonly Action<string> logAction;

        private DbConnectionInfo dbConnectin;

        public TweetTask(DbConnectionInfo dbConnection , Action<string> logAction = null)
        {
            this.logAction = logAction;
            dbConnectin = dbConnection;

            CheckAccountList = new List<CheckAccountList>();
        }

        public int UserId { get; set; }

        public bool LikeEnable { get; set; }
        public bool BookmarkEnable { get; set; }
        public bool RepostEnable { get; set; }
        public bool ReplyEnable { get; set; }
        public bool DuplicateEnable { get; set; }

        public int 件数 { get; set; }
        public string TargetTweetID { get; set; }
        public bool 制限時間以内に履歴ありの無料アカウントを排除 { get; set; }

        public List<AccountMaster> LikeAccountList { get; set; }
        public List<AccountMaster> BookmarkAccountList { get; set; }
        public List<AccountMaster> RepostAccountList { get; set; }
        public List<AccountMaster> ReplyAccountList { get; set; }

        public List<CheckAccountList> CheckAccountList = new List<CheckAccountList>();


        List<CommentMaster> _replyCommentList = new List<CommentMaster>();
        List<CommentMaster> _replyToReplyCommentList = new List<CommentMaster>();


        public int いいね件数 { get; set; }
        public int ブックマーク件数 { get; set; }
        public int リポスト件数 { get; set; }
        public int リプライ件数 { get; set; }

        private static System.Timers.Timer _監視Timer;


        public event EventHandler<EventArgs> 監視完了;

        DateTime _監視list作成日時 = DateTime.Now;

        #region 一括処理

        public void Init一括処理list()
        {
            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);

            // accountMasterListからskipAccountIdListに含まれないアカウントを抽出
            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistoryView().Where(x => x.Result && x.Mode != TweetProcTypes.GET_ACCESSTOKEN && x.Mode != TweetProcTypes.GET_REFRESHTOKEN).ToList();
            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster();
            List<CommentMaster> commenttMasterList = dataAccess.GetCommentMaster();
            List<MediaMaster> mediaMasterList = dataAccess.GetMediaMaster();
            List<UserMaster> userMasterList = dataAccess.GetUserMaster();

            if (UserId != 0)
            {
                accountMasterList = accountMasterList.Where(x => x.UserId == UserId).ToList();
            }

            List<AccountMaster> likeList = FilterAccountList(userMasterList, accountMasterList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.LIKE);
            List<AccountMaster> replyList = FilterAccountList(userMasterList, accountMasterList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.REPLY);
            List<AccountMaster> bookMarkList = FilterAccountList(userMasterList, accountMasterList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.BOOKMARK);
            List<AccountMaster> repostList = FilterAccountList(userMasterList, accountMasterList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.REPOST);

            var selectedItems = SelectBalancedItems(likeList, replyList, bookMarkList, repostList, いいね件数, リプライ件数, ブックマーク件数, リポスト件数);

            LikeAccountList = selectedItems.Item1;
            ReplyAccountList = selectedItems.Item2;
            BookmarkAccountList = selectedItems.Item3;
            RepostAccountList = selectedItems.Item4;
        }


        public void Exe_一括処理()
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
                    TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.LIKE, UserId = likeItem.UserId, AccountId = likeItem.Id, TweetId = TargetTweetID });
                }

                // REPLY処理
                if (i < ReplyAccountList.Count)
                {
                    var replyItem = ReplyAccountList[i];
                    TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.REPLY, UserId = replyItem.UserId, AccountId = replyItem.Id, CommentId = replyItem.CommentId, TweetId = TargetTweetID });
                }

                // BOOKMARK処理
                if (i < BookmarkAccountList.Count)
                {
                    var bookmarkItem = BookmarkAccountList[i];
                    TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.BOOKMARK, UserId = bookmarkItem.UserId, AccountId = bookmarkItem.Id, TweetId = TargetTweetID });
                }

                // REPOST処理
                if (i < RepostAccountList.Count)
                {
                    var replyItem = RepostAccountList[i];
                    TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.REPOST, UserId = replyItem.UserId, AccountId = replyItem.Id, TweetId = TargetTweetID });
                }
            }
        }

        private (List<AccountMaster>, List<AccountMaster>, List<AccountMaster>, List<AccountMaster>) SelectBalancedItems(
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
                    List<AccountMaster> 除外list = new List<AccountMaster>();
                    除外list.AddRange(selectedLike);           // 自モードに追加済のアカウントを除外
                    除外list.AddRange(selectedReply);          // リプライといいねモードの共存は不可

                    var candidate = SelectRandomNonExcluded(likeList, 除外list, excludedIds, random);
                    if (candidate != null) // 候補が見つかれば追加
                    {
                        selectedLike.Add(candidate);
                        excludedIds.Add(candidate.Id); // Id を除外リストに追加
                    }
                }

                if (selectedReply.Count < replyCount)
                {
                    List<AccountMaster> 除外list = new List<AccountMaster>();
                    除外list.AddRange(selectedReply);         // 自モードに追加済のアカウントを除外
                    除外list.AddRange(selectedLike);          // リプライといいねモードの共存は不可
                    除外list.AddRange(selectedBookmark);      // リプライとブックマークモードの共存は不可

                    var candidate = SelectRandomNonExcluded(replyList, 除外list, excludedIds, random);
                    if (candidate != null) // 候補が見つかれば追加
                    {
                        selectedReply.Add(candidate);
                        excludedIds.Add(candidate.Id); // Id を除外リストに追加
                    }
                }

                if (selectedBookmark.Count < bookmarkCount)
                {
                    List<AccountMaster> 除外list = new List<AccountMaster>();
                    除外list.AddRange(selectedBookmark);           // 自モードに追加済のアカウントを除外
                    除外list.AddRange(selectedReply);          // リプライといいねモードの共存は不可

                    var candidate = SelectRandomNonExcluded(bookmarkList, 除外list, excludedIds, random);
                    if (candidate != null)
                    {
                        selectedBookmark.Add(candidate);
                        excludedIds.Add(candidate.Id);
                    }
                }

                if (selectedRepost.Count < repostCount)
                {
                    var candidate = SelectRandomNonExcluded(repostList, selectedRepost, excludedIds, random);
                    if (candidate != null)
                    {
                        selectedRepost.Add(candidate);
                        excludedIds.Add(candidate.Id);
                    }
                }
            }

            return (selectedLike, selectedReply, selectedBookmark, selectedRepost);
        }
        private AccountMaster SelectRandomNonExcluded(List<AccountMaster> source, List<AccountMaster> 除外list, HashSet<int> excludedIds, Random random)
        {
            // 除外list から除外する Id の集合を作成
            HashSet<int> 除外Ids = new HashSet<int>(除外list.Select(x => x.Id));
            var list = source.Where(x => !除外Ids.Contains(x.Id)).ToList();

            // Id が excludedIds に含まれない候補を取得
            List<AccountMaster> candidates;
            if (DuplicateEnable)
                candidates = list.ToList();
            else
                candidates = list.Where(x => !excludedIds.Contains(x.Id)).ToList();

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

        private List<AccountMaster> FilterAccountList(
            List<UserMaster> userMasterList,
            List<AccountMaster> accountMasterList,
            List<TweetHistory> tweetHistoryList,
            List<CommentMaster> commentMasterList,
            List<MediaMaster> mediaMasterList,
            TweetProcTypes tweetProcType)
        {
            List<AccountMaster> retList = new List<AccountMaster>();

            DateTime dateNow = DateTime.Now;

            foreach (var account in accountMasterList)
            {
                // 無効アカウントはスルー
                if (!account.Enable) continue;

                if (userMasterList.Where(x => x.Id == account.UserId).Count() != 1) continue;

                var userMasterRow = userMasterList.Where(x => x.Id == account.UserId).FirstOrDefault();

                if (userMasterRow.Enable == false) continue;
                if (tweetProcType == TweetProcTypes.LIKE && !userMasterRow.LikeEnable) continue;
                else if (tweetProcType == TweetProcTypes.BOOKMARK && !userMasterRow.BookmarkEnable) continue;
                else if (tweetProcType == TweetProcTypes.REPOST && !userMasterRow.RepostEnable) continue;
                else if (tweetProcType == TweetProcTypes.REPLY && !userMasterRow.ReplyEnable) continue;

                // 処理無効アカウントはスルー
                if (tweetProcType == TweetProcTypes.LIKE && !account.LikeEnable) continue;
                else if (tweetProcType == TweetProcTypes.BOOKMARK && !account.BookMarkEnable) continue;
                else if (tweetProcType == TweetProcTypes.REPOST && !account.RepostEnable) continue;
                else if (tweetProcType == TweetProcTypes.REPLY && !account.ReplyEnable) continue;

                var myHistory = tweetHistoryList.Where(x => x.AccountId == account.Id && x.Result == true).ToList();

                // 対象ツイートIDのモードで処理済みの場合はスルー
                if (myHistory.Where(x => x.TargetTweetID == TargetTweetID && x.Mode == tweetProcType).Count() > 0) continue;

                var lastMyHistoryList = myHistory.Where(x => x.AccountId == account.Id).OrderByDescending(x => x.UpdateTime).ToList();
                if (lastMyHistoryList.Count() > 0)
                {
#if false           // 最後と同じ処理に制限かけるのを保留
                    // 最期の処理が同じだった場合はスルー
                    if (lastMyHistoryList.FirstOrDefault().Mode == tweetProcType)
                    {
                        // 3時間以上時間が空いている場合は許可
                        if ((dateNow - lastMyHistoryList.FirstOrDefault().UpdateTime).TotalHours < 3)
                        {
                            continue;
                        }
                    }
#endif
                    // 無料アカウントは制限時間内の取引を中止
                    if (制限時間以内に履歴ありの無料アカウントを排除)
                    {
                        if (tweetProcType == TweetProcTypes.LIKE)
                        {
                            // 無料アカウント or 有料アカウントの無料いいね
                            if (!account.Paid || !account.PaidLike)
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

                if (tweetProcType == TweetProcTypes.REPLY)
                {
                    var commentMasterListWk = commentMasterList.Where(x => x.AccountId == account.Id && x.TweetModeType == TweetModeTypes.Replay).ToList();
                    if (commentMasterListWk.Count == 0) continue;

                    var commentItem = SupportUtil.GetRandomItem(commentMasterListWk.Where(x => x.AccountId == account.Id).ToList());
                    account.CommentId = commentItem.Id;

                    if (commentItem.PhotoEnable && userMasterRow.PhotoEnable)
                    {
                        var photoItem = SupportUtil.GetRandomItem(mediaMasterList.Where(x => x.CommentId == commentItem.Id && x.MediaType == MediaTypes.Photo).ToList());
                        account.PhotoId = photoItem.MediaId;
                    }
                    else
                    {
                        account.PhotoId = 0;
                    }

                    if (commentItem.MovieEnable && userMasterRow.MovieEnable)
                    {
                        var movieItem = SupportUtil.GetRandomItem(mediaMasterList.Where(x => x.CommentId == commentItem.Id && x.MediaType == MediaTypes.Movie).ToList());
                        account.MovieId = movieItem.MediaId;
                    }
                    else
                    {
                        account.MovieId = 0;
                    }
                }

                retList.Add(account);
            }

            return retList;
        }


        #endregion

        #region 監視処理

        public void Init監視list(bool first_flag = false)
        {
            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);

            List<UserMaster> userMasterList = dataAccess.GetUserMaster().Where(x => x.PostEnable && x.Enable).ToList();

            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster()
                .Where(x => x.PostEnable && x.Enable && userMasterList.Any(user => user.Id == x.UserId)).ToList();

            List<CheckAccountList> checkAccountList = dataAccess.GetCheckAccountList()
                .Where(x => x.Enable && accountMasterList.Any(y => y.Id == x.AccountId)).ToList();

            DateTime dtNow = DateTime.Now;
            CheckAccountList.Clear();

            foreach(var item in checkAccountList)
            {
                var account = accountMasterList.Where(x => x.Id == item.AccountId).FirstOrDefault();

                item.CheckInterval = item.Mode == TweetProcTypes.CHECK ? account.CheckInterval : item.Mode == TweetProcTypes.CHECKREP ? account.CheckRepInterval : account.MonomaneInterval;
                item.CheckDate = dtNow.AddSeconds(item.CheckInterval);
                item.TargetAccountName = item.TargetAccountName.Replace("@", "");

                if (item.CheckAccountId == 0) 
                    item.CheckAccountId = item.AccountId;

                var checkaccount = accountMasterList.Where(x => x.Id == item.CheckAccountId).FirstOrDefault();

                item.AccountName = account.Name;
                item.CheckAccountName = checkaccount.Name;

                if (first_flag) item.FirstFlag = true;

                CheckAccountList.Add(item);
            }

            _replyCommentList = dataAccess.GetCommentMaster().Where(x => x.TweetModeType == TweetModeTypes.Replay).ToList();
            _replyToReplyCommentList = dataAccess.GetCommentMaster().Where(x => x.TweetModeType == TweetModeTypes.ReplyToReply).ToList();

            _監視list作成日時 = DateTime.Now;
        }


        public void StartTask_監視()
        {
            Action callback = () =>
            {
                Console.WriteLine("監視タスクが完了しました。");
                // 必要ならここで追加処理を実行
                On監視完了();
            };

            // タイマーを設定（1000msごと = 1秒ごと）
            _監視Timer = new System.Timers.Timer(1000);
            _監視Timer.Elapsed += (sender, e) => OnTimedEvent_監視(sender, e, callback); //OnTimedEvent_監視(null,null, );
            _監視Timer.AutoReset = true; // 繰り返し実行
            _監視Timer.Enabled = true;
        }

        public void EndTask_監視()
        {
            _監視Timer.Enabled = false;
        }

        private void On監視完了()
        {
            Console.WriteLine("監視処理が完了しました。追加処理を行います。");

            監視完了?.Invoke(this, EventArgs.Empty);
            // ここで追加処理を行う
        }

        public void OnTimedEvent_監視(object sender, ElapsedEventArgs e, Action callback)
        {
//            _監視Timer.Enabled = false;
            Console.WriteLine($"処理を実行中: {DateTime.Now}");

            if(_監視list作成日時.AddHours(1) <= DateTime.Now)
            {
                Init監視list(false);
            }

            bool renewFlag = false;

            var list = new List<CheckAccountList>();
            list.AddRange(CheckAccountList);

            DateTime dtNow = DateTime.Now;

            foreach (var item in list)
            {
                // チェック時間に達していない場合はスルー
                if (item.CheckDate >= dtNow) continue;

                var tweetResult = TweetProc(new TweetCommand() { 
                    TweetProcType = item.Mode,// TweetProcTypes.CHECK, 
                    AccountId = item.CheckAccountId, 
                    CheckAccountName = item.TargetAccountName, 
                    CheckListId = item.Id,
                    TweetId = item.SinceTweetId 
                });

                item.CheckDate = dtNow.AddSeconds(item.CheckInterval);

                if(item.FirstFlag == false)
                {
                    if (tweetResult != null && tweetResult.result == true)
                    {
                        TweetProcReply(item, tweetResult);
                    }
                }

                item.FirstFlag = false;

                renewFlag = true;
            }

            if(renewFlag)
            {
                // コールバックを呼び出し(Formのdatagridview更新のため)
                callback?.Invoke();
            }
        }


        #endregion

        #region TweetProc関連

        public void TweetProcReply(CheckAccountList checkAccountList, TweetResult result)
        {
            //            int accountId = SupportUtil.GetRandomItem(checkAccountList.ExeAccountIdList);
            int accountId = checkAccountList.AccountId;

            if (_replyCommentList.Where(x => x.AccountId == accountId).Count() == 0) return;
            var commentId = SupportUtil.GetRandomItem(_replyCommentList.Where(x => x.AccountId == accountId).ToList()).Id;
            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.REPLY, AccountId = accountId, CommentId = commentId, TweetId = result.contents });
        }

        public void TweetProcReplyToReply(CheckAccountList checkAccountList, TweetResult result)
        {
            //            int accountId = SupportUtil.GetRandomItem(checkAccountList.ExeAccountIdList);
            int accountId = checkAccountList.AccountId;

            if (_replyToReplyCommentList.Where(x => x.AccountId == accountId).Count() == 0) return;
            var commentId = SupportUtil.GetRandomItem(_replyToReplyCommentList.Where(x => x.AccountId == accountId).ToList()).Id;
            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.REPLY, AccountId = accountId, CommentId = commentId, TweetId = result.contents });
        }

        private string GetNameList(List<AccountMaster> accountMasterList, List<int> list)
        {
            string ret = string.Empty;

            foreach (var item in list)
            {
                ret += accountMasterList.Where(x => x.Id == item).FirstOrDefault().Name + ",";
            }

            return ret;
        }


        private string GetTweetMode(TweetProcTypes type)
        {
            switch (type)
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
                case TweetProcTypes.CHECK:
                    return "check";
                    break;
                case TweetProcTypes.CHECKREP:
                    return "checkrep";
                    break;
            }
            return string.Empty;
        }

        //        public void TweetProc(TweetProcTypes tweetProcType, int userId, int accountId, int commentId, string tweetId)
        public TweetResult TweetProc(TweetCommand tweetCommand)
        {
            // Pythonスクリプトのパスを指定
            string pythonScriptPath = @"python\tweet.py";

            switch (tweetCommand.TweetProcType)
            {
                case TweetProcTypes.POST:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} comment_id={tweetCommand.CommentId}";

                    if(tweetCommand.MediaType != MediaTypes.None)
                    {
                        pythonScriptPath += $" media_type={(tweetCommand.MediaType == MediaTypes.Photo ? "photo" : "video")} media_id={tweetCommand.MediaId}";
                    }

                    break;

                case TweetProcTypes.LIKE:
                case TweetProcTypes.BOOKMARK:
                case TweetProcTypes.REPOST:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} tweet_id={tweetCommand.TweetId}";
                    break;

                case TweetProcTypes.REPLY:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} comment_id={tweetCommand.CommentId} tweet_id={tweetCommand.TweetId}";
                    break;

                case TweetProcTypes.GET_ACCESSTOKEN:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId}";
                    break;
                case TweetProcTypes.GET_REFRESHTOKEN:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId}";
                    break;

                case TweetProcTypes.CHECK:
                case TweetProcTypes.CHECKREP:
                case TweetProcTypes.MONOMANE:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} check_account_name={tweetCommand.CheckAccountName.Replace("@","")} check_list_id={tweetCommand.CheckListId}";
                    /*
                    if (tweetCommand.DebugMode)
                        pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)}_debug account_id={tweetCommand.CheckAccountName} check_list_id={tweetCommand.CheckListId}";
                    else
                        pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} account_id2={tweetCommand.AccountId2} check_account_name={tweetCommand.CheckAccountName} tweet_id={(tweetCommand.TweetId == null ? "" : tweetCommand.TweetId)}";
                    */

                    //                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} check_list_id={tweetCommand.CheckListId}";
                    break;
            }

            pythonScriptPath += " debug=False";

            // Pythonの実行ファイルのパスを指定（通常 "python" または "python3" でOK）
            string pythonExePath = "python";

            var process = new Process
            {
                StartInfo = new ProcessStartInfo
                {
                    FileName = pythonExePath,
                    Arguments = pythonScriptPath,
                    RedirectStandardOutput = true,
                    RedirectStandardError = true,
                    UseShellExecute = false,
                    CreateNoWindow = true

                }
            };
            // 環境変数を設定
//            StartInfo.EnvironmentVariables["RUNNING_FROM_CSHARP"] = "1";

            logAction?.Invoke($"{DateTime.Now.ToString()} > {pythonScriptPath}");

            TweetResult tweetResult = null;

            try
            {
                process.Start();
                string output = process.StandardOutput.ReadToEnd(); // Pythonスクリプトの標準出力
                string debugMessage = process.StandardError.ReadToEnd();   // Pythonスクリプトの標準エラー
                process.WaitForExit();

                /*
                if (!string.IsNullOrEmpty(debugMessage))
                {
                    Console.WriteLine($"Error: {debugMessage}");
                    return;
                }
                */

                // PythonスクリプトからのJSON結果をデシリアライズ
                //                var result = JsonSerializer.Deserialize<PythonResult>(output);

                // PythonスクリプトからのJSON結果をデシリアライズ (Newtonsoft.Json)
                tweetResult = JsonConvert.DeserializeObject<TweetResult>(output);

                if (tweetResult != null)
                {
                    Console.WriteLine($"{DateTime.Now.ToString()} < [{tweetResult.result}]{tweetResult.contents}");

                    logAction?.Invoke($"{DateTime.Now.ToString()} < [{tweetResult.result}]{tweetResult.contents}");
                }
                else
                {
                    Console.WriteLine("Python script returned invalid output.");
                    logAction?.Invoke($"{DateTime.Now.ToString()} TweetProc Python script returned invalid output.");
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Exception: {ex.Message}");
                logAction?.Invoke($"{DateTime.Now.ToString()} TweetProc Exception: {ex.Message}");
            }

            return tweetResult;

            /*
            switch (tweetCommand.TweetProcType)
            {
                case TweetProcTypes.POST:
                case TweetProcTypes.LIKE:
                case TweetProcTypes.BOOKMARK:
                case TweetProcTypes.REPOST:
                case TweetProcTypes.REPLY:
                case TweetProcTypes.GET_ACCESSTOKEN:
                case TweetProcTypes.GET_REFRESHTOKEN:
                    break;

                case TweetProcTypes.CHECK:
                case TweetProcTypes.CHECKREP:
                case TweetProcTypes.MONOMANE:
                    return tweetResult;
                    break;
            }

            return null;
            */


            /*
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


            // pythonの実行結果を受けて次動作を行うモードの実装
            {

            }
            */

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

        #endregion

    }
}
