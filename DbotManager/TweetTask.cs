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
        いいね,
        ブックマーク,
        リポスト,
        ポスト,
        リプライ,
        ｱｸｾｽﾄｰｸﾝ取得,
        ﾘﾌﾚｯｼｭﾄｰｸﾝ更新,
        モノマネ,
        NONE,
        ポスト監視,
        リプ監視,
        AIリプ監視,
        JAPいいね,
        JAPブックマーク,
        JAPリポスト,
        JAPプロフィール,
        JAP詳細,
        フォロー追加,
        フォロー解除,
        監視初期化
    }

    public enum TweetErrorTypes
    {
        未設定,
        ロック,
        凍結,
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
        public string TweetName { get; set; }
        public int Quantity { get; set; }
        public bool AiEnable { get; set; }
        public int AiMode { get; set; }

        public int? SearchId { get; set; }
        public string CheckAccountName { get; set; }
        public DateTime DateTime { get; set; }

        public MediaTypes MediaType { get; set; }
        public int? MediaId { get; set; }

        public bool DebugMode { get; set; }
        public bool CheckAiRepMode { get; set; }
    }

    public class ReplyEntry
    {
        public int AccountId { get; set; }
        public int CommentId { get; set; }
    }

    public class TweetVpsCommand
    {
        public string VpsIp { get; set; }
        public int VpsId { get; set; }
        public string VpsPort { get; set; }
        public string TweetId { get; set; }
        public int LikeCount { get; set; }
        public List<int> LikeList { get; set; }
        public int BookmarkCount { get; set; }
        public List<int> BookmarkList { get; set; }
        public List<int> RepostList { get; set; }
        public List<ReplyEntry> ReplyList { get; set; }
        public bool RepToRep { get; set; }   
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
        public bool ReplyToRep { get; set; }
        public bool DuplicateEnable { get; set; }

        public bool ExeFollow { get; set; }
        public bool ExeUnFollow { get; set; }
        public string TargetAccountName { get; set; }


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

        public void Init一括処理list(bool ユーザー権限無視 , bool commentRequire)
        {
            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);

            // accountMasterListからskipAccountIdListに含まれないアカウントを抽出
            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistoryView(1).Where(x => x.Result && x.Mode != TweetProcTypes.ｱｸｾｽﾄｰｸﾝ取得 && x.Mode != TweetProcTypes.ﾘﾌﾚｯｼｭﾄｰｸﾝ更新).ToList();
            List<CommentMaster> commenttMasterList = new List<CommentMaster>();
            List<MediaMaster> mediaMasterList = new List<MediaMaster>();

            if(commentRequire)
            {
                commenttMasterList = dataAccess.GetCommentMaster();
                mediaMasterList = dataAccess.GetMediaMaster();
            }

            List<UserMaster> userMasterList, userMasterList_リプ;
            List<AccountMaster> accountMasterList;

            // UserID=0(自ユーザー以外)で処理する場合は、選手権実行フラグがONのユーザーのみ有効
            if (UserId == 0)
            {
                userMasterList = dataAccess.GetUserMaster().Where(x => x.SensyukenExec).ToList();
                userMasterList_リプ = dataAccess.GetUserMaster().Where(x => x.SensyukenExecReply).ToList();
                accountMasterList = dataAccess.GetAccountMaster();
            }
            else
            {
                userMasterList = dataAccess.GetUserMaster();
                userMasterList_リプ = dataAccess.GetUserMaster();
//                accountMasterList = dataAccess.GetAccountMaster().Where(x => x.UserId == UserId).ToList();
                accountMasterList = dataAccess.GetAccountMaster().ToList();
            }

            // 2026.04.04 ロック解除&凍結解除&再連携済みのアカウントに絞る
            {
                accountMasterList = accountMasterList.Where(x => !x.IsLocked && !x.IsSuspended && !x.IsUnauthorized).ToList();
            }


#if false 
            // 「いいね」リスト抽出
            {
                List<AccountMaster> likeList = FilterAccountList(userMasterList, accountMasterList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.いいね, ユーザー権限無視);
                LikeAccountList = likeList.OrderBy(_ => Guid.NewGuid()).Take(いいね件数).ToList();
            }

            // 「ブックマーク」リスト抽出
            {
                // 2025.10.02 「いいね」「ブックマーク」アカウントは重複しないよう対応
                // 2025.10.18 指示があったため処理復活
                //                /*
                // 「いいね」許可したアカウントからブックマークリスト作成
                List<AccountMaster> list1 = FilterAccountList(userMasterList, LikeAccountList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.ブックマーク, ユーザー権限無視);
//                */

                /*
                // 「いいね」許可したアカウント以外からブックマークリスト作成
                var いいねを除外したlist = accountMasterList
                    .Where(a1 => !LikeAccountList.Any(a2 => a2.Id == a1.Id))
                    .ToList();
                List<AccountMaster> list1 = FilterAccountList(userMasterList, いいねを除外したlist, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.ブックマーク, ユーザー権限無視);
                */

                var bookmarkList1 = list1.OrderBy(_ => Guid.NewGuid()).Take(ブックマーク件数).ToList();

                // 「ブックマーク」で追加済を除外したアカウントリスト
                List<AccountMaster> filteredList = accountMasterList.Except(bookmarkList1).ToList();
                List<AccountMaster> list2 = FilterAccountList(userMasterList, filteredList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.ブックマーク, ユーザー権限無視);
                var 残り件数 = ブックマーク件数 - bookmarkList1.Count;
                var bookmarkList2 = list2.OrderBy(_ => Guid.NewGuid()).Take(残り件数).ToList();

                BookmarkAccountList = new List<AccountMaster>();
                BookmarkAccountList.AddRange(bookmarkList1);
                BookmarkAccountList.AddRange(bookmarkList2);
            }
#else     // リトライ処理対応の為、上限を絞る処理は割愛
            List<AccountMaster> likeList = FilterAccountList(userMasterList, accountMasterList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.いいね, ユーザー権限無視);
            LikeAccountList = likeList.OrderBy(_ => Guid.NewGuid()).ToList();

            List<AccountMaster> bookmarkList = FilterAccountList(userMasterList, accountMasterList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.ブックマーク, ユーザー権限無視);
            BookmarkAccountList = bookmarkList.OrderBy(_ => Guid.NewGuid()).ToList();
#endif

            List<AccountMaster> replyList = FilterAccountList(userMasterList_リプ, accountMasterList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.リプライ, ユーザー権限無視, ReplyToRep);
            List<AccountMaster> repostList = FilterAccountList(userMasterList, accountMasterList, tweetHistoryList, commenttMasterList, mediaMasterList, TweetProcTypes.リポスト, ユーザー権限無視);

            var selectedItems = SelectBalancedItems(LikeAccountList, replyList, BookmarkAccountList, repostList, いいね件数, リプライ件数, ブックマーク件数, リポスト件数);

            ReplyAccountList = selectedItems.Item2;
            RepostAccountList = selectedItems.Item4;
        }

        public void Exe_JAP(TweetProcTypes type, string tweet_name, string tweet_id, int quantity, int userId)
        {
            TweetProc(
                new TweetCommand()
                {
                    TweetProcType = type,
                    AccountId = 1,
                    TweetId = tweet_id,
                    TweetName = tweet_name,
                    Quantity = quantity,
                    UserId = userId
                });
        }

        public static List<List<T>> SplitByCount<T>(List<T> list, int groupCount)
        {
            int size = (int)Math.Ceiling((double)list.Count / groupCount);

            return list
                .Select((x, i) => new { Index = i, Value = x })
                .GroupBy(x => x.Index / size)
                .Select(g => g.Select(x => x.Value).ToList())
                .ToList();
        }

        public static List<int> SplitCounts(int totalCount, int groupCount)
        {
            var result = new List<int>();

            int baseCount = totalCount / groupCount;   // 基本配分
            int remainder = totalCount % groupCount;   // 余り

            for (int i = 0; i < groupCount; i++)
            {
                // 余りは先頭から1ずつ配る
                result.Add(baseCount + (i < remainder ? 1 : 0));
            }

            return result;
        }

        public void Exe_一括処理()
        {
            if (LikeAccountList == null) return;
            if (BookmarkAccountList == null) return;
            if (RepostAccountList == null) return;
            if (ReplyAccountList == null) return;

            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);
            List<VpsMaster> vpsMasterList = dataAccess.GetVpsMaster().Where(x => x.ChildEnable).ToList();

            List<List<AccountMaster>> likeAccountGpList = new List<List<AccountMaster>>();
            List<List<AccountMaster>> bookmarkAccountGpList = new List<List<AccountMaster>>();
            List<int> likeCountList = new List<int>();
            List<int> bookMarkCountList = new List<int>();

            // ユーザー指定されている場合
            if (UserId != 0)
            {
                vpsMasterList = vpsMasterList.Where(x => x.UserId == UserId).ToList();
                // VPSグルーピング数で分割
                likeAccountGpList = SplitByCount(LikeAccountList, vpsMasterList.Count());
                bookmarkAccountGpList = SplitByCount(LikeAccountList, vpsMasterList.Count());

                likeCountList = SplitCounts(いいね件数 , vpsMasterList.Count());
                bookMarkCountList = SplitCounts(ブックマーク件数, vpsMasterList.Count());
            }
            else
            {
                likeAccountGpList = SplitByCount(LikeAccountList, 1);
                bookmarkAccountGpList = SplitByCount(LikeAccountList, 1);
                likeCountList = SplitCounts(いいね件数, 1);
                bookMarkCountList = SplitCounts(ブックマーク件数, 1);
            }

            int gpNo = 0;

            foreach (var vps in vpsMasterList)
            {
                if (vps.Id == 0) continue;

//                var likeList = LikeAccountList.Where(x => x.VpsId == vps.Id).ToList();
//                var bookmarkList = BookmarkAccountList.Where(x => x.VpsId == vps.Id).ToList();
                var likeList = likeAccountGpList[gpNo];
                var bookmarkList = bookmarkAccountGpList[gpNo];


                var repostList = RepostAccountList.Where(x => x.VpsId == vps.Id).ToList();
                var replyList = ReplyAccountList.Where(x => x.VpsId == vps.Id).ToList();

                if (likeList.Count == 0 && bookmarkList.Count == 0 && repostList.Count == 0 && replyList.Count == 0) continue;

                TweetVpsCommand tweetVpsCommand = new TweetVpsCommand()
                {
                    VpsIp = vps.IpAddress,
                    VpsId = vps.Id,
                    VpsPort = vps.Port,

                    LikeList = likeList.Select(x => x.Id).ToList(),
                    LikeCount = likeCountList[gpNo],
                    BookmarkList = bookmarkList.Select(x => x.Id).ToList(),
                    BookmarkCount = bookMarkCountList[gpNo],

                    RepostList = repostList.Select(x => x.Id).ToList(),
                    ReplyList = replyList.Select(x => new ReplyEntry
                    {
                        AccountId = x.Id,
                        CommentId = (int)x.CommentId
                    }).ToList(),
                    TweetId = TargetTweetID,
                    RepToRep = ReplyToRep
                };

                TweetVpsProc(tweetVpsCommand);

                gpNo++;

            }

            // VPS_ID=0は使用禁止
            return;

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
                        TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.いいね, UserId = likeItem.UserId, AccountId = likeItem.Id, TweetId = TargetTweetID });
                    }

                    // REPLY処理
                    if (i < replyList.Count)
                    {
                        var replyItem = replyList[i];
                        TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.リプライ, UserId = replyItem.UserId, AccountId = replyItem.Id, CommentId = replyItem.CommentId, TweetId = TargetTweetID });
                    }

                    // BOOKMARK処理
                    if (i < bookmarkList.Count)
                    {
                        var bookmarkItem = bookmarkList[i];
                        TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.ブックマーク, UserId = bookmarkItem.UserId, AccountId = bookmarkItem.Id, TweetId = TargetTweetID });
                    }

                    // REPOST処理
                    if (i < repostList.Count)
                    {
                        var replyItem = repostList[i];
                        TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.リポスト, UserId = replyItem.UserId, AccountId = replyItem.Id, TweetId = TargetTweetID });
                    }
                }

            }

        }

        internal void ExeFollow処理(TweetProcessList tweetProcessList)
        {
            if (!tweetProcessList.ExeFollow && !tweetProcessList.ExeUnFollow) return;
            if (tweetProcessList.ExeFollow && tweetProcessList.ExeUnFollow) return;

            bool followFlag = tweetProcessList.ExeFollow;
            string targetAccountName = tweetProcessList.TargetAccountName;

            var dataAccess = new MySqlDataAccess(dbConnectin);
            var accountList = dataAccess.GetAccountMaster(true).Where(x => x.Enable == true).ToList();

            if(tweetProcessList.UserId != 0)
            {
                accountList = accountList.Where(x => x.UserId == tweetProcessList.UserId).ToList();
            }

            foreach(var account in accountList)
            {
                TweetProc(new TweetCommand() { 
                    TweetProcType = (followFlag ? TweetProcTypes.フォロー追加 : TweetProcTypes.フォロー解除),  
                    AccountId = account.Id,  
                    TweetName = tweetProcessList.TargetAccountName });
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
            TweetProcTypes tweetProcType,
            bool ユーザー権限無視,
            bool repToRep = false
            )
        {
            List<AccountMaster> retList = new List<AccountMaster>();

            DateTime dateNow = DateTime.Now;

            foreach (var account in accountMasterList)
            {
                if(account.Id == 584)
                {
                    int a = 1;
                }


                // 無効アカウントはスルー
                if (!account.Enable) continue;

                if (userMasterList.Where(x => x.Id == account.UserId).Count() != 1) continue;

                var userMasterRow = userMasterList.Where(x => x.Id == account.UserId).FirstOrDefault();

                if (userMasterRow.Enable == false) continue;
                if (tweetProcType == TweetProcTypes.いいね && !userMasterRow.LikeEnable && !ユーザー権限無視) continue;
                else if (tweetProcType == TweetProcTypes.ブックマーク && !userMasterRow.BookmarkEnable && !ユーザー権限無視) continue;
                else if (tweetProcType == TweetProcTypes.リポスト && !userMasterRow.RepostEnable) continue;   // リポストユーザー権限がないものはスルー(2025.03.02 zoom)
                else if (tweetProcType == TweetProcTypes.リプライ && !userMasterRow.ReplyEnable && !ユーザー権限無視) continue;    // リプライユーザー権限がないものでも無視する場合は強制(2025.03.02 zoom)

                // 処理無効アカウントはスルー

                // 2025.05.30 大輔 API貸し出しですが上記画像の四角で囲ってる場所にチェックがない場合はいいね等しないように修正お願いします！
                // ⇒ 貸出APIのいいねは消費しないようにしたいため、ユーザー権限無効に関わらず判定
                if(account.UseAdminApi)
                {
                    if (tweetProcType == TweetProcTypes.いいね && !account.LikeEnable) continue;
                    else if (tweetProcType == TweetProcTypes.ブックマーク && !account.BookMarkEnable) continue;
                    else if (tweetProcType == TweetProcTypes.リポスト && !account.RepostEnable) continue;
                    else if (tweetProcType == TweetProcTypes.リプライ && !account.ReplyEnable) continue;
                }
                else
                {
                    if (tweetProcType == TweetProcTypes.いいね && !account.LikeEnable && !ユーザー権限無視) continue;
                    else if (tweetProcType == TweetProcTypes.ブックマーク && !account.BookMarkEnable && !ユーザー権限無視) continue;
                    else if (tweetProcType == TweetProcTypes.リポスト && !account.RepostEnable) continue;
                    else if (tweetProcType == TweetProcTypes.リプライ && !account.ReplyEnable) continue;
                }

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
//                    if (制限時間以内に履歴ありの無料アカウントを排除)
                    if (false)  // 2026.03.02 無料アカウントの制限を解除
                    {
                            if (tweetProcType == TweetProcTypes.いいね)
                        {
                            // 無料アカウント or 有料アカウントの無料いいね
                            if (!account.Paid || !account.PaidLike)
                            {
                                var lastHistory = lastMyHistoryList.Where(x => x.Mode == TweetProcTypes.いいね).ToList();
                                if (lastHistory.Count > 0)
                                {
                                    if ((dateNow - (DateTime)lastHistory.FirstOrDefault().UpdateTime).TotalDays < 1) continue;
                                }
                            }
                        }
                        else if (tweetProcType == TweetProcTypes.ブックマーク || tweetProcType == TweetProcTypes.リポスト || tweetProcType == TweetProcTypes.リプライ)
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

                if (tweetProcType == TweetProcTypes.リプライ)
                {
                    var commentMasterListWk = commentMasterList.Where(x => x.AccountId == account.Id && x.TweetModeType == (repToRep ? TweetModeTypes.ReplyToReply : TweetModeTypes.Replay)).ToList();

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

        List<CheckTweetAccountList> _checkTweetAccountList = new List<CheckTweetAccountList>();
        List<AccountMaster> _accountMasterList = new List<AccountMaster>();
        List<SearchList> _searchList = new List<SearchList>();

        public void Init監視list(bool first_flag = false)
        {
            _checkTweetAccountList.Clear();

            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);

            _checkTweetAccountList = dataAccess.GetCheckTweetAccountList();

            _accountMasterList = dataAccess.GetAccountMaster(true).Where( x => x.Enable).ToList();

            _searchList = dataAccess.GetSearchList();

            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.監視初期化 });

            /*

            List<UserMaster> userMasterList = dataAccess.GetUserMaster().Where(x => x.Enable && x.CheckEnable).ToList();

            if(CheckUserId != 0) userMasterList = userMasterList.Where(x => x.Id == CheckUserId).ToList();

            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster();
            var 監視対象アカウント = accountMasterList.Where(x => x.Enable && (bool)x.SearchEnable && userMasterList.Any(user => user.Id == x.UserId)).ToList();

            // 監視対象アカウントの AccountId 一覧を取得
            var 監視対象アカウントID一覧 = 監視対象アカウント.Select(x => x.Id).ToHashSet();

            var tweetWatchMasterList = dataAccess.GetTweetWatchMaster();

            tweetWatchMasterList = tweetWatchMasterList.Where(x => (x.CommentEnable_Reply || x.CommentEnable_Tweet || x.MonomaneEnable_Tweet)).ToList();

            // tweetWatchMasterListをさらに絞り込み
            tweetWatchMasterList = tweetWatchMasterList
                .Where(x => 監視対象アカウントID一覧.Contains(x.AccountId))
                .ToList();

            dataAccess.InitTweetWatch(tweetWatchMasterList.Select(x => x.WatchUserName).Distinct().ToList());

            */

            /*

            List<SearchList> wk1 = dataAccess.GetSearchList().Where(x => (bool)x.Enable).ToList();
            List<SearchList> wk2 = wk1.Where(x => userMasterList.Any(user => user.Id == x.SearchUserId)).ToList();
            List<SearchList> searchList_通常 = wk2.Where(x => 監視対象アカウント.Any(y => (bool)y.Enable)).ToList();

//            searchList_通常.Clear();

            var 自動AIリプライアカウント = accountMasterList
                .Where(x => x.Enable &&
                (bool)x.AiReplyEnable &&
                x.AiMode == 2 &&
                x.GROQ_API_KEY != null &&
                x.OPENAI_API_KEY != null &&
                x.AiReplyPrompt != null).ToList();

            List<SearchList> searchList_自動リプ = new List<SearchList>();
            foreach (var item in 自動AIリプライアカウント)
            {
                SearchList searchItem = new SearchList()
                {
                    SearchUserId = item.UserId,
                    Enable = true,
                    LastReplyTime = DateTime.Now,
                    CheckInterval = item.CheckInterval,
                    CheckDate = DateTime.Now,
                    FirstFlag = true,
                    TimeEnable = false,
                    CheckAiRepMode = true,
                    ReplyAccountId = item.Id

                };

                searchList_自動リプ.Add(searchItem);
            }

            List<SearchList> searchList = new List<SearchList>();

            searchList.AddRange(searchList_通常);
            searchList.AddRange(searchList_自動リプ);

//            searchList = searchList.Where(x => x.PostAccountId == 239).ToList();

            List<AccountMaster> accountList = new List<AccountMaster>();
            accountList.AddRange(監視対象アカウント);
            accountList.AddRange(自動AIリプライアカウント);


            InitSearchHistory(accountList);

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
            */

            _replyCommentList = dataAccess.GetCommentMaster().Where(x => x.TweetModeType == TweetModeTypes.Replay).ToList();
            _replyToReplyCommentList = dataAccess.GetCommentMaster().Where(x => x.TweetModeType == TweetModeTypes.ReplyToReply).ToList();

        }

        public void InitSearchHistory(List<AccountMaster> accountMasterList)
        {
            _searchHistoryList.Clear();

            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);

            List<TweetHistory> tweetHistoryList = dataAccess.GetTweetHistoryView(1).Where(x => x.Mode == TweetProcTypes.ポスト監視).ToList();

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

        /*
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
        */

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

            // 日付変更時にに再初期化
            if(_監視list作成日時.Date != DateTime.Now.Date)
            {
                Init監視list(false);
                _監視list作成日時 = DateTime.Now;
            }

            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);

            var list = dataAccess.GetCheckTweetAccountList();

            List<CheckTweetAccountList> 追加tweetItems = new List<CheckTweetAccountList>();

            foreach(var row in list)
            {
                if(!_checkTweetAccountList.Any(x => x.TweetId == row.TweetId))
//                if (_checkTweetAccountList.Where(x => x.TweetId == row.TweetId).Count() == 0)
                {
                    追加tweetItems.Add(row);
                }
            }


            foreach( var item in 追加tweetItems)
            {
                var targetSearchList = _searchList.Where(x => x.SearchUserName == item.AccountName).ToList();

                foreach(var targetRow in targetSearchList)
                {
                    if(item.Type == TweetProcTypes.ポスト)
                    {
                        if ((bool)targetRow.PostEnable)
                        {
                            TweetProcReply(targetRow, item.TweetId);
                        }

                        if ((bool)targetRow.MonomaneEnable)
                        {
                            TweetProcMonomane(targetRow, item.TweetId);
                        }
                    }
                    else if(item.Type == TweetProcTypes.リプライ)
                    {
                        if ((bool)targetRow.ReplyEnable)
                        {
                            // 自分宛のリプライは除外
                            if(item.TweetId != item.ReplyToTweetId)
                            {
                                //08.22 未実装の為、一旦コメントアウト
                                TweetProcReplyToReply(targetRow, item.TweetId);
                            }
                        }
                    }


                }

                /*
                if (tweetResult != null && (bool)item.PostEnable && tweetResult.result1 == true)
                {
                    TweetProcReply(item, tweetResult);
                }

                if (tweetResult != null && (bool)item.ReplyEnable && tweetResult.result2 == true)
                {
                    TweetProcReplyToReply(item, tweetResult);
                }
                */

            }

//            _checkTweetAccountList = list;
            _checkTweetAccountList.AddRange(追加tweetItems);

            /*

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
                    TweetProcType = item.CheckAiRepMode ? TweetProcTypes.AIリプ監視 : TweetProcTypes.ポスト監視, 
                    SearchId = item.Id,
                    AccountId = searchHistoryRow.AccountId,
                    AccountId2 = item.ReplyAccountId
                });

                item.CheckDate = dtNow.AddSeconds(item.CheckInterval);
                RenewSearchDateTime(searchHistoryRow);

//                if (item.FirstFlag == false)
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
            */

            _監視Timer.Enabled = true;

        }



        #endregion

        #region TweetProc関連

        /// <summary>
        /// 2025.08.22 commentId取得できない場合も許容するよう変更(AIリプのため)
        /// </summary>
        /// <param name="searchList"></param>
        /// <param name="targetTweetId"></param>
        public void TweetProcReply(SearchList searchList, string targetTweetId)
        {
            int accountId = searchList.AccountId;
            var commentItem = SupportUtil.GetRandomItem(_replyCommentList.Where(x => x.AccountId == accountId).ToList());
            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.リプライ, AccountId = accountId, CommentId = commentItem?.Id ?? 0, TweetId = targetTweetId });
        }

        public void TweetProcMonomane(SearchList searchList, string targetTweetId)
        {
            int accountId = searchList.AccountId;
            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.モノマネ, AccountId = accountId, TweetId = targetTweetId });
        }

        public void TweetProcReply(SearchList searchList, TweetResult result)
        {
            //            int accountId = SupportUtil.GetRandomItem(checkAccountList.ExeAccountIdList);
            int accountId = searchList.AccountId;

            if (_replyCommentList.Where(x => x.AccountId == accountId).Count() == 0) return;

            var commentItem = SupportUtil.GetRandomItem(_replyCommentList.Where(x => x.AccountId == accountId).ToList());
            if (commentItem == null) return;
            var commentId = commentItem.Id;
            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.リプライ, AccountId = accountId, CommentId = commentId, TweetId = result.contents1 });
        }

        public void TweetProcReplyToReply(SearchList searchList, string targetTweetId)
        {
            //            int accountId = SupportUtil.GetRandomItem(checkAccountList.ExeAccountIdList);
            int accountId = searchList.AccountId;

            var commentItem = SupportUtil.GetRandomItem(_replyToReplyCommentList.Where(x => x.AccountId == accountId).ToList());
            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.リプライ, AccountId = accountId, CommentId = commentItem?.Id ?? 0, TweetId = targetTweetId });

            /*
            if (_replyToReplyCommentList.Where(x => x.AccountId == accountId).Count() == 0) return;

            var commentItem = SupportUtil.GetRandomItem(_replyToReplyCommentList.Where(x => x.AccountId == accountId).ToList());
            if (commentItem == null) return;
            var commentId = commentItem.Id;

            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.リプライ, AccountId = accountId, CommentId = commentId, TweetId = targetTweetId });
            */
        }

        public void TweetProcReplyToReply(SearchList searchList, TweetResult result)
        {
            //            int accountId = SupportUtil.GetRandomItem(checkAccountList.ExeAccountIdList);
            int accountId = searchList.AccountId;

            if (_replyToReplyCommentList.Where(x => x.AccountId == accountId).Count() == 0) return;

            var commentItem = SupportUtil.GetRandomItem(_replyToReplyCommentList.Where(x => x.AccountId == accountId).ToList());
            if (commentItem == null) return;
            var commentId = commentItem.Id;

            TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.リプライ, AccountId = accountId, CommentId = commentId, TweetId = result.contents2 });
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
                case TweetProcTypes.いいね:
                    return "like";
                    break;
                case TweetProcTypes.JAPいいね:
                    return "jap_like";
                    break;
                case TweetProcTypes.リプライ:
                    return "reply";
                    break;
                case TweetProcTypes.ブックマーク:
                    return "bookmark";
                    break;
                case TweetProcTypes.JAPブックマーク:
                    return "jap_bookmark";
                    break;
                case TweetProcTypes.リポスト:
                    return "repost";
                    break;
                case TweetProcTypes.JAPリポスト:
                    return "jap_repost";
                    break;
                case TweetProcTypes.ポスト:
                    return "post";
                    break;
                case TweetProcTypes.ｱｸｾｽﾄｰｸﾝ取得:
                    return "get_access_token";
                    break;
                case TweetProcTypes.ﾘﾌﾚｯｼｭﾄｰｸﾝ更新:
                    return "get_refresh_token";
                    break;
                case TweetProcTypes.モノマネ:
                    return "monomane";
                    break;
                case TweetProcTypes.ポスト監視:
                    return "check";
                    break;
                case TweetProcTypes.リプ監視:
                    return "checkrep";
                    break;

                case TweetProcTypes.AIリプ監視:
                    return "checkairep";
                    break;

                case TweetProcTypes.フォロー追加:
                    return "follow";
                    break;

                case TweetProcTypes.フォロー解除:
                    return "unfollow";
                    break;
                case TweetProcTypes.JAPプロフィール:
                    return "jap_profile";
                    break;
                case TweetProcTypes.JAP詳細:
                    return "jap_detail";
                    break;
            }
            return string.Empty;
        }

        //        public void TweetProc(TweetProcTypes tweetProcType, int userId, int accountId, int commentId, string tweetId)
        public  TweetResult TweetProc(TweetCommand tweetCommand)
        {
            ReadIniファイル();


            // Pythonスクリプトのパスを指定
            string pythonScriptPath = $@"{pythonWorkingPath}\tweet.py";

            switch (tweetCommand.TweetProcType)
            {
                case TweetProcTypes.ポスト:

                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} comment_id={tweetCommand.CommentId} ai_enable={tweetCommand.AiEnable}";

                    if(tweetCommand.MediaType != MediaTypes.None)
                    {
                        pythonScriptPath += $" media_type={(tweetCommand.MediaType == MediaTypes.Photo ? "photo" : "video")} media_id={tweetCommand.MediaId}";
                    }

                    break;

                case TweetProcTypes.いいね:
                case TweetProcTypes.ブックマーク:
                case TweetProcTypes.リポスト:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} tweet_id={tweetCommand.TweetId}";
                    break;

                case TweetProcTypes.JAPいいね:
                case TweetProcTypes.JAPブックマーク:
                case TweetProcTypes.JAPリポスト:
                case TweetProcTypes.JAPプロフィール:
                case TweetProcTypes.JAP詳細:
                    {
                        // MySQLデータアクセスの初期化
                        var dataAccess = new MySqlDataAccess(dbConnectin);
                        List<UserMaster> userMasterList = dataAccess.GetUserMaster();
                        var userRow = userMasterList.Where(x => x.Id == tweetCommand.UserId).FirstOrDefault();
                        pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} tweet_id={tweetCommand.TweetId} tweet_name={tweetCommand.TweetName} quantity={tweetCommand.Quantity} jap_api_key={userRow.JapApiKey}";

                    }
                    break;

                case TweetProcTypes.リプライ:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} comment_id={tweetCommand.CommentId} tweet_id={tweetCommand.TweetId}";
                    break;

                case TweetProcTypes.ｱｸｾｽﾄｰｸﾝ取得:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId}";
                    break;
                case TweetProcTypes.ﾘﾌﾚｯｼｭﾄｰｸﾝ更新:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId}";
                    break;

                case TweetProcTypes.ポスト監視:
                case TweetProcTypes.リプ監視:
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

                case TweetProcTypes.モノマネ:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} tweet_id={tweetCommand.TweetId}";
                    break;

                case TweetProcTypes.AIリプ監視:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} account_id2={tweetCommand.AccountId2}";
                    break;

                case TweetProcTypes.フォロー追加:
                case TweetProcTypes.フォロー解除:
                    pythonScriptPath += $" mode={GetTweetMode(tweetCommand.TweetProcType)} account_id={tweetCommand.AccountId} tweet_name={tweetCommand.TweetName}";
                    break;

                case TweetProcTypes.監視初期化:
                    pythonScriptPath += $" mode=init_check_tweet_account_master";
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
                int timeoutMs = 15000; // 15秒でタイムアウト（必要に応じて変更）

                process.Start();

                // 非同期で出力を読む（デッドロック防止）
                Task<string> outputTask = process.StandardOutput.ReadToEndAsync();
                Task<string> errorTask = process.StandardError.ReadToEndAsync();

                // プロセス終了を待つ（タイムアウト付き）
                if (!process.WaitForExit(timeoutMs))
                {
                    process.Kill();
                    logAction?.Invoke($"{DateTime.Now.ToString()} < タイムアウト {pythonScriptPath}");
                    return new TweetResult { result1 = false, contents1 = "TIMEOUT" };
                }

                // 同期で結果を取得（ここがポイント）
                string output = outputTask.GetAwaiter().GetResult();
                string debugMessage = errorTask.GetAwaiter().GetResult();

                /*
                // 非同期で出力を読む（ReadToEnd のデッドロック防止）
                Task<string> outputTask = process.StandardOutput.ReadToEndAsync();
                Task<string> errorTask = process.StandardError.ReadToEndAsync();

                // プロセス終了を待つ（タイムアウト付き）
                if (!process.WaitForExit(timeoutMs))
                {
                    // タイムアウト発生！
                    try
                    {
                        process.Kill();
                    }
                    catch { }

                    logAction?.Invoke($"{DateTime.Now} TweetProc TIMEOUT after {timeoutMs}ms");

                    return new TweetResult
                    {
                        result1 = false,
                        contents1 = "TIMEOUT",
                        result2 = false,
                        contents2 = ""
                    };
                }

                // 出力取得（プロセスが正常終了した場合）
                string output = await outputTask;
                string debugMessage = await errorTask;
                */

                /*
                process.Start();
                string output = process.StandardOutput.ReadToEnd(); // Pythonスクリプトの標準出力
                string debugMessage = process.StandardError.ReadToEnd();   // Pythonスクリプトの標準エラー
                process.WaitForExit();
                */

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
                tweet_id = tweetVpsCommand.TweetId,
                like_count = tweetVpsCommand.LikeCount,
                like_list = tweetVpsCommand.LikeList,
                bookmark_count = tweetVpsCommand.BookmarkCount,
                bookmark_list = tweetVpsCommand.BookmarkList,
                repost_list = tweetVpsCommand.RepostList,
                reply_list = tweetVpsCommand.ReplyList,  // ここはそのままリストで渡す
                rep_to_rep = tweetVpsCommand.RepToRep,    // これは bool 型なのでそのままでOK
                id = tweetVpsCommand.VpsId
                /*
                tweet_id = tweetVpsCommand.TweetId ,
                like_list = string.Join(",", tweetVpsCommand.LikeList),
                bookmark_list = string.Join(",", tweetVpsCommand.BookmarkList),
                repost_list = string.Join(",", tweetVpsCommand.RepostList),
                reply_list = string.Join(",", tweetVpsCommand.ReplyList),
                rep_to_rep = string.Join(",", tweetVpsCommand.RepToRep),
                */
            };
            string json = JsonConvert.SerializeObject(requestData);
            var content = new StringContent(json, Encoding.UTF8, "application/json");

            try
            {
                // ヘッダー設定
                httpClient.DefaultRequestHeaders.Accept.Clear();
                httpClient.DefaultRequestHeaders.Accept.Add(new System.Net.Http.Headers.MediaTypeWithQualityHeaderValue("application/json"));


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
                case TweetProcTypes.ポスト:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId} comment_id={commentId}";
                    break;
                case TweetProcTypes.いいね:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId} tweet_id={tweetId}";
                    break;
                case TweetProcTypes.ブックマーク:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId} tweet_id={tweetId}";
                    break;
                case TweetProcTypes.ｱｸｾｽﾄｰｸﾝ取得:
                    pythonScriptPath += $" mode={GetTweetMode(tweetProcType)} account_id={accountId}";
                    break;
                case TweetProcTypes.ﾘﾌﾚｯｼｭﾄｰｸﾝ更新:
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
