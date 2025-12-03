using System;
using System.Collections.Generic;
using System.ComponentModel.Design;
using System.Data.Common;
using System.Linq;
using System.Text;
using System.Threading;
using System.Threading.Tasks;
using System.Timers;
using DbotManager.Table;

namespace DbotManager
{
    public class ReserveTask
    {
        private readonly Action<string> logAction;

        private DbConnectionInfo dbConnectin;

        public bool 作成済 { get; set; }

        private static System.Timers.Timer _予約監視Timer;

        private List<ReserveSchedule> _reserveScheduleList = new List<ReserveSchedule>();

        private DateTime dtBk = DateTime.Today;

        List<AccountMaster> _accountList = new List<AccountMaster>();

        public ReserveTask(DbConnectionInfo dbConnection, Action<string> logAction = null)
        {
            this.logAction = logAction;
            dbConnectin = dbConnection;

            作成済 = false;
        }

        public List<ReserveSchedule> MakeScheduleList()
        {
            // MySQLデータアクセスの初期化
            var dataAccess = new MySqlDataAccess(dbConnectin);

//            _accountList = dataAccess.GetAccountMaster(true).Where(x => x.Enable && x.PostEnable).ToList();
            _accountList = dataAccess.GetAccountMaster(true).Where(x => x.Id == 3228). Where(x => x.Enable && x.PostEnable).ToList();
            
            List<ReserveMaster> reserveMasterList = new List<ReserveMaster>();
            List<CommentMaster> commentMasterList = dataAccess.GetCommentMaster();
            List<MediaMaster> mediaMasterList = dataAccess.GetMediaMaster();

            foreach (var account in _accountList)
            {
//              var reserve = dataAccess.GetReserveMaster(account.Id);

                if (account.Reserve1StartHour > account.Reserve1EndHour)
                    account.Reserve1EndHour += 24;
                if (account.Reserve2StartHour > account.Reserve2EndHour)
                    account.Reserve2EndHour += 24;
                if (account.Reserve3StartHour > account.Reserve3EndHour)
                    account.Reserve3EndHour += 24;
                if (account.Reserve4StartHour > account.Reserve4EndHour)
                    account.Reserve4EndHour += 24;

//              if (account != null) reserveMasterList.Add(reserve);
            }

            List<ReserveSchedule> reserveScheduleList = new List<ReserveSchedule>();

            int noCommentCnt = 0;

            foreach (var account in _accountList)
            {
                // ランダム指定済みのコメントは除外する
                var commentList = commentMasterList
                    .Where(x => x.AccountId == account.Id)// && !withoutCommentIdList.Contains(x.Id))
                    .Where(x => x.TweetModeType == TweetModeTypes.Post)
                    .ToList();


                /*
                if (commentList.Count == 0)
                {
                    noCommentCnt++;
                    continue;
                }
                */

//                var targetAccount = _accountList.Where(x => x.Id == account.AccountId).FirstOrDefault();

                if (account.Reserve1Enable)
                {
                    var commentListWk = commentList.Where(x => x.ReserveMode == 0 || x.ReserveMode == 1).ToList();
//                    if(commentListWk.Count > 0)
                    {
//                        var scheduleWk = MakeSchedule(reserve.Reserve1Count, reserve.Reserve1StartHour, reserve.Reserve1EndHour, reserve.UserId, reserve.AccountId,  commentListWk, 1, reserveScheduleList, mediaMasterList , targetAccount);
                        var scheduleWk = MakeSchedule(account, commentListWk, 1, reserveScheduleList, mediaMasterList);
                        reserveScheduleList.AddRange(scheduleWk);
                    }
                }

                if (account.Reserve2Enable)
                {
                    var commentListWk = commentList.Where(x => x.ReserveMode == 0 || x.ReserveMode == 2).ToList();
//                    if (commentListWk.Count > 0)
                    {
//                        var scheduleWk = MakeSchedule(reserve.Reserve2Count, reserve.Reserve2StartHour, reserve.Reserve2EndHour, reserve.UserId, reserve.AccountId, commentListWk, 2, reserveScheduleList, mediaMasterList, targetAccount);
                        var scheduleWk = MakeSchedule(account, commentListWk, 2, reserveScheduleList, mediaMasterList);
                        reserveScheduleList.AddRange(scheduleWk);
                    }
                }

                if (account.Reserve3Enable)
                {
                    var commentListWk = commentList.Where(x => x.ReserveMode == 0 || x.ReserveMode == 3).ToList();
//                    if (commentListWk.Count > 0)
                    {
//                        var scheduleWk = MakeSchedule(reserve.Reserve3Count, reserve.Reserve3StartHour, reserve.Reserve3EndHour, reserve.UserId, reserve.AccountId, commentListWk, 3, reserveScheduleList, mediaMasterList, targetAccount);
                        var scheduleWk = MakeSchedule(account, commentListWk, 3, reserveScheduleList, mediaMasterList);
                        reserveScheduleList.AddRange(scheduleWk);
                    }
                }

                if (account.Reserve4Enable)
                {
                    var commentListWk = commentList.Where(x => x.ReserveMode == 0 || x.ReserveMode == 4).ToList();
//                    if (commentListWk.Count > 0)
                    {
//                        var scheduleWk = MakeSchedule(reserve.Reserve4Count, reserve.Reserve4StartHour, reserve.Reserve4EndHour, reserve.UserId, reserve.AccountId, commentListWk, 4, reserveScheduleList, mediaMasterList, targetAccount);
                        var scheduleWk = MakeSchedule(account, commentListWk, 4, reserveScheduleList, mediaMasterList);
                        reserveScheduleList.AddRange(scheduleWk);
                    }
                }
            }

//            dataAccess.DeleteReserveSchedule(DateTime.Today);

            foreach (var item in reserveScheduleList)
            {

                if (!(bool)item.AiEnable)
                { 
                    var commentItem = commentMasterList.Where(x => x.Id == item.CommentId).ToList();
                    if (commentItem.Count > 0)
                    {
                        item.Comment = commentItem.FirstOrDefault().Comment;
                    }

                }
                var accountItem = _accountList.Where(x => x.Id == item.AccountId).ToList();
                if (accountItem.Count > 0)
                {
                    item.AccountName = accountItem.FirstOrDefault().Name;
                }
            }


            foreach (var item in reserveScheduleList)
            {
//                dataAccess.InsertReserveSchedule(item);
            }

            if (reserveScheduleList.Count > 0) 作成済 = true;

            _reserveScheduleList.Clear();
            _reserveScheduleList.AddRange(reserveScheduleList.OrderBy(x => x.ReserveDate).ThenBy(x => x.ReserveTime));

            return reserveScheduleList;
        }

//        private List<ReserveSchedule> MakeSchedule(int count, int startHour, int endHour, int userId, int accountId, List<CommentMaster> commentList, int type , List<ReserveSchedule> reserveList , List<MediaMaster> mediaMasterList, AccountMaster accountMaster)
        private List<ReserveSchedule> MakeSchedule(AccountMaster account, List<CommentMaster> commentList, int type, List<ReserveSchedule> reserveList, List<MediaMaster> mediaMasterList)
        {
            int count = 0, startHour = 0, endHour = 0, userId = account.UserId, accountId = account.Id;
            bool ai_enable = false;

            switch(type)
            {
                case 1:
                    count = account.Reserve1Count;
                    startHour = account.Reserve1StartHour;
                    endHour = account.Reserve1EndHour;
                    ai_enable = (bool)account.AiPostEnable && (bool)account.Reserve1Ai;
                    break;
                case 2:
                    count = account.Reserve2Count;
                    startHour = account.Reserve2StartHour;
                    endHour = account.Reserve2EndHour;
                    ai_enable = (bool)account.AiPostEnable && (bool)account.Reserve2Ai;
                    break;
                case 3:
                    count = account.Reserve3Count;
                    startHour = account.Reserve3StartHour;
                    endHour = account.Reserve3EndHour;
                    ai_enable = (bool)account.AiPostEnable && (bool)account.Reserve3Ai;
                    break;
                case 4:
                    count = account.Reserve4Count;
                    startHour = account.Reserve4StartHour;
                    endHour = account.Reserve4EndHour;
                    ai_enable = (bool)account.AiPostEnable && (bool)account.Reserve4Ai;
                    break;
            }



            var schedules = new List<ReserveSchedule>();

            // 2025.12.03 時間設定が正常に出ていないと無限ループになるため、リターン
            if (startHour >= endHour) return schedules;

            var random = new Random();
            var withoutCommentIdList = reserveList.Select(x => (int)x.CommentId).ToList();

            Thread.Sleep(10);
            // ランダムな件数を設定 (0 ～ count)
//            int randomCount = random.Next(count+1); // countを含めるため +1
            int randomCount = random.Next(1 , count + 1); // 0を除外してランダムカウント生成
            Thread.Sleep(10);

            // 今日の日付
            var today = DateTime.Today;

            // 開始時刻と終了時刻
            var startDateTime = startHour >= 24
                ? today.AddDays(1).AddHours(startHour - 24) // 翌日の時間
                : today.AddHours(startHour);

            var endDateTime = endHour >= 24
                ? today.AddDays(1).AddHours(endHour - 24) // 翌日の時間
                : today.AddHours(endHour);                // 当日の時間

            // ランダムな時間を生成する
            for (int i = 0; i < randomCount; i++)
            {
                DateTime randomTime;
                int attempt = 0;
                const int maxAttempt = 20;

                do
                {
                    attempt++;
                    if (attempt > maxAttempt)
                    {
                        // ★ 20 回失敗 → 無限ループ回避のため return
                        Console.WriteLine("ランダム時間生成に失敗したため return します");
                        return schedules;
                    }

                    Thread.Sleep(1);

                    // ランダムな時刻を生成
                    var totalMinutes = (int)(endDateTime - startDateTime).TotalMinutes;
                    randomTime = startDateTime.AddMinutes(random.Next(totalMinutes)).AddSeconds(random.Next(60));
                }
                // 直前のスケジュールと5分以上の間隔を設ける
                while (schedules.Any(s => Math.Abs(((DateTime)s.ReserveTime - randomTime).TotalMinutes) < 5));

                MediaMaster mediaRow = null;
                CommentMaster randomComment = null;

                if (ai_enable)
                {
                    int aiMediaSelectionRate = account.AiMediaSelectionRate; // 例: 30 なら 30% の確率でメディアを使う

                    int randomValue = random.Next(1, 101); // 1〜100 の乱数を生成

                    // 乱数が選択率以上の場合はスルー（何もせず抜ける）
                    if (randomValue <= aiMediaSelectionRate)
                    {
                        if ((bool)account.AiPhotoEnable && (bool)account.AiMovieEnable)
                        {
                            var mediaList = mediaMasterList.Where(x => x.AccountId == account.Id).ToList();
                            if (mediaList.Count > 0)
                            {
                                mediaRow = mediaList[random.Next(mediaList.Count)];
                            }
                        }
                        else if ((bool)account.AiPhotoEnable)
                        {
                            var mediaList = mediaMasterList.Where(x => x.AccountId == account.Id && x.MediaType == MediaTypes.Photo).ToList();
                            if (mediaList.Count > 0)
                            {
                                mediaRow = mediaList[random.Next(mediaList.Count)];
                            }
                        }
                        else if ((bool)account.AiMovieEnable)
                        {
                            var mediaList = mediaMasterList.Where(x => x.AccountId == account.Id && x.MediaType == MediaTypes.Movie).ToList();
                            if (mediaList.Count > 0)
                            {
                                mediaRow = mediaList[random.Next(mediaList.Count)];
                            }
                        }
                    }
                }
                else
                {
                    if (commentList.Count == 0) continue;

                    var commentList_重複除外 = commentList.Where(x => !withoutCommentIdList.Contains(x.Id)).ToList();

                    if (commentList_重複除外.Count == 0) continue;

                    Thread.Sleep(1);

                    // CommentMaster からランダムに1つ選択
                    randomComment = commentList_重複除外[random.Next(commentList_重複除外.Count)];
                    
                    if (randomComment.PhotoEnable)
                    {
                        var mediaList = mediaMasterList.Where(x => x.AccountId == randomComment.AccountId && x.MediaType == MediaTypes.Photo).ToList();
                        if (mediaList.Count > 0)
                        {
                            mediaRow = mediaList[random.Next(mediaList.Count)];
                        }
                    }
                    else if (randomComment.MovieEnable)
                    {
                        var mediaList = mediaMasterList.Where(x => x.AccountId == randomComment.AccountId && x.MediaType == MediaTypes.Movie).ToList();
                        if (mediaList.Count > 0)
                        {
                            mediaRow = mediaList[random.Next(mediaList.Count)];
                        }
                    }
                }


                // スケジュールを追加
                schedules.Add(new ReserveSchedule
                {
                    ReserveDate = today,
                    ReserveTime = randomTime,
                    UserId = userId,
                    AccountId = accountId,
                    CommentId = ai_enable ? 0 : randomComment.Id,
                    ReserveId = $"{accountId}-{type}-{(i + 1)}",
                    Result = false,

                    MediaType = mediaRow == null ? MediaTypes.None : mediaRow.MediaType,
                    MediaId = mediaRow == null ? null : (int?)mediaRow.MediaId,

                    AiEnable = ai_enable,
                });

                 if (!ai_enable)
                {
                    withoutCommentIdList.Add(randomComment.Id);
                }

            }

            return schedules;
        }

