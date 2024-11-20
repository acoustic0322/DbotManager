using System;
using System.Collections.Generic;
using System.Data;
using DbotManager.Table;
using System.Data.SqlClient;
using MySql.Data.MySqlClient;
using System.ComponentModel.Design;

public class MySqlDataAccess
{
    private string connectionString;

    public MySqlDataAccess(string server, string database, string user, string password)
    {
        // 接続文字列の構築
        connectionString = $"Server={server};Database={database};Uid={user};Pwd={password};charset=utf8mb4;";
    }

    public List<TweetHistory> GetTweetHistoryView()
    {
        List<TweetHistory> tweetHistoryList = new List<TweetHistory>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = "SELECT user_name, account_id, account_name, paid ,comment, tweet_mode, target_tweet_id, result, error_log ,updatetime FROM tweet_history_view;";
                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            TweetHistory tweetHistory = new TweetHistory
                            {
                                UserName = reader["user_name"].ToString(),
                                AccountId = reader["account_id"].ToString(),
                                AccountName = reader["account_name"].ToString(),
                                Paid = reader["paid"].ToString() == "1",
                                Comment = reader["comment"].ToString(),
                                TweetMode = reader["tweet_mode"].ToString(),
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
                    am.access_token,am.access_token_secret,
                    am.bearer_token,am.refresh_token,am.enable
                    ,am.like_enable,am.bookmark_enable,am.retweet_enable,am.tweet_enable
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
                                AccessToken = reader["access_token"].ToString(),
                                AccessTokenSecret = reader["access_token_secret"].ToString(),
                                BearerToken = reader["bearer_token"].ToString(),
                                RefreshToken = reader["refresh_token"].ToString(),
                                Enable = reader["enable"].ToString() == "1" ,
                                LikeEnable = reader["like_enable"].ToString() == "1",
                                BookMarkEnable = reader["bookmark_enable"].ToString() == "1",
                                RetweetEnable = reader["retweet_enable"].ToString() == "1",
                                TweetEnable = reader["tweet_enable"].ToString() == "1",
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
                        account_id,comment,enable , whole
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
                                Comment = reader["comment"].ToString(),
                                Enable = reader["enable"].ToString() == "1",
                                Whole = reader["whole"].ToString() == "1",
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

    public CommentMaster GetCommentMaster(int commentId)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT id,user_id,
                        account_id,comment,enable , whole
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
                                Comment = reader["comment"].ToString(),
                                Enable = reader["enable"].ToString() == "1",
                                Whole = reader["whole"].ToString() == "1",
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
                                 whole = @Whole,
                                 enable = @Enable
                             WHERE id = @Id;";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", commentMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", commentMaster.AccountId);
                    command.Parameters.AddWithValue("@Comment", commentMaster.Comment);
                    command.Parameters.AddWithValue("@Whole", commentMaster.Whole ? 1 : 0);
                    command.Parameters.AddWithValue("@Enable", commentMaster.Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Id", commentMaster.Id);

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

                string query = @"INSERT INTO comment_master (user_id, account_id, comment, enable, whole) 
                             VALUES (@UserId, @AccountId, @Comment, @Enable, @Whole);";
//                SELECT LAST_INSERT_ID(); ";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@UserId", commentMaster.UserId);
                    command.Parameters.AddWithValue("@AccountId", commentMaster.AccountId);
                    command.Parameters.AddWithValue("@Comment", commentMaster.Comment);
                    command.Parameters.AddWithValue("@Enable", commentMaster.Enable ? 1 : 0);
                    command.Parameters.AddWithValue("@Whole", commentMaster.Whole ? 1 : 0);

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

    public List<UserMaster> GetUserNames()
    {
        List<UserMaster> userList = new List<UserMaster>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = "SELECT id, username , password , admin , enable ,memo FROM user_master;";
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
                                Memo = reader["memo"].ToString()
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

    public bool InsertReserveSchedule(ReserveSchedule schedule)
    {
        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();
                string query = @"INSERT INTO reserve_schedule 
                             (reserve_date, reserve_time, account_id, comment_id, result, reserve_id) 
                             VALUES (@ReserveDate, @ReserveTime, @AccountId, @CommentId, @Result, @ReserveId);";

                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    command.Parameters.AddWithValue("@ReserveDate", schedule.ReserveDate);
                    command.Parameters.AddWithValue("@ReserveTime", schedule.ReserveTime);
                    command.Parameters.AddWithValue("@AccountId", schedule.AccountId);
                    command.Parameters.AddWithValue("@CommentId", schedule.CommentId);
                    command.Parameters.AddWithValue("@Result", schedule.Result ? "1" : "0");
                    command.Parameters.AddWithValue("@ReserveId", schedule.ReserveId);

                    return command.ExecuteNonQuery() > 0; // 挿入が成功した場合はtrueを返す
                }
            }
            catch (Exception ex)
            {
                Console.WriteLine("エラー: " + ex.Message);
                return false;
            }
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
