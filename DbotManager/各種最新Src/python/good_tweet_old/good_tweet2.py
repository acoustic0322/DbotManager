import tweepy

# 各種認証情報を設定
#consumer_key = 'SBd4tiZXE2w65cquDEWHLuqHi'
#consumer_secret = 'K7f1EfMmPkRWXCQYz4HREbPrvunTk4h3ymZtG1RoMwZcBfBUYC'

#consumer_key = 'eHRzVVNlb1ZDLWVSNTl2ckg5b246MTpjaQ'
#consumer_secret = 'VfDkPqPfbOyk5VCbETYKk7t-rRP1BUMlGO8Gg2t5ea7zoD6RXE'
#access_token = '1777348550851956736-GUi9D959N3oMP7ZcJPCiZCA5PaZgsC'
#access_token_secret = 'RNfWGPFVn5czTyvMxu3luIg4HHGbTzXM6w1daghpFi4Il'


#OnSounds(なんぽん)
consumer_key = 'nWBWZwWOIZU4fc0VnwjHeVM2X'
consumer_secret = 'pcwSUiA2TQsuaxJnE4CCl0YPLenGQVRFoFWtI6Rl4AHz3Yfrp5'
access_token = '2446855615-rAl5beTCVoTrpSeoghbl1V5pM0DD6l5ZwkUXIJr'
access_token_secret = '27myFiqAmkjWa1fx6NAljvR9iqYMA7SlzwoZ3YszlokLp'


#clientID=NkJGVEtCUkJkRzVIY0NOQTRQbk46MTpjaQ
#clientsecret=3m-S0Clov1VoLUPQxnYUASeBDUF5oDivViWZwK7YgqndxDDKfn

# OAuth 1.0aで認証するための設定
auth = tweepy.OAuth1UserHandler(
    consumer_key, consumer_secret,
    access_token, access_token_secret
)

# ここに自分のTwitter APIの認証情報を入力
#client = tweepy.Client(bearer_token='YWpGM1h3WjNRMlczMDJmTmhOaWdTcFVxVkJNX05wTXYtbFMwOWc4NjVpSmFUOjE3MzA4MTQ5NTQyMTM6MToxOmF0OjE')
#client = tweepy.Client(auth=auth)
# 認証をクライアントに適用
api = tweepy.API(auth)

# アクセス権限の確認
try:
    api.verify_credentials()
    print("認証成功")
except tweepy.errors.Unauthorized:
    print("認証エラー")
except Exception as e:
    print(f"エラーが発生しました: {e}")

# 認証情報を設定する
client = tweepy.Client(
    consumer_key=consumer_key,
    consumer_secret=consumer_secret,
    access_token=access_token,
    access_token_secret=access_token_secret
)

#if proxy_url!="":
#    client.session.proxies = proxies

# ツイートのID
tweet_id = '1854085562485129666'#args[1]  # ここに対象のツイートのIDを入力してください

#try:
    # いいねをする
#    client.like(tweet_id)
#except tweepy.errors.Unauthorized:
#    print("認証に失敗しました：認証情報を確認してください。")
#except Exception as e:
#    print(f"エラーが発生しました: {e}")


#try:
#    tweet_id = '1854085562485129666'
#    api.create_favorite(tweet_id)
#    api.like(tweet_id)
#    print("ツイートにいいねしました。")
#except tweepy.errors.Unauthorized:
#    print("認証に失敗しました：認証情報を確認してください。")
#except Exception as e:
#    print(f"エラーが発生しました: {e}")

#try:
#    # tweet_idが別の場所で定義されていると仮定
#    tweet_id = 1842391298260738190
#    client.like(tweet_id)
#except tweepy.errors.Unauthorized:
#    print("認証に失敗しました：認証情報と権限を確認してください。")