        public void StartTask()
        {
            // タイマーを設定（1000msごと = 1秒ごと）
            _予約監視Timer = new System.Timers.Timer(10 * 1000);
            _予約監視Timer.Elapsed += OnTimedEvent;
            _予約監視Timer.AutoReset = true; // 繰り返し実行
            _予約監視Timer.Enabled = true;
        }

        public void EndTask()
        {
            _予約監視Timer.Enabled = false;
        }

        private static object _lockObj = new object();

        public void OnTimedEvent(object sender, ElapsedEventArgs e)
        {

            if (!Monitor.TryEnter(_lockObj))
            {
                // 既に実行中
                Console.WriteLine($"OnTimedEvent:実行中の処理がある為return({DateTime.Now})");
                return;
            }

            try
            {
                Console.WriteLine($"OnTimedEvent:処理を実行中({DateTime.Now})");

                DateTime dtNow = DateTime.Now;

                // 日付が変わったらリスト再作成
                if (DateTime.Today != dtBk)
                {
                    MakeScheduleList();
                }

                foreach (var reserveSchedule in _reserveScheduleList)
                {
                    if (reserveSchedule.Result) continue;

                    if (reserveSchedule.ReserveDate == null) continue;
                    if (reserveSchedule.ReserveTime == null) continue;

                    if ((DateTime)reserveSchedule.ReserveDate.Value.Date != dtNow.Date) continue;

                    // 未来の予約をスルー
                    if ((DateTime)reserveSchedule.ReserveTime.Value > dtNow) continue;

                    // 過去３分以上過ぎたものをスルー
                    if ((DateTime)reserveSchedule.ReserveTime.Value < dtNow.AddMinutes(-5)) continue;

                    // 無効ユーザーの処理は無視
                    if (_accountList.Where(x => x.Id == reserveSchedule.AccountId).Count() == 0)
                    {
                        Console.WriteLine($"OnTimedEvent　無効ユーザーの処理は無視: {DateTime.Now}");
                        continue;
                    }

                    TweetTask task = new TweetTask(dbConnectin, logAction);
                    var result = task.TweetProc(new TweetCommand()
                    {
                        TweetProcType = TweetProcTypes.ポスト,
                        AccountId = (int)reserveSchedule.AccountId,
                        CommentId = (int)reserveSchedule.CommentId,
                        MediaId = reserveSchedule.MediaId,
                        MediaType = reserveSchedule.MediaType,
                        AiEnable = (bool)reserveSchedule.AiEnable,
                    }
                    );

                    if (result != null)
                    {
                        if (result.result1 == true)
                        {
                            reserveSchedule.Result = true;
                        }
                        else
                        {
                            if (result.contents1.Contains("Too Many Requests"))
                            {
                                reserveSchedule.Result = true;
                            }
                        }

                        reserveSchedule.Result = true;
                    }

                    //2025.06.20 Taskエラーでnullが帰ってきたときにリトライ処理を行わせないための暫定対応
                    reserveSchedule.Result = true;

                }

                dtBk = DateTime.Today;

                /*

                foreach (var item in CheckAccountList_監視)
                {
                    int exeAccountId = SupportUtil.GetRandomItem(item.ExeAccountIdList);
                    var tweetResult = TweetProc(new TweetCommand() { TweetProcType = TweetProcTypes.CHECK, AccountId = 監視実施AccountId, AccountId2 = exeAccountId, CheckAccountName = item.CheckAccount, TweetId = item.SinceTweetId });

                    if (tweetResult != null && tweetResult.result == true)
                    {
                        TweetProcReply(item, tweetResult);
                    }
                }
                */
            }
            finally
            {
                Monitor.Exit(_lockObj);
            }
        }
    }
}
