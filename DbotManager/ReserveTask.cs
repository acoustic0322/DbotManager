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

            var accountList = dataAccess.GetAccountMaster(true).Where(x => x.Enable && x.PostEnable);

            List<ReserveMaster> reserveMasterList = new List<ReserveMaster>();
            List<AccountMaster> accountMasterList = dataAccess.GetAccountMaster();
            List<CommentMaster> commentMasterList = dataAccess.GetCommentMaster();
            List<MediaMaster> mediaMasterList = dataAccess.GetMediaMaster();

            foreach (var account in accountList)
            {
                var reserve = dataAccess.GetReserveMaster(account.Id);
                if(reserve != null) reserveMasterList.Add(reserve);
            }

            List<ReserveSchedule> reserveScheduleList = new List<ReserveSchedule>();

            foreach (var reserve in reserveMasterList)
            {
                // ランダム指定済みのコメントは除外する
                var commentList = commentMasterList
                    .Where(x => x.AccountId == reserve.AccountId)// && !withoutCommentIdList.Contains(x.Id))
                    .Where(x => x.TweetModeType == TweetModeTypes.Post)
                    .ToList();

                if (commentList.Count == 0) continue;

                if (reserve.Reserve1Enable)
                {
                    var commentListWk = commentList.Where(x => x.ReserveMode == 0 || x.ReserveMode == 1).ToList();
                    if(commentListWk.Count > 0)
                    {
                        var scheduleWk = MakeSchedule(reserve.Reserve1Count, reserve.Reserve1StartHour, reserve.Reserve1EndHour, reserve.UserId, reserve.AccountId, commentListWk, 1, reserveScheduleList, mediaMasterList);
                        reserveScheduleList.AddRange(scheduleWk);
                    }
                }

                if (reserve.Reserve2Enable)
                {
                    var commentListWk = commentList.Where(x => x.ReserveMode == 0 || x.ReserveMode == 2).ToList();
                    if (commentListWk.Count > 0)
                    {
                        var scheduleWk = MakeSchedule(reserve.Reserve2Count, reserve.Reserve2StartHour, reserve.Reserve2EndHour, reserve.UserId, reserve.AccountId, commentListWk, 2, reserveScheduleList, mediaMasterList);
                        reserveScheduleList.AddRange(scheduleWk);
                    }
                }

                if (reserve.Reserve3Enable)
                {
                    var commentListWk = commentList.Where(x => x.ReserveMode == 0 || x.ReserveMode == 3).ToList();
                    if (commentListWk.Count > 0)
                    {
                        var scheduleWk = MakeSchedule(reserve.Reserve3Count, reserve.Reserve3StartHour, reserve.Reserve3EndHour, reserve.UserId, reserve.AccountId, commentListWk, 3, reserveScheduleList, mediaMasterList);
                        reserveScheduleList.AddRange(scheduleWk);
                    }
                }

                if (reserve.Reserve4Enable)
                {
                    var commentListWk = commentList.Where(x => x.ReserveMode == 0 || x.ReserveMode == 4).ToList();
                    if (commentListWk.Count > 0)
                    {
                        var scheduleWk = MakeSchedule(reserve.Reserve4Count, reserve.Reserve4StartHour, reserve.Reserve4EndHour, reserve.UserId, reserve.AccountId, commentListWk, 4, reserveScheduleList, mediaMasterList);
                        reserveScheduleList.AddRange(scheduleWk);
                    }
                }
            }

            dataAccess.DeleteReserveSchedule(DateTime.Today);


            foreach (var item in reserveScheduleList)
            {
                var commentItem = commentMasterList.Where(x => x.Id == item.CommentId).ToList();
                if(commentItem.Count > 0)
                {
                    item.Comment = commentItem.FirstOrDefault().Comment;
                }

                var accountItem = accountMasterList.Where(x => x.Id == item.AccountId).ToList();
                if (accountItem.Count > 0)
                {
                    item.AccountName = accountItem.FirstOrDefault().Name;
                }
            }


            foreach (var item in reserveScheduleList)
            {
                dataAccess.InsertReserveSchedule(item);
            }

            if (reserveScheduleList.Count > 0) 作成済 = true;

            _reserveScheduleList.Clear();
            _reserveScheduleList.AddRange(reserveScheduleList);

            return reserveScheduleList;
        }

        private List<ReserveSchedule> MakeSchedule(int count, int startHour, int endHour, int userId, int accountId, List<CommentMaster> commentList, int type , List<ReserveSchedule> reserveList , List<MediaMaster> mediaMasterList)
        {
            var schedules = new List<ReserveSchedule>();
            var random = new Random();
            var withoutCommentIdList = reserveList.Select(x => (int)x.CommentId).ToList();

            int randWait = 0;

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
            for (int i = 0; i < count; i++)
            {
                DateTime randomTime;

                do
                {
                    randWait = random.Next(100, 300);
                    Thread.Sleep(randWait);

                    // ランダムな時刻を生成
                    var totalMinutes = (int)(endDateTime - startDateTime).TotalMinutes;
                    randomTime = startDateTime.AddMinutes(random.Next(totalMinutes)).AddSeconds(random.Next(60));
                }
                // 直前のスケジュールと5分以上の間隔を設ける
                while (schedules.Any(s => Math.Abs(((DateTime)s.ReserveTime - randomTime).TotalMinutes) < 5));

                var commentList_重複除外 = commentList.Where(x => !withoutCommentIdList.Contains(x.Id)).ToList();

                if (commentList_重複除外.Count == 0) continue;

                randWait = random.Next(100, 300);
                Thread.Sleep(randWait);

                // CommentMaster からランダムに1つ選択
                var randomComment = commentList_重複除外[random.Next(commentList_重複除外.Count)];

                MediaMaster mediaRow = null;
                if(randomComment.MovieEnable)
                {
                    var mediaList = mediaMasterList.Where(x => x.AccountId == randomComment.AccountId && x.MediaType == MediaTypes.Photo).ToList();
                    if(mediaList.Count > 0)
                    {
                        mediaRow = mediaList[random.Next(mediaList.Count)];
                    }
                }
                else if(randomComment.MovieEnable)
                {
                    var mediaList = mediaMasterList.Where(x => x.AccountId == randomComment.AccountId && x.MediaType == MediaTypes.Movie).ToList();
                    if (mediaList.Count > 0)
                    {
                        mediaRow = mediaList[random.Next(mediaList.Count)];
                    }
                }

                // スケジュールを追加
                schedules.Add(new ReserveSchedule
                {
                    ReserveDate = today,
                    ReserveTime = randomTime,
                    UserId = userId,
                    AccountId = accountId,
                    CommentId = randomComment.Id,
                    ReserveId = $"{accountId}-{type}-{(i + 1)}",
                    Result = false,

                    MediaType = mediaRow == null ? MediaTypes.None : mediaRow.MediaType,
                    MediaId = mediaRow == null ? null : (int?)mediaRow.MediaId,
                });

                withoutCommentIdList.Add(randomComment.Id);
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

        public void OnTimedEvent(object sender, ElapsedEventArgs e)
        {
            Console.WriteLine($"処理を実行中: {DateTime.Now}");

            DateTime dtNow = DateTime.Now;

            // 日付が変わったらリスト再作成
            if(DateTime.Today != dtBk)
            {
                MakeScheduleList();
            }

            foreach(var reserveSchedule in _reserveScheduleList)
            {
                if (reserveSchedule.Result) continue;

                if (reserveSchedule.ReserveDate == null) continue;
                if (reserveSchedule.ReserveTime == null) continue;

                if ((DateTime)reserveSchedule.ReserveDate.Value.Date != dtNow.Date) continue;

                // 未来の予約をスルー
                if ((DateTime)reserveSchedule.ReserveTime.Value > dtNow) continue;

                // 過去３分以上過ぎたものをスルー
                if ((DateTime)reserveSchedule.ReserveTime.Value < dtNow.AddMinutes(-3)) continue;

                TweetTask task = new TweetTask(dbConnectin, logAction);
                var result = task.TweetProc(new TweetCommand() { 
                    TweetProcType = TweetProcTypes.POST,
                    AccountId = (int)reserveSchedule.AccountId,
                    CommentId = (int)reserveSchedule.CommentId ,
                    MediaId = reserveSchedule.MediaId,
                    MediaType = reserveSchedule.MediaType

                }
                );

                if(result != null)
                {
                    if (result.result1 == true)
                    {
                        reserveSchedule.Result = true;
                    }
                    else
                    {
                        if(result.contents1.Contains("Too Many Requests"))
                        {
                            reserveSchedule.Result = true;
                        }
                    }

                    reserveSchedule.Result = true;
                }


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


    }
}
