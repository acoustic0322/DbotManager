using System;
using System.Collections.Generic;
using System.Data;
using DbotManager.Table;
using System.Data.SqlClient;
using MySql.Data.MySqlClient;
using System.ComponentModel.Design;
using DbotManager.MySql;
using DbotManager;

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

    public List<TweetHistory> GetTweetHistoryView()
    {
        List<TweetHistory> tweetHistoryList = new List<TweetHistory>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = "SELECT user_name, account_id, account_name, paid ,comment, mode, target_tweet_id, result, error_log ,updatetime FROM tweet_history_view order by updatetime desc;";
                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            TweetHistory tweetHistory = new TweetHistory
                            {
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
                            AccountMaster accountItem = new AccountMaster() { 
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
                                Enable = reader["enable"].ToString() == "1" ,
                                LikeEnable = reader["like_enable"].ToString() == "1",
                                ReplyEnable = reader["reply_enable"].ToString() == "1",
                                BookMarkEnable = reader["bookmark_enable"].ToString() == "1",
                                RepostEnable = reader["repost_enable"].ToString() == "1",
                                PostEnable = reader["post_enable"].ToString() == "1",

                                Reserve1Count= int.Parse(reader["reserve1_count"].ToString()),
                                Reserve2Count = int.Parse(reader["reserve2_count"].ToString()),
                                Reserve3Count = int.Parse(reader["reserve3_count"].ToString()),
                                Reserve4Count = int.Parse(reader["reserve4_count"].ToString()),
                                Reserve1StartHour = int.Parse(reader["reserve1_start_hour"].ToString()),
                                Reserve2StartHour = int.Parse(reader["reserve2_start_hour"].ToString()),
                                Reserve3StartHour = int.Parse(reader["reserve3_start_hour"].ToString()),
                                Reserve4StartHour = int.Parse(reader["reserve4_start_hour"].ToString()),
                                Reserve1EndHour = int.Parse(reader["reserve1_end_hour"].ToString()),
                                Reserve2EndHour = int.Parse(reader["reserve2_end_hour"].ToString()),
                                Reserve3EndHour = int.Parse(reader["reserve3_end_hour"].ToString()),
                                Reserve4EndHour = int.Parse(reader["reserve4_end_hour"].ToString()),
                                Reserve1Enable = reader["reserve1_enable"].ToString() == "1",
                                Reserve2Enable = reader["reserve2_enable"].ToString() == "1",
                                Reserve3Enable = reader["reserve3_enable"].ToString() == "1",
                                Reserve4Enable = reader["reserve4_enable"].ToString() == "1",
                                Paid = reader["paid"].ToString() == "1",
                                PaidLike = reader["paid_like"].ToString() == "1",
                                PaidBookmark = reader["paid_bookmark"].ToString() == "1",
                            };
                
                            accountMasterList.Add(accountItem);
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
                        account_id,comment,enable , chatgpt , mode , photo_enable , movie_enable
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
                                TweetModeType = reader["mode"].ToString() == "tweet" ? TweetModeTypes.Tweet : TweetModeTypes.Replay,
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
                        account_id,comment,enable , chatgpt , mode , photo_enable , movie_enable
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
                                TweetModeType = reader["mode"].ToString() == "tweet" ? TweetModeTypes.Tweet : TweetModeTypes.Replay,
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
                        account_id,comment,enable , chatgpt , mode , photo_enable , movie_enable
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
                                TweetModeType = reader["mode"].ToString() == "tweet" ? TweetModeTypes.Tweet : TweetModeTypes.Replay,
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
                                 movie_enable = @MovieEnable
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
                    command.Parameters.AddWithValue("@Mode", commentMaster.TweetModeType == TweetModeTypes.Tweet ? "tweet" : "retweet");

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

                string query = @"INSERT INTO comment_master (user_id, account_id, comment, enable, chatgpt , mode , photo_enable , movie_enable) 
                             VALUES (@UserId, @AccountId, @Comment, @Enable, @Chatgpt, @Mode , @PhotoEnable , @MovieEnable);
                            SELECT LAST_INSERT_ID(); ";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", commentMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", commentMaster.AccountId);
                    command.Parameters.AddWithValue("@Comment", commentMaster.Comment);
                    command.Parameters.AddWithValue("@Enable", commentMaster.Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Chatgpt", commentMaster.ChatGpt ? 1 : 0);
                    command.Parameters.AddWithValue("@Mode", commentMaster.TweetModeType == TweetModeTypes.Tweet ? "tweet" : "retweet");
                    command.Parameters.AddWithValue("@PhotoEnable", commentMaster.PhotoEnable ? 1 : 0);
                    command.Parameters.AddWithValue("@MovieEnable", commentMaster.MovieEnable ? 1 : 0);

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
                    "like_enable,bookmark_enable,reply_enable,repost_enable,sensyuken_enable,post_enable,reserve_enable,photo_enable,movie_enable" +
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
                                SensyukenEnable = reader["sensyuken_enable"].ToString() == "1",
                                PostEnable = reader["post_enable"].ToString() == "1",
                                ReserveEnable = reader["reserve_enable"].ToString() == "1",
                                PhotoEnable = reader["photo_enable"].ToString() == "1",
                                MovieEnable = reader["movie_enable"].ToString() == "1",
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
                 reserve1_count, reserve2_count, reserve3_count) 
                VALUES 
                (@UserId, @AccountId, @Reserve1Enable, @Reserve2Enable, @Reserve3Enable, 
                 @Reserve1StartHour, @Reserve2StartHour, @Reserve3StartHour, 
                 @Reserve1EndHour, @Reserve2EndHour, @Reserve3EndHour, 
                 @Reserve1Count, @Reserve2Count, @Reserve3Count);";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", reserveMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", reserveMaster.AccountId);
                    command.Parameters.AddWithValue("@Reserve1Enable", reserveMaster.Reserve1Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve2Enable", reserveMaster.Reserve2Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve3Enable", reserveMaster.Reserve3Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve1StartHour", reserveMaster.Reserve1StartHour);
                    command.Parameters.AddWithValue("@Reserve2StartHour", reserveMaster.Reserve2StartHour);
                    command.Parameters.AddWithValue("@Reserve3StartHour", reserveMaster.Reserve3StartHour);
                    command.Parameters.AddWithValue("@Reserve1EndHour", reserveMaster.Reserve1EndHour);
                    command.Parameters.AddWithValue("@Reserve2EndHour", reserveMaster.Reserve2EndHour);
                    command.Parameters.AddWithValue("@Reserve3EndHour", reserveMaster.Reserve3EndHour);
                    command.Parameters.AddWithValue("@Reserve1Count", reserveMaster.Reserve1Count);
                    command.Parameters.AddWithValue("@Reserve2Count", reserveMaster.Reserve2Count);
                    command.Parameters.AddWithValue("@Reserve3Count", reserveMaster.Reserve3Count);

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

                string query = @"SELECT user_id , account_id,reserve1_enable,reserve2_enable,reserve3_enable,
                        reserve1_start_hour,reserve2_start_hour,reserve3_start_hour,
                        reserve1_end_hour,reserve2_end_hour,reserve3_end_hour,
                        reserve1_count,reserve2_count,reserve3_count
                        FROM reserve_master where account_id = @AccountId;";

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
                                AccountId = int.Parse(reader["account_id"].ToString()),
                                Reserve1Count = int.Parse(reader["reserve1_count"].ToString()),
                                Reserve2Count = int.Parse(reader["reserve2_count"].ToString()),
                                Reserve3Count = int.Parse(reader["reserve3_count"].ToString()),
                                Reserve1StartHour = int.Parse(reader["reserve1_start_hour"].ToString()),
                                Reserve2StartHour = int.Parse(reader["reserve2_start_hour"].ToString()),
                                Reserve3StartHour = int.Parse(reader["reserve3_start_hour"].ToString()),
                                Reserve1EndHour = int.Parse(reader["reserve1_end_hour"].ToString()),
                                Reserve2EndHour = int.Parse(reader["reserve2_end_hour"].ToString()),
                                Reserve3EndHour = int.Parse(reader["reserve3_end_hour"].ToString()),
                                Reserve1Enable = reader["reserve1_enable"].ToString() == "1",
                                Reserve2Enable = reader["reserve2_enable"].ToString() == "1",
                                Reserve3Enable = reader["reserve3_enable"].ToString() == "1",
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
                UPDATE reserve_master 
                SET 
                    user_id = @UserId,
                    reserve1_enable = @Reserve1Enable,
                    reserve2_enable = @Reserve2Enable,
                    reserve3_enable = @Reserve3Enable,
                    reserve1_start_hour = @Reserve1StartHour,
                    reserve2_start_hour = @Reserve2StartHour,
                    reserve3_start_hour = @Reserve3StartHour,
                    reserve1_end_hour = @Reserve1EndHour,
                    reserve2_end_hour = @Reserve2EndHour,
                    reserve3_end_hour = @Reserve3EndHour,
                    reserve1_count = @Reserve1Count,
                    reserve2_count = @Reserve2Count,
                    reserve3_count = @Reserve3Count
                WHERE account_id = @AccountId;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", reserveMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", reserveMaster.AccountId);
                    command.Parameters.AddWithValue("@Reserve1Enable", reserveMaster.Reserve1Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve2Enable", reserveMaster.Reserve2Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve3Enable", reserveMaster.Reserve3Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Reserve1StartHour", reserveMaster.Reserve1StartHour);
                    command.Parameters.AddWithValue("@Reserve2StartHour", reserveMaster.Reserve2StartHour);
                    command.Parameters.AddWithValue("@Reserve3StartHour", reserveMaster.Reserve3StartHour);
                    command.Parameters.AddWithValue("@Reserve1EndHour", reserveMaster.Reserve1EndHour);
                    command.Parameters.AddWithValue("@Reserve2EndHour", reserveMaster.Reserve2EndHour);
                    command.Parameters.AddWithValue("@Reserve3EndHour", reserveMaster.Reserve3EndHour);
                    command.Parameters.AddWithValue("@Reserve1Count", reserveMaster.Reserve1Count);
                    command.Parameters.AddWithValue("@Reserve2Count", reserveMaster.Reserve2Count);
                    command.Parameters.AddWithValue("@Reserve3Count", reserveMaster.Reserve3Count);

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

    #region MediaMaster

    public List<MediaMaster> GetMediaMaster()
    {
        List<MediaMaster> commentMasterList = new List<MediaMaster>();

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
                                CommentId = int.Parse(reader["comment_id"].ToString()),
                                MediaId = int.Parse(reader["media_id"].ToString()),
                                UserId = int.Parse(reader["user_id"].ToString()),
                                AccountId = int.Parse(reader["account_id"].ToString()),
                                Name = reader["name"].ToString(),
                                MediaType = reader["media_type"].ToString() == "photo" ? MediaTypes.Photo : MediaTypes.Movie
                            };

                            commentMasterList.Add(mediaMaster);
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
}
