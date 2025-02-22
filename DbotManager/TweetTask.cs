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
using System.Net.Http;


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

        public int? SearchId { get; set; }
        public string CheckAccountName { get; set; }
        public DateTime DateTime { get; set; }

        public MediaTypes MediaType { get; set; }
        public int? MediaId { get; set; }

        public bool DebugMode { get; set; }
    }

    public class TweetVpsCommand
    {
        public string VpsIp { get; set; }
        public string VpsPort { get; set; }
        public string TweetId { get; set; }
        public List<int> LikeList { get; set; }
        public List<int> BookmarkList { get; set; }
        public List<int> RepostList { get; set; }
        public List<int> ReplyList { get; set; }
    }

    public class TweetResult
    {
        public bool result1 { get; set; }
        public string contents1 { get; set; }
        public bool result2 { get; set; }
        public string contents2 { get; set; }
    }

    public class TweetTask
    {
        private readonly Action<string> logAction;

        private DbConnectionInfo dbConnectin;

        public TweetTask(DbConnectionInfo dbConnection , Action<string> logAction = null)
        {
            this.logAction = logAction;
            dbConnectin = dbConnection;

            CheckSearchList = new List<SearchList>();
        }

        public int UserId { get; set; }
        public int CheckUserId { get; set; }

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

        public List<SearchList> CheckSearchList = new List<SearchList>();


        List<CommentMaster> _replyCommentList = new List<CommentMaster>();
        List<CommentMaster> _replyToReplyCommentList = new List<CommentMaster>();

        List<SearchHistory> _searchHistoryList = new List<SearchHistory>();

        public int いいね件数 { get; set; }
        public int ブックマーク件数 { get; set; }
        public int リポスト件数 { get; set; }
        public int リプライ件数 { get; set; }

        private static System.Timers.Timer _監視Timer;


        public event EventHandler<EventArgs> 監視完了;

        DateTime _監視list作成日時 = DateTime.Now;

        private string pythonWorkingPath;

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
            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);
            List<VpsMaster> vpsMasterList = dataAccess.GetVpsMaster();

            /*
            foreach(var row in LikeAccountList)
            {
                row.VpsId = 0;
            }
            foreach (var row in ReplyAccountList)
            {
                row.VpsId = 0;
            }
            foreach (var row in BookmarkAccountList)
            {
                row.VpsId = 0;
            }
            foreach (var row in RepostAccountList)
            {
                row.VpsId = 0;
            }
            */

            foreach (var vps in vpsMasterList)
            {
                if (vps.Id == 0) continue;

                var likeList = LikeAccountList.Where(x => x.VpsId == vps.Id).ToList();
                var bookmarkList = BookmarkAccountList.Where(x => x.VpsId == vps.Id).ToList();
                var repostList = RepostAccountList.Where(x => x.VpsId == vps.Id).ToList();
                var replyList = ReplyAccountList.Where(x => x.VpsId == vps.Id).ToList();

                if (likeList.Count == 0 && bookmarkList.Count == 0 && repostList.Count == 0 && repostList.Count == 0) continue;

                TweetVpsCommand tweetVpsCommand = new TweetVpsCommand()
                {
                    VpsIp = vps.IpAddress,
                    VpsPort = vps.Port,
                    LikeList = likeList.Select(x => x.Id).ToList(),
                    BookmarkList = bookmarkList.Select(x => x.Id).ToList(),
                    RepostList = repostList.Select(x => x.Id).ToList(),
                    ReplyList = replyList.Select(x => x.Id).ToList(),
                    TweetId = TargetTweetID
                };

                TweetVpsProc(tweetVpsCommand);

            }

            {
                var likeList = LikeAccountList.Where(x => x.VpsId == 0).ToList();
                var bookmarkList = BookmarkAccountList.Where(x => x.VpsId == 0).ToList();
                var repostList = RepostAccountList.Where(x => x.VpsId == 0).ToList();
                var replyList = ReplyAccountList.Where(x => x.VpsId == 0).ToList();

                int maxLength = Math.Max(replyList.Count,
                                Math.Max(likeList.Count,
                                 Math.Max(bookmarkList.Count, repostList.Count)));

                for (int i = 0; i < maxLength; i++)
                {
                    // LIKE処理
                    if (i < likeList.Count)
                    {
                        var likeItem = likeList[i];
                        TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.LIKE, UserId = likeItem.UserId, AccountId = likeItem.Id, TweetId = TargetTweetID });
                    }

                    // REPLY処理
                    if (i < replyList.Count)
                    {
                        var replyItem = replyList[i];
                        TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.REPLY, UserId = replyItem.UserId, AccountId = replyItem.Id, CommentId = replyItem.CommentId, TweetId = TargetTweetID });
                    }

                    // BOOKMARK処理
                    if (i < bookmarkList.Count)
                    {
                        var bookmarkItem = bookmarkList[i];
                        TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.BOOKMARK, UserId = bookmarkItem.UserId, AccountId = bookmarkItem.Id, TweetId = TargetTweetID });
                    }

                    // REPOST処理
                    if (i < repostList.Count)
                    {
                        var replyItem = repostList[i];
                        TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.REPOST, UserId = replyItem.UserId, AccountId = replyItem.Id, TweetId = TargetTweetID });
                    }
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
                                    if ((dateNow - (DateTime)lastHistory.FirstOrDefault().UpdateTime).TotalDays < 1) continue;
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
                                    if ((dateNow - (DateTime)lastHistory.FirstOrDefault().UpdateTime).TotalMinutes < 15) continue;
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
                    account.CommentId = commentItem == null ? 0 : commentItem.Id;

                    account.PhotoId = 0;

                    if (commentItem.PhotoEnable && userMasterRow.MediaEnable)
                    {
                        var photoItem = SupportUtil.GetRandomItem(mediaMasterList.Where(x => x.CommentId == commentItem.Id && x.MediaType == MediaTypes.Photo).ToList());
                        if(photoItem != null)
                            account.PhotoId = photoItem.MediaId;
                    }

                    account.MovieId = 0;
                    if (commentItem.MovieEnable && userMasterRow.MediaEnable)
                    {
                        var movieItem = SupportUtil.GetRandomItem(mediaMasterList.Where(x => x.CommentId == commentItem.Id && x.MediaType == MediaTypes.Movie).ToList());

                        if(movieItem != null)
                            account.MovieId = movieItem.MediaId;
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

            List<UserMaster> userMasterList = dataAccess.GetUserMaster().Where(x => x.Enable && x.CheckEnable).ToList();

            if(CheckUserId != 0) userMasterList = userMasterList.Where(x => x.Id == CheckUserId).ToList();

            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster()
                .Where(x => x.Enable && (bool)x.SearchEnable && userMasterList.Any(user => user.Id == x.UserId)).ToList();

            // 監視、監視toRep、モノマネアカウントリストの取得

            //            List <SearchList> searchList = dataAccess.GetSearchList()
            //                .Where(x => (bool)x.Enable && accountMasterList.Any(y => y.Id == x.PostAccountId)).ToList();

            List<SearchList> wk1 = dataAccess.GetSearchList().Where(x => (bool)x.Enable).ToList();
            List<SearchList> wk2 = wk1.Where(x => userMasterList.Any(user => user.Id == x.SearchUserId)).ToList();
            List<SearchList> searchList = wk2.Where(x => accountMasterList.Any(y => (bool)y.Enable)).ToList();

            //            List<SearchList> searchList = dataAccess.GetSearchList().Where(x => (bool)x.Enable && accountMasterList.Any(y => (bool)y.Enable && (bool)y.SearchEnable )).ToList();

            InitSearchHistory(accountMasterList);

            DateTime dtNow = DateTime.Now;
            CheckSearchList.Clear();

            foreach(var item in searchList)
            {
                // 60秒周期にチェック
                item.CheckInterval = 60;
                item.CheckDate = dtNow.AddSeconds(item.CheckInterval);
                if (first_flag) item.FirstFlag = true;
                CheckSearchList.Add(item);
            }

            _replyCommentList = dataAccess.GetCommentMaster().Where(x => x.TweetModeType == TweetModeTypes.Replay).ToList();
            _replyToReplyCommentList = dataAccess.GetCommentMaster().Where(x => x.TweetModeType == TweetModeTypes.ReplyToReply).ToList();

            _監視list作成日時 = DateTime.Now;
        }

        public void InitSearchHistory(List<AccountMaster> accountMasterList)
        {
            _searchHistoryList.Clear();

            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);

            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistoryView().Where(x => x.Mode == TweetProcTypes.CHECK).ToList();

            foreach (var row in accountMasterList.Where(x => x.SearchEnable == true))
            {
                var lastCheck = (tweetHistoryList.Where(x => x.AccountId == row.Id))?.OrderByDescending(x=>x.UpdateTime).FirstOrDefault();

                _searchHistoryList.Add(
                    new SearchHistory() { 
                        AccountId = row.Id ,
                        UserId = row.UserId ,
                        SearchDatetime = lastCheck == null ? DateTime.Now : lastCheck.UpdateTime ,

//                        Interval = (row.Paid ? 300 : 900)    //有料API=5分 無料API=60分
                        Interval = (row.CheckInterval < 5 ? 5 : row.CheckInterval) * 60   //アカウントで設定している検索周期を反映(最低5分)
                    });
            }

        }

        public void OrderSearchHistory()
        {
            // 並べ替え処理
            var now = DateTime.Now;
            _searchHistoryList = _searchHistoryList
                .OrderByDescending(sh =>
                {
                    if (sh.SearchDatetime == null)
                    {
                        return TimeSpan.MaxValue.TotalSeconds; // nullは一番大きい値として扱う
                    }

                    var targetTime = sh.SearchDatetime.Value.AddSeconds(sh.Interval);
                    return (now - targetTime).TotalSeconds;
                })
                .ToList();

            // 結果を表示
            foreach (var item in _searchHistoryList)
            {
                Console.WriteLine($"UserId: {item.UserId}, AccountId: {item.AccountId}, SearchDatetime: {item.SearchDatetime}, Interval: {item.Interval}");
            }

        }

        private SearchHistory GetSearchHistoryRow(SearchList item , DateTime dtNow)
        {
            // 利用者の履歴に絞る
            var userSearchHistoryList = _searchHistoryList.Where(x => x.UserId == item.SearchUserId).ToList();

            if (userSearchHistoryList.Count == 0) return null;

            // 監視インターバルが過ぎているもののみ絞り込み
            var timeSearchHistoryList = userSearchHistoryList.Where(x => ((DateTime)x.SearchDatetime).AddSeconds(x.Interval) < dtNow).ToList();

            if (timeSearchHistoryList.Count == 0) return null;

            return timeSearchHistoryList.FirstOrDefault();
        }

        private void RenewSearchDateTime(SearchHistory item)
        {
            foreach(var row in _searchHistoryList)
            {
                if(row.AccountId == item.AccountId)
                {
                    row.SearchDatetime = DateTime.Now.AddSeconds(row.Interval);
                }
            }
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
            _監視Timer = new System.Timers.Timer(10000);
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
            _監視Timer.Enabled = false;
            Console.WriteLine($"処理を実行中: {DateTime.Now}");

            if(_監視list作成日時.AddHours(1) <= DateTime.Now)
            {
                Init監視list(false);
            }

            bool renewFlag = false;

            DateTime dtNow = DateTime.Now;

            // 検索履歴を並べ替え
            OrderSearchHistory();

            foreach (var item in CheckSearchList)
            {
                // チェック時間に達していない場合はスルー
                if (item.CheckDate >= dtNow) continue;

                // 時間帯を絞っていて時間外の場合はスルー
                if((bool)item.TimeEnable)
                {
                    if (item.StartHour > dtNow.Hour) continue;
                    if (item.EndHour <= dtNow.Hour) continue;
                }

                var searchHistoryRow = GetSearchHistoryRow(item , dtNow);

                if (searchHistoryRow == null) continue;

                var tweetResult = TweetProc(new TweetCommand() { 
                    TweetProcType = TweetProcTypes.CHECK, 
                    SearchId = item.Id,
                    AccountId = searchHistoryRow.AccountId
                });

                item.CheckDate = dtNow.AddSeconds(item.CheckInterval);
                RenewSearchDateTime(searchHistoryRow);

                if (item.FirstFlag == false)
                {
                    if (tweetResult != null && (bool)item.PostEnable && tweetResult.result1 == true)
                    {
                        TweetProcReply(item, tweetResult);
                    }

                    if (tweetResult != null && (bool)item.ReplyEnable && tweetResult.result2 == true)
                    {
                        TweetProcReplyToReply(item, tweetResult);
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

            _監視Timer.Enabled = true;

        }



        #endregion

        #region TweetProc関連

        public void TweetProcReply(SearchList searchList, TweetResult result)
        {
            //            int accountId = SupportUtil.GetRandomItem(checkAccountList.ExeAccountIdList);
            int accountId = searchList.PostAccountId;

            if (_replyCommentList.Where(x => x.AccountId == accountId).Count() == 0) return;

            var commentItem = SupportUtil.GetRandomItem(_replyCommentList.Where(x => x.AccountId == accountId).ToList());
            if (commentItem == null) return;
            var commentId = commentItem.Id;
            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.REPLY, AccountId = accountId, CommentId = commentId, TweetId = result.contents1 });
        }

        public void TweetProcReplyToReply(SearchList searchList, TweetResult result)
        {
            //            int accountId = SupportUtil.GetRandomItem(checkAccountList.ExeAccountIdList);
            int accountId = searchList.ReplyAccountId;

            if (_replyToReplyCommentList.Where(x => x.AccountId == accountId).Count() == 0) return;

            var commentItem = SupportUtil.GetRandomItem(_replyToReplyCommentList.Where(x => x.AccountId == accountId).ToList());
            if (commentItem == null) return;
            var commentId = commentItem.Id;

            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.REPLY, AccountId = accountId, CommentId = commentId, TweetId = result.contents2 });
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
            ReadIniファイル();

            // Pythonスクリプトのパスを指定
            string pythonScriptPath = $@"{pythonWorkingPath}\tweet.py";

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
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} search_id={tweetCommand.SearchId}";
//                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} check_account_name={tweetCommand.CheckAccountName.Replace("@","")} check_list_id={tweetCommand.SearchId}";
                    /*
                    if (tweetCommand.DebugMode)
                        pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)}_debug account_id={tweetCommand.CheckAccountName} check_list_id={tweetCommand.CheckListId}";
                    else
                        pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} account_id2={tweetCommand.AccountId2} check_account_name={tweetCommand.CheckAccountName} tweet_id={(tweetCommand.TweetId == null ? "" : tweetCommand.TweetId)}";
                    */

                    //                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} check_list_id={tweetCommand.CheckListId}";
                    break;
            }

