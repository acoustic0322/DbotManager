using System;
using System.Collections.Generic;
using System.Data;
using DbotManager.Table;
using System.Data.SqlClient;
using MySql.Data.MySqlClient;

public class MySqlDataAccess
{
    private string connectionString;

    public MySqlDataAccess(string server, string database, string user, string password)
    {
        // 接続文字列の構築
        connectionString = $"Server={server};Database={database};Uid={user};Pwd={password};charset=utf8mb4;";
    }

    public List<TweetHistory> GetTweetHistory()
    {
        List<TweetHistory> tweetHistoryList = new List<TweetHistory>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = "SELECT user_name, account_name, tweet_mode, comment, updatetime FROM tweet_history_view;";
                using (MySqlCommand command = new MySqlCommand(query, connection))
                {
                    using (MySqlDataReader reader = command.ExecuteReader())
                    {
                        while (reader.Read())
                        {
                            TweetHistory tweetHistory = new TweetHistory
                            {
                                UserName = reader["user_name"].ToString(),
                                AccountName = reader["account_name"].ToString(),
                                TweetMode = reader["tweet_mode"].ToString(),
                                Comment = reader["comment"].ToString(),
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

    public List<AccountMaster> GetAccountMaster()
    {
        List<AccountMaster> accountMasterList = new List<AccountMaster>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT id,user_id,name,
login_id,login_password,
api_key,api_key_secret,
access_token,access_token_secret,
bearer_token,refresh_token,enable
FROM account_master;";

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

    public List<CommentMaster> GetCommentMaster()
    {
        List<CommentMaster> commentMasterList = new List<CommentMaster>();

        using (MySqlConnection connection = new MySqlConnection(connectionString))
        {
            try
            {
                connection.Open();

                string query = @"SELECT id,user_id,
                        account_id,comment,enable 
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
                                Comment = reader["comment"].ToString(),
                                Enable = reader["enable"].ToString() == "1",
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
}
