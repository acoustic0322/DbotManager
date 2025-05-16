using System;
using System.Collections.Generic;
using System.Data;
using DbotManager.Table;
using System.Data.SqlClient;
using MySql.Data.MySqlClient;
using System.ComponentModel.Design;
using DbotManager.MySql;
using DbotManager;
using static Mysqlx.Crud.UpdateOperation.Types;
using System.Linq;

public class DbConnectionInfo
{
    public string MachineName { get; set; }
    public string User { get; set; }
    public string Root { get; set; }
    public string Pass { get; set; }
}

public class MySqlDataAccess
{
    private string connectionString;

    public MySqlDataAccess(DbConnectionInfo dbConnection)
    {
        // 接続文字列の構築
        connectionString = $"Server={dbConnection.MachineName};Database={dbConnection.User};Uid={dbConnection.Root};Pwd={dbConnection.Pass};charset=utf8mb4;";
    }

    public List<TweetHistory> GetTweetHistoryView(bool allFlag = false)
    {
        List<TweetHistory> tweetHistoryList = new List<TweetHistory>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                // 現在の日時を取得
                DateTime currentDateTime = DateTime.Now;
                // 24時間前の日時を計算
                DateTime twentyFourHoursAgo = currentDateTime.AddHours(-24);

                // SQLクエリにWHERE句を追加して24時間以内のデータを絞り込む
                string query = @"
                SELECT user_id,user_name, account_id, account_name, paid ,comment, mode, target_tweet_id, result, error_log ,updatetime 
                FROM tweet_history_view 
                WHERE updatetime >= @TwentyFourHoursAgo
                ORDER BY updatetime DESC;";

                if(allFlag)
                {
                    query = @"
                    SELECT user_id,user_name, account_id, account_name, paid ,comment, mode, target_tweet_id, result, error_log ,updatetime 
                    FROM tweet_history_view 
                    ORDER BY updatetime DESC;";
                }


                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    if(!allFlag)
                    {
                        // パラメータを設定
                        command.Parameters.AddWithValue("@TwentyFourHoursAgo", twentyFourHoursAgo);

                    }

                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            try
                            {
                                TweetHistory tweetHistory = new TweetHistory
                                {
                                    UserId = int.Parse(reader["user_id"].ToString()),
                                    UserName = reader["user_name"].ToString(),
                                    AccountId = int.Parse(reader["account_id"].ToString()),
                                    AccountName = reader["account_name"].ToString(),
                                    Paid = reader["paid"].ToString() == "1",
                                    Comment = reader["comment"].ToString(),
                                    Mode = GetTweetProcType(reader["mode"].ToString()),
                                    TargetTweetID = reader["target_tweet_id"].ToString(),
                                    Result = reader["result"].ToString() == "1",
                                    ErrorLog = reader["error_log"].ToString(),
                                    UpdateTime = Convert.ToDateTime(reader["updatetime"])
                                };

                                tweetHistoryList.Add(tweetHistory);
                            }
                            catch(Exception ex)
                            {
                                Console.WriteLine("エラーが発生しました: " + ex.Message);
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return tweetHistoryList;
    }

    private TweetProcTypes GetTweetProcType(string value)
    {
        if (value == "like") return TweetProcTypes.LIKE;
        else if (value == "repost") return TweetProcTypes.REPOST;
        else if (value == "bookmark") return TweetProcTypes.BOOKMARK;
        else if (value == "post") return TweetProcTypes.POST;
        else if (value == "reply") return TweetProcTypes.REPLY;
        else if (value == "get_access_token") return TweetProcTypes.GET_ACCESSTOKEN;
        else if (value == "get_refresh_token") return TweetProcTypes.GET_REFRESHTOKEN;
        else if (value == "check" || value == "CHECK") return TweetProcTypes.CHECK;
        else if (value == "checkrep" || value == "CHECKREP") return TweetProcTypes.CHECKREP;
        else if (value == "monomane" || value == "MONOMANE") return TweetProcTypes.MONOMANE;

        return TweetProcTypes.NONE;
    }

    #region AccountMaster

    public int InsertAccountMaster(AccountMaster account)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                INSERT INTO account_master 
                (user_id, name, login_id, login_password, api_key, api_key_secret, 
                 client_id, client_secret, access_token, access_token_secret, 
                 bearer_token, refresh_token, enable, like_enable, reply_enable, bookmark_enable, 
                 repost_enable, post_enable, reserve1_enable, reserve1_start_hour, 
                 reserve1_end_hour, reserve1_count, reserve2_enable, reserve2_start_hour, 
                 reserve2_end_hour, reserve2_count, reserve3_enable, reserve3_start_hour, 
                 reserve3_end_hour, reserve3_count, reserve4_enable, reserve4_start_hour, 
                 reserve4_end_hour, reserve4_count
                 , paid_like , paid_bookmark
                )
                VALUES 
                (@UserId, @Name, @LoginId, @LoginPassword, @ApiKey, @ApiKeySecret, 
                 @ClientId, @ClientSecret, @AccessToken, @AccessTokenSecret, 
                 @BearerToken, @RefreshToken, @Enable, @LikeEnable, @ReplyEnable, @BookmarkEnable, 
                 @RepostEnable, @TweetEnable, @Reserve1Enable, @Reserve1StartHour, 
                 @Reserve1EndHour, @Reserve1Count, @Reserve2Enable, @Reserve2StartHour, 
                 @Reserve2EndHour, @Reserve2Count, @Reserve3Enable, @Reserve3StartHour, 
                 @Reserve3EndHour, @Reserve3Count, @Reserve4Enable, @Reserve4StartHour, 
                 @Reserve4EndHour, @Reserve4Count
                 ,@PaidLike, @PaidBookmark
                );
                SELECT LAST_INSERT_ID(); ";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", account.UserId);
                    command.Parameters.AddWithValue("@Name", account.Name);
                    command.Parameters.AddWithValue("@LoginId", account.LoginId);
                    command.Parameters.AddWithValue("@LoginPassword", account.LoginPass);
                    command.Parameters.AddWithValue("@ApiKey", account.ApiKey);
                    command.Parameters.AddWithValue("@ApiKeySecret", account.ApiKeySecret);
                    command.Parameters.AddWithValue("@ClientId", account.ClientId);
                    command.Parameters.AddWithValue("@ClientSecret", account.ClientSecret);
                    command.Parameters.AddWithValue("@AccessToken", account.AccessToken);
                    command.Parameters.AddWithValue("@AccessTokenSecret", account.AccessTokenSecret);
                    command.Parameters.AddWithValue("@BearerToken", account.BearerToken);
                    command.Parameters.AddWithValue("@RefreshToken", account.RefreshToken);
                    command.Parameters.AddWithValue("@Enable", account.Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@LikeEnable", account.LikeEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@ReplyEnable", account.ReplyEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@BookmarkEnable", account.BookMarkEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@RepostEnable", account.RepostEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@TweetEnable", account.PostEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve1Enable", account.Reserve1Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve1StartHour", account.Reserve1StartHour);
                    command.Parameters.AddWithValue("@Reserve1EndHour", account.Reserve1EndHour);
                    command.Parameters.AddWithValue("@Reserve1Count", account.Reserve1Count);
                    command.Parameters.AddWithValue("@Reserve2Enable", account.Reserve2Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve2StartHour", account.Reserve2StartHour);
                    command.Parameters.AddWithValue("@Reserve2EndHour", account.Reserve2EndHour);
                    command.Parameters.AddWithValue("@Reserve2Count", account.Reserve2Count);
                    command.Parameters.AddWithValue("@Reserve3Enable", account.Reserve3Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve3StartHour", account.Reserve3StartHour);
                    command.Parameters.AddWithValue("@Reserve3EndHour", account.Reserve3EndHour);
                    command.Parameters.AddWithValue("@Reserve3Count", account.Reserve3Count);
                    command.Parameters.AddWithValue("@Reserve4Enable", account.Reserve4Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve4StartHour", account.Reserve4StartHour);
                    command.Parameters.AddWithValue("@Reserve4EndHour", account.Reserve4EndHour);
                    command.Parameters.AddWithValue("@Reserve4Count", account.Reserve4Count);
                    command.Parameters.AddWithValue("@PaidLike", account.PaidLike ? 1 : 0);
                    command.Parameters.AddWithValue("@PaidBookmark", account.PaidBookmark ? 1 : 0);

//                    command.ExecuteNonQuery();
                    int insertedId = Convert.ToInt32(command.ExecuteScalar());
                    return insertedId;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }

            return -1;
        }
    }

    public List<AccountMaster> GetAccountMaster(bool userEnable = false)
    {
        List<AccountMaster> accountMasterList = new List<AccountMaster>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT am.id,am.user_id,am.name,
                    am.login_id,am.login_password,
                    am.api_key,am.api_key_secret,
                    am.client_id,am.client_secret,
                    am.access_token,am.access_token_secret,
                    am.bearer_token,am.refresh_token,am.enable
                    ,am.like_enable,am.reply_enable,am.bookmark_enable,am.repost_enable,am.post_enable,am.paid
                    ,am.reserve1_enable,am.reserve1_start_hour,am.reserve1_end_hour,am.reserve1_count
                    ,am.reserve2_enable,am.reserve2_start_hour,am.reserve2_end_hour,am.reserve2_count
                    ,am.reserve3_enable,am.reserve3_start_hour,am.reserve3_end_hour,am.reserve3_count
                    ,am.reserve4_enable,am.reserve4_start_hour,am.reserve4_end_hour,am.reserve4_count
                    ,am.paid_like,am.paid_bookmark
                    ,am.check_interval
                    ,am.search_enable,am.vps_id,
                    um.GROQ_API_KEY,
                    um.OPENAI_API_KEY,
                    am.ai_mode,
                    am.ai_post_enable,
                    am.ai_reply_enable,
                    am.ai_post_prompt,
                    am.ai_reply_prompt,
                    am.reserve1_ai,
                    am.reserve2_ai,
                    am.reserve3_ai,
                    am.reserve4_ai
                    FROM account_master am
                    left join user_master um on um.id = am.user_id
                    ";

                if (userEnable)
                {
                    query += "where um.enable = '1';";
                }
                else
                {
                    query += ";";
                }

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            try
                            {
                                AccountMaster accountItem = new AccountMaster()
                                {
                                    Id = int.Parse(reader["id"].ToString()),
                                    UserId = int.Parse(reader["user_id"].ToString()),
                                    Name = reader["name"].ToString(),
                                    LoginId = reader["login_id"].ToString(),
                                    LoginPass = reader["login_password"].ToString(),
                                    ApiKey = reader["api_key"].ToString(),
                                    ApiKeySecret = reader["api_key_secret"].ToString(),
                                    ClientId = reader["client_id"].ToString(),
                                    ClientSecret = reader["client_secret"].ToString(),
                                    AccessToken = reader["access_token"].ToString(),
                                    AccessTokenSecret = reader["access_token_secret"].ToString(),
                                    BearerToken = reader["bearer_token"].ToString(),
                                    RefreshToken = reader["refresh_token"].ToString(),
                                    Enable = reader["enable"].ToString() == "1",
                                    LikeEnable = reader["like_enable"].ToString() == "1",
                                    ReplyEnable = reader["reply_enable"].ToString() == "1",
                                    BookMarkEnable = reader["bookmark_enable"].ToString() == "1",
                                    RepostEnable = reader["repost_enable"].ToString() == "1",
                                    PostEnable = reader["post_enable"].ToString() == "1",

                                    Reserve1Count = SupportUtil.ParseOrDefault(reader["reserve1_count"],0),
                                    Reserve2Count = SupportUtil.ParseOrDefault(reader["reserve2_count"], 0),
                                    Reserve3Count = SupportUtil.ParseOrDefault(reader["reserve3_count"], 0),
                                    Reserve4Count = SupportUtil.ParseOrDefault(reader["reserve4_count"], 0),
                                    Reserve1StartHour = SupportUtil.ParseOrDefault(reader["reserve1_start_hour"], 0),
                                    Reserve2StartHour = SupportUtil.ParseOrDefault(reader["reserve2_start_hour"], 0),
                                    Reserve3StartHour = SupportUtil.ParseOrDefault(reader["reserve3_start_hour"], 0),
                                    Reserve4StartHour = SupportUtil.ParseOrDefault(reader["reserve4_start_hour"], 0),
                                    Reserve1EndHour = SupportUtil.ParseOrDefault(reader["reserve1_end_hour"], 0),
                                    Reserve2EndHour = SupportUtil.ParseOrDefault(reader["reserve2_end_hour"], 0),
                                    Reserve3EndHour = SupportUtil.ParseOrDefault(reader["reserve3_end_hour"], 0),
                                    Reserve4EndHour = SupportUtil.ParseOrDefault(reader["reserve4_end_hour"], 0),
                                    Reserve1Enable = reader["reserve1_enable"].ToString() == "1",
                                    Reserve2Enable = reader["reserve2_enable"].ToString() == "1",
                                    Reserve3Enable = reader["reserve3_enable"].ToString() == "1",
                                    Reserve4Enable = reader["reserve4_enable"].ToString() == "1",
                                    Paid = reader["paid"].ToString() == "1",
                                    PaidLike = reader["paid_like"].ToString() == "1",
                                    PaidBookmark = reader["paid_bookmark"].ToString() == "1",


                                    CheckInterval = SupportUtil.ParseOrDefault(reader["check_interval"], 60),

                                    SearchEnable = reader["search_enable"].ToString() == "1",
                                    VpsId = SupportUtil.ParseOrDefault(reader["vps_id"], 0),

                                     GROQ_API_KEY = reader["GROQ_API_KEY"].ToString(),
                                    OPENAI_API_KEY = reader["GROQ_API_KEY"].ToString(),

                                    AiPostPrompt = reader["ai_post_prompt"].ToString(),
                                    AiReplyPrompt = reader["ai_reply_prompt"].ToString(),
                                    AiMode = SupportUtil.ParseOrDefault(reader["ai_mode"],0),
                                    AiPostEnable = reader["ai_post_enable"].ToString() == "1",
                                    AiReplyEnable = reader["ai_reply_enable"].ToString() == "1",

                                    Reserve1Ai = reader["reserve1_ai"].ToString() == "1",
                                    Reserve2Ai = reader["reserve2_ai"].ToString() == "1",
                                    Reserve3Ai = reader["reserve3_ai"].ToString() == "1",
                                    Reserve4Ai = reader["reserve4_ai"].ToString() == "1",



                                };

                                accountMasterList.Add(accountItem);

                            }
                            catch(Exception ex) 
                            {
                                Console.WriteLine("エラーが発生しました: " + ex.Message);
                            }
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return accountMasterList;
    }

    public void UpdateAccountMaster(AccountMaster account)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                UPDATE account_master 
                SET user_id = @UserId, 
                    name = @Name, 
                    login_id = @LoginId, 
                    login_password = @LoginPassword, 
                    api_key = @ApiKey, 
                    api_key_secret = @ApiKeySecret, 
                    client_id = @ClientId, 
                    client_secret = @ClientSecret, 
                    access_token = @AccessToken, 
                    access_token_secret = @AccessTokenSecret, 
                    bearer_token = @BearerToken, 
                    refresh_token = @RefreshToken, 
                    enable = @Enable, 
                    paid = @Paid, 
                    like_enable = @LikeEnable, 
                    reply_enable = @ReplyEnable, 
                    bookmark_enable = @BookmarkEnable, 
                    repost_enable = @RepostEnable, 
                    post_enable = @TweetEnable, 
                    reserve1_enable = @Reserve1Enable, 
                    reserve1_start_hour = @Reserve1StartHour, 
                    reserve1_end_hour = @Reserve1EndHour, 
                    reserve1_count = @Reserve1Count, 
                    reserve2_enable = @Reserve2Enable, 
                    reserve2_start_hour = @Reserve2StartHour, 
                    reserve2_end_hour = @Reserve2EndHour, 
                    reserve2_count = @Reserve2Count, 
                    reserve3_enable = @Reserve3Enable, 
                    reserve3_start_hour = @Reserve3StartHour, 
                    reserve3_end_hour = @Reserve3EndHour, 
                    reserve3_count = @Reserve3Count, 
                    reserve4_enable = @Reserve4Enable, 
                    reserve4_start_hour = @Reserve4StartHour, 
                    reserve4_end_hour = @Reserve4EndHour, 
                    reserve4_count = @Reserve4Count
                    ,paid_like = @PaidLike
                    ,paid_bookmark = @PaidBookmark
                    ,vps_id = @VpsId
                WHERE id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@Id", account.Id);
                    command.Parameters.AddWithValue("@UserId", account.UserId);
                    command.Parameters.AddWithValue("@Name", account.Name);
                    command.Parameters.AddWithValue("@LoginId", account.LoginId);
                    command.Parameters.AddWithValue("@LoginPassword", account.LoginPass);
                    command.Parameters.AddWithValue("@ApiKey", account.ApiKey);
                    command.Parameters.AddWithValue("@ApiKeySecret", account.ApiKeySecret);
                    command.Parameters.AddWithValue("@ClientId", account.ClientId);
                    command.Parameters.AddWithValue("@ClientSecret", account.ClientSecret);
                    command.Parameters.AddWithValue("@AccessToken", account.AccessToken);
                    command.Parameters.AddWithValue("@AccessTokenSecret", account.AccessTokenSecret);
                    command.Parameters.AddWithValue("@BearerToken", account.BearerToken);
                    command.Parameters.AddWithValue("@RefreshToken", account.RefreshToken);
                    command.Parameters.AddWithValue("@Enable", account.Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Paid", account.Paid ? 1 : 0);
                    command.Parameters.AddWithValue("@PaidLike", account.PaidLike ? 1 : 0);
                    command.Parameters.AddWithValue("@PaidBookmark", account.PaidBookmark ? 1 : 0);
                    command.Parameters.AddWithValue("@LikeEnable", account.LikeEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@ReplyEnable", account.ReplyEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@BookmarkEnable", account.BookMarkEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@RepostEnable", account.RepostEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@TweetEnable", account.PostEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve1Enable", account.Reserve1Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve1StartHour", account.Reserve1StartHour);
                    command.Parameters.AddWithValue("@Reserve1EndHour", account.Reserve1EndHour);
                    command.Parameters.AddWithValue("@Reserve1Count", account.Reserve1Count);
                    command.Parameters.AddWithValue("@Reserve2Enable", account.Reserve2Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve2StartHour", account.Reserve2StartHour);
                    command.Parameters.AddWithValue("@Reserve2EndHour", account.Reserve2EndHour);
                    command.Parameters.AddWithValue("@Reserve2Count", account.Reserve2Count);
                    command.Parameters.AddWithValue("@Reserve3Enable", account.Reserve3Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve3StartHour", account.Reserve3StartHour);
                    command.Parameters.AddWithValue("@Reserve3EndHour", account.Reserve3EndHour);
                    command.Parameters.AddWithValue("@Reserve3Count", account.Reserve3Count);
                    command.Parameters.AddWithValue("@Reserve4Enable", account.Reserve4Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve4StartHour", account.Reserve4StartHour);
                    command.Parameters.AddWithValue("@Reserve4EndHour", account.Reserve4EndHour);
                    command.Parameters.AddWithValue("@Reserve4Count", account.Reserve4Count);
                    command.Parameters.AddWithValue("@VpsId", account.VpsId);

                    command.ExecuteNonQuery();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
    }

    public bool DeleteAccountMaster(int accountId)
    {
        bool isDeleted = false;

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = "DELETE FROM account_master WHERE id = @AccountId;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@AccountId", accountId);

                    int rowsAffected = command.ExecuteNonQuery();

                    // 削除された行数が1以上で成功とみなす
                    isDeleted = rowsAffected > 0;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return isDeleted;
    }



    #endregion

    #region TweetProcessList
    public TweetProcessList GetTargetTweetProcess()
    {
        List<TweetProcessList> list = new List<TweetProcessList>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                    SELECT `tweet_process_list`.`id`,
                        `tweet_process_list`.`user_id`,
                        `tweet_process_list`.`updatetime`,
                        `tweet_process_list`.`tweet_id`,
                        `tweet_process_list`.`like_enable`,
                        `tweet_process_list`.`bookmark_enable`,
                        `tweet_process_list`.`reply_enable`,
                        `tweet_process_list`.`rep_to_rep`,
                        `tweet_process_list`.`repost_enable`,
                        `tweet_process_list`.`like_count`,
                        `tweet_process_list`.`jap_like_count`,
                        `tweet_process_list`.`bookmark_count`,
                        `tweet_process_list`.`reply_count`,
                        `tweet_process_list`.`repost_count`,
                        `tweet_process_list`.`sensyuken_mode`,
                        `tweet_process_list`.`dumplicate`,
                        `tweet_process_list`.`exe_follow`,
                        `tweet_process_list`.`exe_unfollow`,
                        `tweet_process_list`.`target_account_name`,
                        `tweet_process_list`.`exe_flag`
                    FROM tweet_process_list 
                    WHERE exe_flag = '0'
                    AND updatetime >= NOW() - INTERVAL 6 HOUR
                    ORDER BY updatetime

                    ";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {

                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            TweetProcessList item = new TweetProcessList()
                            {
                                Id = int.Parse(reader["id"].ToString()),
                                UserId = int.Parse(reader["user_id"].ToString()),
                                UpdateTime = Convert.ToDateTime(reader["updatetime"]),
                                TweetId = reader["tweet_id"].ToString(),
                                LikeEnable = reader["like_enable"].ToString() == "1",
                                BookmarkEnable = reader["bookmark_enable"].ToString() == "1",
                                ReplyEnable = reader["reply_enable"].ToString() == "1",
                                RepToRep = reader["rep_to_rep"].ToString() == "1",
                                RepostEnable = reader["repost_enable"].ToString() == "1",
                                LikeCount = SupportUtil.ParseOrDefault(reader["like_count"], 0),
                                JapLikeCount = SupportUtil.ParseOrDefault(reader["jap_like_count"], 0),
                                BookmarkCount = SupportUtil.ParseOrDefault(reader["bookmark_count"], 0),
                                RepostCount = SupportUtil.ParseOrDefault(reader["repost_count"], 0),
                                ReplyCount = SupportUtil.ParseOrDefault(reader["reply_count"], 0),
                                SensyukenMode = SupportUtil.ParseOrDefault(reader["sensyuken_mode"], 0),
                                Dumplicate = reader["dumplicate"].ToString() == "1",
                                ExeFollow = reader["exe_follow"].ToString() == "1",
                                ExeUnFollow = reader["exe_unfollow"].ToString() == "1",
                                TargetAccountName = reader["target_account_name"].ToString(),
                                ExeFlag = reader["exe_flag"].ToString() == "1",
                            };

                            list.Add(item);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return list.Count == 0 ? null : list.FirstOrDefault();
    }

    public void UpdateTweetProcess(TweetProcessList tweetProcess)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                UPDATE tweet_process_list SET 
                    user_id = @UserId,
                    updatetime = @UpdateTime,
                    tweet_id = @TweetId,
                    like_enable = @LikeEnable,
                    bookmark_enable = @BookmarkEnable,
                    reply_enable = @ReplyEnable,
                    repost_enable = @RepostEnable,
                    like_count = @LikeCount,
                    bookmark_count = @BookmarkCount,
                    reply_count = @ReplyCount,
                    repost_count = @RepostCount,
                    dumplicate = @Dumplicate,
                    exe_flag = @ExeFlag
                WHERE id = @Id";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", tweetProcess.UserId);
                    command.Parameters.AddWithValue("@UpdateTime", tweetProcess.UpdateTime);
                    command.Parameters.AddWithValue("@TweetId", tweetProcess.TweetId);
                    command.Parameters.AddWithValue("@LikeEnable", tweetProcess.LikeEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@BookmarkEnable", tweetProcess.BookmarkEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@ReplyEnable", tweetProcess.ReplyEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@RepostEnable", tweetProcess.RepostEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@LikeCount", tweetProcess.LikeCount);
                    command.Parameters.AddWithValue("@BookmarkCount", tweetProcess.BookmarkCount);
                    command.Parameters.AddWithValue("@ReplyCount", tweetProcess.ReplyCount);
                    command.Parameters.AddWithValue("@RepostCount", tweetProcess.RepostCount);
                    command.Parameters.AddWithValue("@Dumplicate", tweetProcess.Dumplicate ? 1 : 0);
                    command.Parameters.AddWithValue("@ExeFlag", tweetProcess.ExeFlag ? 1 : 0);
                    command.Parameters.AddWithValue("@Id", tweetProcess.Id);

                    int rowsAffected = command.ExecuteNonQuery();
                    if (rowsAffected == 0)
                    {
                        Console.WriteLine("更新対象のレコードが見つかりませんでした。");
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
    }


    #endregion TweetProcessList

    #region CheckAccountList

    public int InsertCheckAccountList(CheckAccountList account)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                INSERT INTO check_account_list 
                (
                    account_id, enable, mode, target_account_name
                )
                VALUES 
                (@AccountId, @Enable, @Mode, @TargetAccountName
                );
                SELECT LAST_INSERT_ID(); ";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
//                    command.Parameters.AddWithValue("@Id", account.Id);
                    command.Parameters.AddWithValue("@AccountId", account.AccountId);
                    command.Parameters.AddWithValue("@Enable", account.Enable ? "1" : "0");
                    command.Parameters.AddWithValue("@Mode", account.Mode.ToString());
                    command.Parameters.AddWithValue("@TargetAccountName", account.TargetAccountName);
                    command.Parameters.AddWithValue("@CheckAccountId", account.CheckAccountId);

                    //                    command.ExecuteNonQuery();
                    int insertedId = Convert.ToInt32(command.ExecuteScalar());
                    return insertedId;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }

            return -1;
        }
    }

    public List<CheckAccountList> GetCheckAccountList()
    {
        List<CheckAccountList> checkAccountList = new List<CheckAccountList>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT id ,account_id, enable, mode, target_account_name , check_account_id
                    FROM check_account_list
                    ";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {

                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            CheckAccountList accountItem = new CheckAccountList()
                            {
                                Id = int.Parse(reader["id"].ToString()),
                                AccountId = int.Parse(reader["account_id"].ToString()),
                                CheckAccountId = SupportUtil.ParseOrDefault(reader["check_account_id"], 0),
                                Mode = GetTweetProcType(reader["mode"].ToString()),
                                TargetAccountName = reader["target_account_name"].ToString().Replace("@",""),
                                Enable = reader["enable"].ToString() == "1",
                            };

                            checkAccountList.Add(accountItem);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return checkAccountList;
    }

    public void UpdateCheckAccountList(CheckAccountList item)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                UPDATE check_account_list 
                SET account_id = @AccountId, 
                    enable = @Enable, 
                    mode = @Mode, 
                    target_account_name = @TargetAccountName ,
                    check_account_id = @CheckAccountId 
                WHERE id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@Id", item.Id);
                    command.Parameters.AddWithValue("@AccountId", item.AccountId);
                    command.Parameters.AddWithValue("@Enable", item.Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Mode", item.Mode.ToString());
                    command.Parameters.AddWithValue("@TargetAccountName", item.TargetAccountName);
                    command.Parameters.AddWithValue("@CheckAccountId", item.CheckAccountId);

                    command.ExecuteNonQuery();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
    }

    public bool DeleteCheckAccountList(int id)
    {
        bool isDeleted = false;

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = "DELETE FROM check_account_list WHERE id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@Id", id);

                    int rowsAffected = command.ExecuteNonQuery();

                    // 削除された行数が1以上で成功とみなす
                    isDeleted = rowsAffected > 0;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return isDeleted;
    }



    #endregion

    #region SearchList

    public int InsertSearchList(SearchList search)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
            INSERT INTO search_list 
            (
                search_user_name, search_user_id, enable,  
                post_account_id, post_enable, last_post_id, last_post_time, 
                reply_account_id, reply_enable, last_reply_id, last_reply_time, 
                monomane_account_id, monomane_enable, last_monomane_id, last_monomane_time
            )
            VALUES 
            (
                @SearchUserName, @SearchUserId, @Enable ,  
                @PostAccountId, @PostEnable, @LastPostId, @LastPostTime, 
                @ReplyAccountId, @ReplyEnable, @LastReplyId, @LastReplyTime, 
                @MonomaneAccountId, @MonomaneEnable, @LastMonomaneId, @LastMonomaneTime
            );
            SELECT LAST_INSERT_ID();";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    // パラメータの設定
                    command.Parameters.AddWithValue("@SearchUserName", search.SearchUserName);
                    command.Parameters.AddWithValue("@SearchUserId", search.SearchUserId);
                    command.Parameters.AddWithValue("@Enable", search.Enable.HasValue ? (search.Enable.Value ? "1" : "0") : null);
                    command.Parameters.AddWithValue("@PostAccountId", search.PostAccountId);
                    command.Parameters.AddWithValue("@PostEnable", search.PostEnable.HasValue ? (search.PostEnable.Value ? "1" : "0") : null);
                    command.Parameters.AddWithValue("@LastPostId", search.LastPostId);
                    command.Parameters.AddWithValue("@LastPostTime", search.LastPostTime?.ToString("yyyy-MM-dd HH:mm:ss"));
                    command.Parameters.AddWithValue("@ReplyAccountId", search.ReplyAccountId);
                    command.Parameters.AddWithValue("@ReplyEnable", search.ReplyEnable.HasValue ? (search.ReplyEnable.Value ? "1" : "0") : null);
                    command.Parameters.AddWithValue("@LastReplyId", search.LastReplyId);
                    command.Parameters.AddWithValue("@LastReplyTime", search.LastReplyTime?.ToString("yyyy-MM-dd HH:mm:ss"));
                    command.Parameters.AddWithValue("@MonomaneAccountId", search.MonomaneAccountId);
                    command.Parameters.AddWithValue("@MonomaneEnable", search.MonomaneEnable.HasValue ? (search.MonomaneEnable.Value ? "1" : "0") : null);
                    command.Parameters.AddWithValue("@LastMonomaneId", search.LastMonomaneId);
                    command.Parameters.AddWithValue("@LastMonomaneTime", search.LastMonomaneTime?.ToString("yyyy-MM-dd HH:mm:ss"));

                    // クエリを実行して挿入されたIDを取得
                    int insertedId = Convert.ToInt32(command.ExecuteScalar());
                    return insertedId;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }

            return -1;
        }
    }


    public List<SearchList> GetSearchList()
    {
        List<SearchList> searchList = new List<SearchList>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                SELECT 
                    sl.id,
                    sl.enable,
                    sl.search_user_name,
                    sl.search_user_id, 
                    sl.post_account_id,
                    sl.post_enable,
                    sl.last_post_id,
                    sl.last_post_time,
                    sl.reply_account_id,
                    sl.reply_enable,
                    sl.last_reply_id, 
                    sl.last_reply_time,
                    sl.monomane_account_id,
                    sl.monomane_enable,
                    sl.last_monomane_id,
                    sl.last_monomane_time,
                    sl.time_enable ,
                    sl.start_hour ,
                    sl.end_hour ,
                    um.searchrep_enable
                FROM search_list sl
                LEFT JOIN user_master um on um.id = sl.search_user_id
";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            SearchList searchItem = new SearchList()
                            {
                                Id = reader["id"] != DBNull.Value ? Convert.ToInt32(reader["id"]) : 0,
                                Enable = reader["enable"] != DBNull.Value ? reader["enable"].ToString() == "1" : (bool?)null,
                                SearchUserName = reader["search_user_name"].ToString(),
                                SearchUserId = reader["search_user_id"] != DBNull.Value ? Convert.ToInt32(reader["search_user_id"]) : 0,
                                PostAccountId = reader["post_account_id"] != DBNull.Value ? Convert.ToInt32(reader["post_account_id"]) : 0,
                                PostEnable = reader["post_enable"] != DBNull.Value ? reader["post_enable"].ToString() == "1" : (bool?)null,
                                LastPostId = reader["last_post_id"].ToString(),
                                LastPostTime = reader["last_post_time"] != DBNull.Value
                                    ? DateTime.Parse(reader["last_post_time"].ToString())
                                    : (DateTime?)null,
                                ReplyAccountId = reader["reply_account_id"] != DBNull.Value ? Convert.ToInt32(reader["reply_account_id"]) : 0,
                                ReplyEnable = reader["reply_enable"] != DBNull.Value ? reader["reply_enable"].ToString() == "1" : (bool?)null,
                                LastReplyId = reader["last_reply_id"].ToString(),
                                LastReplyTime = reader["last_reply_time"] != DBNull.Value
                                    ? DateTime.Parse(reader["last_reply_time"].ToString())
                                    : (DateTime?)null,
                                MonomaneAccountId = reader["monomane_account_id"] != DBNull.Value ? Convert.ToInt32(reader["monomane_account_id"]) : 0,
                                MonomaneEnable = reader["monomane_enable"] != DBNull.Value ? reader["monomane_enable"].ToString() == "1" : (bool?)null,
                                LastMonomaneId = reader["last_monomane_id"].ToString(),
                                LastMonomaneTime = reader["last_monomane_time"] != DBNull.Value
                                    ? DateTime.Parse(reader["last_monomane_time"].ToString())
                                    : (DateTime?)null,
                                TimeEnable = reader["time_enable"] != DBNull.Value ? reader["time_enable"].ToString() == "1" : (bool?)null,
                                StartHour = reader["start_hour"] != DBNull.Value ? Convert.ToInt32(reader["start_hour"]) : 0,
                                EndHour = reader["end_hour"] != DBNull.Value ? Convert.ToInt32(reader["end_hour"]) : 0,
                            };

                            // 2025.04.03 コメントアウト
                            /*
                            // ユーザー設定で監視向こうの場合はフラグをOFFに固定
                            if( (reader["searchrep_enable"] != DBNull.Value ? reader["searchrep_enable"].ToString() == "1" : false ) == false)
                            {
                                searchItem.PostEnable = false;
                                searchItem.ReplyEnable = false;
                            }
                            */

                            searchList.Add(searchItem);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return searchList;
    }


    public void UpdateSearchList(SearchList item)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                UPDATE search_list 
                SET 
                    search_user_name = @SearchUserName,
                    search_user_id = @SearchUserId,
                    enable = @ Enable,
                    post_account_id = @PostAccountId,
                    post_enable = @PostEnable,
                    last_post_id = @LastPostId,
                    last_post_time = @LastPostTime,
                    reply_account_id = @ReplyAccountId,
                    reply_enable = @ReplyEnable,
                    last_reply_id = @LastReplyId,
                    last_reply_time = @LastReplyTime,
                    monomane_account_id = @MonomaneAccountId,
                    monomane_enable = @MonomaneEnable,
                    last_monomane_id = @LastMonomaneId,
                    last_monomane_time = @LastMonomaneTime
                WHERE id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@Id", item.Id);
                    command.Parameters.AddWithValue("@SearchUserName", item.SearchUserName ?? (object)DBNull.Value);
                    command.Parameters.AddWithValue("@SearchUserId", item.SearchUserId != 0 ? item.SearchUserId : (object)DBNull.Value);
                    command.Parameters.AddWithValue("@Enable", item.Enable.HasValue ? (item.Enable.Value ? 1 : 0) : (object)DBNull.Value);
                    command.Parameters.AddWithValue("@PostAccountId", item.PostAccountId != 0 ? item.PostAccountId : (object)DBNull.Value);
                    command.Parameters.AddWithValue("@PostEnable", item.PostEnable.HasValue ? (item.PostEnable.Value ? 1 : 0) : (object)DBNull.Value);
                    command.Parameters.AddWithValue("@LastPostId", item.LastPostId ?? (object)DBNull.Value);
                    command.Parameters.AddWithValue("@LastPostTime", item.LastPostTime.HasValue ? item.LastPostTime.Value.ToString("yyyy-MM-dd HH:mm:ss") : (object)DBNull.Value);
                    command.Parameters.AddWithValue("@ReplyAccountId", item.ReplyAccountId != 0 ? item.ReplyAccountId : (object)DBNull.Value);
                    command.Parameters.AddWithValue("@ReplyEnable", item.ReplyEnable.HasValue ? (item.ReplyEnable.Value ? 1 : 0) : (object)DBNull.Value);
                    command.Parameters.AddWithValue("@LastReplyId", item.LastReplyId ?? (object)DBNull.Value);
                    command.Parameters.AddWithValue("@LastReplyTime", item.LastReplyTime.HasValue ? item.LastReplyTime.Value.ToString("yyyy-MM-dd HH:mm:ss") : (object)DBNull.Value);
                    command.Parameters.AddWithValue("@MonomaneAccountId", item.MonomaneAccountId != 0 ? item.MonomaneAccountId : (object)DBNull.Value);
                    command.Parameters.AddWithValue("@MonomaneEnable", item.MonomaneEnable.HasValue ? (item.MonomaneEnable.Value ? 1 : 0) : (object)DBNull.Value);
                    command.Parameters.AddWithValue("@LastMonomaneId", item.LastMonomaneId ?? (object)DBNull.Value);
                    command.Parameters.AddWithValue("@LastMonomaneTime", item.LastMonomaneTime.HasValue ? item.LastMonomaneTime.Value.ToString("yyyy-MM-dd HH:mm:ss") : (object)DBNull.Value);

                    command.ExecuteNonQuery();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
    }


    public bool DeleteSearchList(int id)
    {
        bool isDeleted = false;

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = "DELETE FROM search_list WHERE id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@Id", id);

                    int rowsAffected = command.ExecuteNonQuery();

                    // 削除された行数が1以上で成功とみなす
                    isDeleted = rowsAffected > 0;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return isDeleted;
    }



    #endregion


    #region CheckUserMaster

    public int InsertCheckUserMaster(CheckUserMaster row)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                INSERT INTO check_user_master 
                (
                    user_name, user_id, update_time
                )
                VALUES 
                (@UserName, @UserId, @UpdateTime
                );
                SELECT LAST_INSERT_ID(); ";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    //                    command.Parameters.AddWithValue("@Id", account.Id);
                    command.Parameters.AddWithValue("@UserName", row.UserName);
                    command.Parameters.AddWithValue("@UserId", row.UserId);
                    command.Parameters.AddWithValue("@UpdateTime", row.UpdateTime);

                    //                    command.ExecuteNonQuery();
                    int insertedId = Convert.ToInt32(command.ExecuteScalar());
                    return insertedId;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }

            return -1;
        }
    }

    public List<CheckUserMaster> GetCheckUserMaster()
    {
        List<CheckUserMaster> checkAccountList = new List<CheckUserMaster>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT id ,user_name, user_id, update_time
                    FROM check_user_master
                    ";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {

                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            CheckUserMaster accountItem = new CheckUserMaster()
                            {
                                Id = int.Parse(reader["id"].ToString()),
                                UserName = reader["user_name"].ToString(),
                                UserId = reader["user_id"].ToString(),
                            };

                            checkAccountList.Add(accountItem);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return checkAccountList;
    }

    public void UpdateCheckUserMaster(CheckUserMaster item)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                UPDATE check_user_master 
                SET user_name = @UserName, 
                    user_id = @UserId 
                WHERE id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserName", item.UserName);
                    command.Parameters.AddWithValue("@UserId", item.UserId);
                    command.Parameters.AddWithValue("@Id", item.Id);

                    command.ExecuteNonQuery();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
    }

    public bool DeleteCheckUserMaster(int id)
    {
        bool isDeleted = false;

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = "DELETE FROM check_user_master WHERE id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@Id", id);

                    int rowsAffected = command.ExecuteNonQuery();

                    // 削除された行数が1以上で成功とみなす
                    isDeleted = rowsAffected > 0;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return isDeleted;
    }



    #endregion


    #region CommentMaster

    public List<CommentMaster> GetCommentMaster()
    {
        List<CommentMaster> commentMasterList = new List<CommentMaster>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT id,user_id,
                        account_id,comment,enable , chatgpt , mode , photo_enable , movie_enable, reserve_mode
                        FROM comment_master;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            CommentMaster commentItem = new CommentMaster()
                            {
                                Id = int.Parse(reader["id"].ToString()),
                                UserId = int.Parse(reader["user_id"].ToString()),
                                AccountId = int.Parse(reader["account_id"].ToString()),
                                PhotoEnable = reader["photo_enable"].ToString() == "1",
                                MovieEnable = reader["movie_enable"].ToString() == "1",
//                                MovieId = int.Parse(reader["movie_id"].ToString()),
//                                PhotoId = int.Parse(reader["photo_id"].ToString()),
                                Comment = reader["comment"].ToString(),
                                Enable = reader["enable"].ToString() == "1",
                                ChatGpt = reader["chatgpt"].ToString() == "1",
                                TweetModeType = reader["mode"].ToString() == "post" ? TweetModeTypes.Post : reader["mode"].ToString() == "reply" ? TweetModeTypes.Replay : TweetModeTypes.ReplyToReply,
                                ReserveMode = SupportUtil.ParseOrDefault(reader["reserve_mode"], 0),
                            };

                            commentMasterList.Add(commentItem);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return commentMasterList;
    }

    public List<CommentMaster> GetCommentMasterByAccountId(int accountId)
    {
        List<CommentMaster> retList = new List<CommentMaster>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT id,user_id,
                        account_id,comment,enable , chatgpt , mode , photo_enable , movie_enable , reserve_mode
                        FROM comment_master where account_id = @AccountId;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@AccountId", accountId);

                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            CommentMaster commentItem = new CommentMaster()
                            {
                                Id = int.Parse(reader["id"].ToString()),
                                UserId = int.Parse(reader["user_id"].ToString()),
                                AccountId = int.Parse(reader["account_id"].ToString()),
                                PhotoEnable = reader["photo_enable"].ToString() == "1",
                                MovieEnable = reader["movie_enable"].ToString() == "1",
//                                MovieId = int.Parse(reader["movie_id"].ToString()),
//                                PhotoId = int.Parse(reader["photo_id"].ToString()),
                                Comment = reader["comment"].ToString(),
                                Enable = reader["enable"].ToString() == "1",
                                ChatGpt = reader["chatgpt"].ToString() == "1",
                                TweetModeType = reader["mode"].ToString() == "post" ? TweetModeTypes.Post : reader["mode"].ToString() == "reply" ? TweetModeTypes.Replay : TweetModeTypes.ReplyToReply,
                                ReserveMode = SupportUtil.ParseOrDefault(reader["reserve_mode"], 0),
                            };

                            retList.Add(commentItem);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }

        }

        return retList;
    }

    public CommentMaster GetCommentMaster(int commentId)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT id,user_id,
                        account_id,comment,enable , chatgpt , mode , photo_enable , movie_enable, reserve_mode
                        FROM comment_master where id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@Id", commentId);

                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            CommentMaster commentItem = new CommentMaster()
                            {
                                Id = int.Parse(reader["id"].ToString()),
                                UserId = int.Parse(reader["user_id"].ToString()),
                                AccountId = int.Parse(reader["account_id"].ToString()),
                                PhotoEnable = reader["photo_enable"].ToString() == "1",
                                MovieEnable = reader["movie_enable"].ToString() == "1",
                                Comment = reader["comment"].ToString(),
                                Enable = reader["enable"].ToString() == "1",
                                ChatGpt = reader["chatgpt"].ToString() == "1",
                                TweetModeType = reader["mode"].ToString() == "post" ? TweetModeTypes.Post : reader["mode"].ToString() == "reply" ? TweetModeTypes.Replay : TweetModeTypes.ReplyToReply,
                                ReserveMode = SupportUtil.ParseOrDefault(reader["reserve_mode"], 0),
                            };

                            return commentItem;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }

        }

        return null;
    }

    public bool UpdateCommentMaster(CommentMaster commentMaster)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"UPDATE comment_master 
                             SET user_id = @UserId,
                                 account_id = @AccountId,
                                 comment = @Comment,
                                 chatgpt = @Chatgpt,
                                 mode = @Mode,
                                 enable = @Enable,
                                 photo_enable = @PhotoEnable,
                                 movie_enable = @MovieEnable,
                                 reserve_mode = @ReserveMode
                             WHERE id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", commentMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", commentMaster.AccountId);
                    command.Parameters.AddWithValue("@Comment", commentMaster.Comment);
                    command.Parameters.AddWithValue("@Chatgpt", commentMaster.ChatGpt ? 1 : 0);
                    command.Parameters.AddWithValue("@Enable", commentMaster.Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Id", commentMaster.Id);
                    command.Parameters.AddWithValue("@PhotoEnable", commentMaster.PhotoEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@MovieEnable", commentMaster.MovieEnable ? 1 : 0);
                    //                    command.Parameters.AddWithValue("@PhotoId", commentMaster.PhotoId);
                    //                    command.Parameters.AddWithValue("@MovieId", commentMaster.MovieId);
                    command.Parameters.AddWithValue("@Mode", commentMaster.TweetModeType == TweetModeTypes.Post ? "post" : commentMaster.TweetModeType == TweetModeTypes.Replay ? "reply" : "replytoreply");
                    command.Parameters.AddWithValue("@ReserveMode", commentMaster.ReserveMode);

                    int rowsAffected = command.ExecuteNonQuery();
                    return rowsAffected > 0;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
        return false;
    }

    public int InsertCommentMaster(CommentMaster commentMaster)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"INSERT INTO comment_master (user_id, account_id, comment, enable, chatgpt , mode , photo_enable , movie_enable, reserve_mode) 
                             VALUES (@UserId, @AccountId, @Comment, @Enable, @Chatgpt, @Mode , @PhotoEnable , @MovieEnable , @ReserveMode);
                            SELECT LAST_INSERT_ID(); ";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", commentMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", commentMaster.AccountId);
                    command.Parameters.AddWithValue("@Comment", commentMaster.Comment);
                    command.Parameters.AddWithValue("@Enable", commentMaster.Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Chatgpt", commentMaster.ChatGpt ? 1 : 0);
                    command.Parameters.AddWithValue("@Mode", commentMaster.TweetModeType == TweetModeTypes.Post ? "post" : commentMaster.TweetModeType == TweetModeTypes.Replay ? "reply" : "replytoreply");
                    command.Parameters.AddWithValue("@PhotoEnable", commentMaster.PhotoEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@MovieEnable", commentMaster.MovieEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@ReserveMode", commentMaster.ReserveMode);

                    int insertedId = Convert.ToInt32(command.ExecuteScalar());
                    return insertedId;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
        return -1; // エラー時は -1 を返す
    }

    public bool DeleteCommentMaster(int commentId)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"DELETE FROM comment_master WHERE id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@Id", commentId);

                    int rowsAffected = command.ExecuteNonQuery();
                    return rowsAffected > 0;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
        return false;
    }


    #endregion

    public List<UserMaster> GetUserMaster()
    {
        List<UserMaster> userList = new List<UserMaster>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = "SELECT id, username , password , admin , enable ,memo , " +
                    "like_enable,bookmark_enable,reply_enable,repost_enable,sensyuken_mode,post_enable,reserve_enable,media_enable,check_enable,searchrep_enable" +
                    " FROM user_master;";
                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            UserMaster user = new UserMaster
                            {
                                Id = Convert.ToInt32(reader["id"]),
                                Name = reader["username"].ToString(),
                                Password = reader["password"].ToString(),
                                Admin = reader["admin"].ToString() == "1",
                                Enable = reader["enable"].ToString() == "1",
                                Memo = reader["memo"].ToString(),
                                LikeEnable = reader["like_enable"].ToString() == "1",
                                BookmarkEnable = reader["bookmark_enable"].ToString() == "1",
                                ReplyEnable = reader["reply_enable"].ToString() == "1",
                                RepostEnable = reader["repost_enable"].ToString() == "1",
                                SensyukenEnable = reader["sensyuken_mode"].ToString() == "1",
                                PostEnable = reader["post_enable"].ToString() == "1",
                                ReserveEnable = reader["reserve_enable"].ToString() == "1",
                                MediaEnable = reader["media_enable"].ToString() == "1",
                                CheckEnable = reader["check_enable"].ToString() == "1",
                                SearchRepEnable = reader["searchrep_enable"].ToString() == "1",
                            };

                            userList.Add(user);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return userList;
    }

    #region ReserveMaster

    public void InsertReserveMaster(ReserveMaster reserveMaster)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                INSERT INTO reserve_master 
                (user_id,account_id, reserve1_enable, reserve2_enable, reserve3_enable, 
                 reserve1_start_hour, reserve2_start_hour, reserve3_start_hour, 
                 reserve1_end_hour, reserve2_end_hour, reserve3_end_hour, 
                 reserve1_count, reserve2_count, reserve3_count
                 ,reserve4_enable,reserve4_start_hour,reserve4_end_hour,reserve4_count) 
                VALUES 
                (@UserId, @AccountId, @Reserve1Enable, @Reserve2Enable, @Reserve3Enable, 
                 @Reserve1StartHour, @Reserve2StartHour, @Reserve3StartHour, 
                 @Reserve1EndHour, @Reserve2EndHour, @Reserve3EndHour, 
                 @Reserve1Count, @Reserve2Count, @Reserve3Count
                 ,@Reserve4Enable, @Reserve4StartHour, @Reserve4EndHour, @Reserve4Count
                  );";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", reserveMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", reserveMaster.AccountId);
                    command.Parameters.AddWithValue("@Reserve1Enable", reserveMaster.Reserve1Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve2Enable", reserveMaster.Reserve2Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve3Enable", reserveMaster.Reserve3Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve4Enable", reserveMaster.Reserve4Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve1StartHour", reserveMaster.Reserve1StartHour);
                    command.Parameters.AddWithValue("@Reserve2StartHour", reserveMaster.Reserve2StartHour);
                    command.Parameters.AddWithValue("@Reserve3StartHour", reserveMaster.Reserve3StartHour);
                    command.Parameters.AddWithValue("@Reserve4StartHour", reserveMaster.Reserve4StartHour);
                    command.Parameters.AddWithValue("@Reserve1EndHour", reserveMaster.Reserve1EndHour);
                    command.Parameters.AddWithValue("@Reserve2EndHour", reserveMaster.Reserve2EndHour);
                    command.Parameters.AddWithValue("@Reserve3EndHour", reserveMaster.Reserve3EndHour);
                    command.Parameters.AddWithValue("@Reserve4EndHour", reserveMaster.Reserve4EndHour);
                    command.Parameters.AddWithValue("@Reserve1Count", reserveMaster.Reserve1Count);
                    command.Parameters.AddWithValue("@Reserve2Count", reserveMaster.Reserve2Count);
                    command.Parameters.AddWithValue("@Reserve3Count", reserveMaster.Reserve3Count);
                    command.Parameters.AddWithValue("@Reserve4Count", reserveMaster.Reserve4Count);

                    command.ExecuteNonQuery();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
    }


    public ReserveMaster GetReserveMaster(int accountId)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT user_id , id,reserve1_enable,reserve2_enable,reserve3_enable,
                        reserve1_start_hour,reserve2_start_hour,reserve3_start_hour,
                        reserve1_end_hour,reserve2_end_hour,reserve3_end_hour,
                        reserve1_count,reserve2_count,reserve3_count
                        ,reserve4_enable,reserve4_start_hour,reserve4_end_hour,reserve4_count
                        FROM account_master where id = @AccountId;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@AccountId", accountId);

                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            ReserveMaster reserveItem = new ReserveMaster()
                            {
                                UserId = int.Parse(reader["user_id"].ToString()),
                                AccountId = int.Parse(reader["id"].ToString()),
                                Reserve1Count = SupportUtil.ParseOrDefault(reader["reserve1_count"], 0),
                                Reserve2Count = SupportUtil.ParseOrDefault(reader["reserve2_count"], 0),
                                Reserve3Count = SupportUtil.ParseOrDefault(reader["reserve3_count"], 0),
                                Reserve4Count = SupportUtil.ParseOrDefault(reader["reserve4_count"], 0),
                                Reserve1StartHour = SupportUtil.ParseOrDefault(reader["reserve1_start_hour"], 0),
                                Reserve2StartHour = SupportUtil.ParseOrDefault(reader["reserve2_start_hour"], 0),
                                Reserve3StartHour = SupportUtil.ParseOrDefault(reader["reserve3_start_hour"], 0),
                                Reserve4StartHour = SupportUtil.ParseOrDefault(reader["reserve4_start_hour"], 0),
                                Reserve1EndHour = SupportUtil.ParseOrDefault(reader["reserve1_end_hour"], 0),
                                Reserve2EndHour = SupportUtil.ParseOrDefault(reader["reserve2_end_hour"], 0),
                                Reserve3EndHour = SupportUtil.ParseOrDefault(reader["reserve3_end_hour"], 0),
                                Reserve4EndHour = SupportUtil.ParseOrDefault(reader["reserve4_end_hour"], 0),
                                Reserve1Enable = reader["reserve1_enable"].ToString() == "1",
                                Reserve2Enable = reader["reserve2_enable"].ToString() == "1",
                                Reserve3Enable = reader["reserve3_enable"].ToString() == "1",
                                Reserve4Enable = reader["reserve4_enable"].ToString() == "1",
                            };

                            return reserveItem;
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }

        }

        return null;
    }

    public void UpdateReserveMaster(ReserveMaster reserveMaster)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                UPDATE account_master 
                SET 
                    reserve1_enable = @Reserve1Enable,
                    reserve2_enable = @Reserve2Enable,
                    reserve3_enable = @Reserve3Enable,
                    reserve4_enable = @Reserve4Enable,
                    reserve1_start_hour = @Reserve1StartHour,
                    reserve2_start_hour = @Reserve2StartHour,
                    reserve3_start_hour = @Reserve3StartHour,
                    reserve4_start_hour = @Reserve4StartHour,
                    reserve1_end_hour = @Reserve1EndHour,
                    reserve2_end_hour = @Reserve2EndHour,
                    reserve3_end_hour = @Reserve3EndHour,
                    reserve4_end_hour = @Reserve4EndHour,
                    reserve1_count = @Reserve1Count,
                    reserve2_count = @Reserve2Count,
                    reserve3_count = @Reserve3Count,
                    reserve4_count = @Reserve4Count
                WHERE account_id = @AccountId;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", reserveMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", reserveMaster.AccountId);
                    command.Parameters.AddWithValue("@Reserve1Enable", reserveMaster.Reserve1Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve2Enable", reserveMaster.Reserve2Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve3Enable", reserveMaster.Reserve3Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve4Enable", reserveMaster.Reserve4Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve1StartHour", reserveMaster.Reserve1StartHour);
                    command.Parameters.AddWithValue("@Reserve2StartHour", reserveMaster.Reserve2StartHour);
                    command.Parameters.AddWithValue("@Reserve3StartHour", reserveMaster.Reserve3StartHour);
                    command.Parameters.AddWithValue("@Reserve4StartHour", reserveMaster.Reserve4StartHour);
                    command.Parameters.AddWithValue("@Reserve1EndHour", reserveMaster.Reserve1EndHour);
                    command.Parameters.AddWithValue("@Reserve2EndHour", reserveMaster.Reserve2EndHour);
                    command.Parameters.AddWithValue("@Reserve3EndHour", reserveMaster.Reserve3EndHour);
                    command.Parameters.AddWithValue("@Reserve4EndHour", reserveMaster.Reserve4EndHour);
                    command.Parameters.AddWithValue("@Reserve1Count", reserveMaster.Reserve1Count);
                    command.Parameters.AddWithValue("@Reserve2Count", reserveMaster.Reserve2Count);
                    command.Parameters.AddWithValue("@Reserve3Count", reserveMaster.Reserve3Count);
                    command.Parameters.AddWithValue("@Reserve4Count", reserveMaster.Reserve4Count);

                    command.ExecuteNonQuery();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
    }




    #endregion

    private int? GetIntValue(object value)
    {
        if (value == null) return null;

        if (value.ToString() == string.Empty) return null;

        return int.Parse(value.ToString());
    }

    #region MediaMaster

    public List<MediaMaster> GetMediaMaster()
    {
        List<MediaMaster> mediaMasterList = new List<MediaMaster>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT comment_id , media_id, user_id,
                        account_id, name, register_date , media_type
                        FROM media_master;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            MediaMaster mediaMaster = new MediaMaster()
                            {
                                CommentId = GetIntValue(reader["comment_id"]),// int.Parse(reader["comment_id"].ToString()),
                                MediaId = GetIntValue(reader["media_id"]),
                                UserId = GetIntValue(reader["user_id"]),
                                AccountId = GetIntValue(reader["account_id"]),
                                Name = reader["name"].ToString(),
                                MediaType = reader["media_type"].ToString() == "photo" ? MediaTypes.Photo : MediaTypes.Movie
                            };

                            mediaMasterList.Add(mediaMaster);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return mediaMasterList;
    }

    public void InsertMediaMaster(MediaMaster mediaMaster)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"INSERT INTO media_master (comment_id , media_id, user_id, account_id, name, register_date, media_type) 
                             VALUES (@CommentId , @MediaId, @UserId, @AccountId, @Name, @RegisterDate, @MediaType);";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@CommentId", mediaMaster.CommentId);
                    command.Parameters.AddWithValue("@MediaId", mediaMaster.MediaId);
                    command.Parameters.AddWithValue("@UserId", mediaMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", mediaMaster.AccountId);
                    command.Parameters.AddWithValue("@Name", mediaMaster.Name);
                    command.Parameters.AddWithValue("@RegisterDate", mediaMaster.RegisterDate);
                    command.Parameters.AddWithValue("@MediaType", mediaMaster.MediaType == MediaTypes.Photo ? "photo" : "movie");

                    command.ExecuteNonQuery();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
    }

    public void UpdateMediaMaster(MediaMaster mediaMaster)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"UPDATE media_master 
                             SET comment_id = @CommentId , user_id = @UserId, account_id = @AccountId, name = @Name, 
                                 register_date = @RegisterDate, media_type = @MediaType
                             WHERE media_id = @MediaId;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@CommentId", mediaMaster.CommentId);
                    command.Parameters.AddWithValue("@MediaId", mediaMaster.MediaId);
                    command.Parameters.AddWithValue("@UserId", mediaMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", mediaMaster.AccountId);
                    command.Parameters.AddWithValue("@Name", mediaMaster.Name);
                    command.Parameters.AddWithValue("@RegisterDate", mediaMaster.RegisterDate);
                    command.Parameters.AddWithValue("@MediaType", mediaMaster.MediaType == MediaTypes.Photo ? "photo" : "movie");

                    command.ExecuteNonQuery();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
    }

    public void DeleteMediaMaster(int mediaId)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"DELETE FROM media_master WHERE media_id = @MediaId;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@MediaId", mediaId);

                    command.ExecuteNonQuery();
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }
    }

    #endregion

    #region ReserveSchedule

    public List<ReserveSchedule> GetReserveSchedules()
    {
        List<ReserveSchedule> reserveSchedules = new List<ReserveSchedule>();
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();
                string query = @"SELECT reserve_date, reserve_time, account_id, comment_id, result, reserve_id 
                             FROM reserve_schedule;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                using (MySqlDataReader reader = command.ExecuteReader())
                {
                    while (reader.Read())
                    {
                        reserveSchedules.Add(new ReserveSchedule
                        {
                            ReserveDate = reader["reserve_date"] as DateTime?,
                            ReserveTime = reader["reserve_time"] as DateTime?,
                            AccountId = reader["account_id"] as int?,
                            CommentId = reader["comment_id"] as int?,
                            Result = reader["result"]?.ToString() == "1",
                            ReserveId = reader["reserve_id"]?.ToString()
                        });
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラー: " + ex.Message);
            }
        }

        return reserveSchedules;
    }

    public int InsertReserveSchedule(ReserveSchedule schedule)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();
                string query = @"INSERT INTO reserve_schedule 
                             (reserve_date, reserve_time, account_id, comment_id, result, reserve_id) 
                             VALUES (@ReserveDate, @ReserveTime, @AccountId, @CommentId, @Result, @ReserveId);
                            SELECT LAST_INSERT_ID(); ";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@ReserveDate", schedule.ReserveDate);
                    command.Parameters.AddWithValue("@ReserveTime", schedule.ReserveTime);
                    command.Parameters.AddWithValue("@AccountId", schedule.AccountId);
                    command.Parameters.AddWithValue("@CommentId", schedule.CommentId);
                    command.Parameters.AddWithValue("@Result", schedule.Result ? "1" : "0");
                    command.Parameters.AddWithValue("@ReserveId", schedule.ReserveId);

                    int insertedId = Convert.ToInt32(command.ExecuteScalar());
                    return insertedId;
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラー: " + ex.Message);
                return -1;
            }

            return -1;
        }
    }

    public bool UpdateReserveSchedule(ReserveSchedule schedule)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();
                string query = @"UPDATE reserve_schedule 
                             SET reserve_date = @ReserveDate,
                                 reserve_time = @ReserveTime,
                                 comment_id = @CommentId,
                                 result = @Result
                             WHERE account_id = @AccountId 
                               AND reserve_id = @ReserveId;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@ReserveDate", schedule.ReserveDate);
                    command.Parameters.AddWithValue("@ReserveTime", schedule.ReserveTime);
                    command.Parameters.AddWithValue("@CommentId", schedule.CommentId);
                    command.Parameters.AddWithValue("@Result", schedule.Result ? "1" : "0");
                    command.Parameters.AddWithValue("@AccountId", schedule.AccountId);
                    command.Parameters.AddWithValue("@ReserveId", schedule.ReserveId);

                    return command.ExecuteNonQuery() > 0; // 更新が成功した場合はtrueを返す
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラー: " + ex.Message);
                return false;
            }
        }
    }

    public List<ReserveScheduleView> GetReserveScheduleView(DateTime date)
    {
        List<ReserveScheduleView> reserveScheduleViews = new List<ReserveScheduleView>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();
                string query = @"
                SELECT user_name, account_id, account_name, comment, 
                       reserve_time, result, reserve_id
                FROM reserve_schedule_view
                WHERE DATE(reserve_time) = @Date;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    // パラメータを追加
                    command.Parameters.AddWithValue("@Date", date.Date);

                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            ReserveScheduleView viewItem = new ReserveScheduleView
                            {
                                UserName = reader["user_name"]?.ToString(),
                                AccountId = int.Parse(reader["account_id"].ToString()),
                                AccountName = reader["account_name"]?.ToString(),
                                Comment = reader["comment"]?.ToString(),
                                ReserveTime = reader["reserve_time"] as DateTime?,
                                Result = reader["result"]?.ToString() == "1",
                                ReserveId = reader["reserve_id"]?.ToString()
                            };
                            reserveScheduleViews.Add(viewItem);
                        }
                    }

                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return reserveScheduleViews;
    }

    public bool DeleteReserveSchedule(DateTime dt , bool resultContain = false)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();
                string query = @"DELETE FROM reserve_schedule 
                             WHERE reserve_date = @ReserveDate";

                if (resultContain)
                {
                    query += ";";
                }
                else
                {
                    query += "and result = '1';";
                }

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    return command.ExecuteNonQuery() > 0; // 削除が成功した場合はtrueを返す
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラー: " + ex.Message);
                return false;
            }
        }
    }




    #endregion




    public List<VpsMaster> GetVpsMaster()
    {
        List<VpsMaster> vpsList = new List<VpsMaster>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"
                SELECT 
                    id,
                    ip_address, 
                    port, 
                    name,
                    username,
                    pass,
                    memo
                FROM vps_master";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            VpsMaster searchItem = new VpsMaster()
                            {
                                Id = reader["id"] != DBNull.Value ? Convert.ToInt32(reader["id"]) : 0,
                                IpAddress = reader["ip_address"].ToString(),
                                Port = reader["port"].ToString(),
                                Name = reader["name"].ToString(),
                                Username = reader["username"].ToString(),
                                Pass = reader["pass"].ToString(),
                                Memo = reader["memo"].ToString(),
                            };

                            vpsList.Add(searchItem);
                        }
                    }
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラーが発生しました: " + ex.Message);
            }
        }

        return vpsList;
    }
}