//            pythonScriptPath += " debug=True";
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
                    CreateNoWindow = true,
                    WorkingDirectory = pythonWorkingPath

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

                // PythonスクリプトからのJSON結果をデシリアライズ (Newtonsoft.Json)
                tweetResult = JsonConvert.DeserializeObject<TweetResult>(output);

                if (tweetResult != null)
                {
                    Console.WriteLine($"{DateTime.Now.ToString()} < [{tweetResult.result1}]{tweetResult.contents1} [{tweetResult.result2}]{tweetResult.contents2}");

                    logAction?.Invoke($"{DateTime.Now.ToString()} < [{tweetResult.result1}]{tweetResult.contents1} [{tweetResult.result2}]{tweetResult.contents2}");
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
        }


        public async Task TweetVpsProc(TweetVpsCommand tweetVpsCommand)
        {
            var httpClient = new HttpClient();
            var url = $"http://{tweetVpsCommand.VpsIp}:{tweetVpsCommand.VpsPort}/run";

            // JSONデータを作成
            var requestData = new
            {
                tweet_id = tweetVpsCommand.TweetId ,
                like_list = string.Join(",", tweetVpsCommand.LikeList),
                bookmark_list = string.Join(",", tweetVpsCommand.BookmarkList),
                repost_list = string.Join(",", tweetVpsCommand.RepostList),
                reply_list = string.Join(",", tweetVpsCommand.ReplyList)
            };
            string json = JsonConvert.SerializeObject(requestData);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            try
            {
                // POSTリクエストを送信
                var response = await httpClient.PostAsync(url, content);
                var responseBody = await response.Content.ReadAsStringAsync();

                Console.WriteLine($"Response: {responseBody}");
            }
            catch (Exception ex)
            {
                Console.WriteLine($"Error: {ex.Message}");
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

        #endregion


        private void ReadIniファイル()
        {
            string filePath = "config_tweet.ini";

            // ファイルを読み込み
            if (File.Exists(filePath))
            {
                var lines = File.ReadAllLines(filePath);
                var settings = new Dictionary<string, Dictionary<string, string>>();
                string currentSection = "";

                foreach (var line in lines)
                {
                    if (line.StartsWith("[") && line.EndsWith("]"))
                    {
                        currentSection = line.Trim('[', ']');
                        if (!settings.ContainsKey(currentSection))
                        {
                            settings[currentSection] = new Dictionary<string, string>();
                        }
                    }
                    else if (!string.IsNullOrWhiteSpace(line) && line.Contains('='))
                    {
                        var keyValue = line.Split(new[] { '=' }, 2);
                        if (!string.IsNullOrEmpty(currentSection) && keyValue.Length == 2)
                        {
                            settings[currentSection][keyValue[0].Trim()] = keyValue[1].Trim();
                        }
                    }
                }

                // 設定を確認
                if (settings.ContainsKey("Tweet") && settings["Tweet"].ContainsKey("working"))
                {
                    pythonWorkingPath = settings["Tweet"]["working"];
                }
            }
        }

    }
}
