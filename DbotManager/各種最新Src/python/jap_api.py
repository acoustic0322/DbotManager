import requests

import config
from config import outputLog

def proc_like_jap(tweet_name, tweet_id , quantity = 10):

    # APIエンドポイント
    api_url = 'https://justanotherpanel.com/api/v2'

    # 必要なパラメータ
    api_key = '7f7dc877aadbc0b7c996d6e48e95f1bf'  # 取得したAPIキー
#    api_key = '026e7a18d6426b6bad09801b5e203883'
    action = 'add'            # アクションタイプ

#    service_id = 'service_id_for_twitter_likes'  # Twitterいいね用のサービスID
#    service_id = '9391'  # Twitterいいね用のサービスID
    service_id = '7743'  # Twitterいいね用のサービスID

#    link = f'https://twitter.com/{tweet_id}'  # 対象のツイートURL
    link = f'https://x.com/{tweet_name}/status/{tweet_id}'

    outputLog(link)


    # リクエストデータ
    data = {
        'key': api_key,
        'action': action,
        'service': service_id,
        'link': link,
        'quantity': quantity
    }

    # POSTリクエストの送信
    response = requests.post(api_url, data=data)

    # レスポンスの確認
    if response.status_code == 200:
        try:
            result = response.json()
            if 'order' in result:
                #outputLog(f'JAP API SUCCESS : ID={result['order']}')
                return True, result['order']
        except ValueError:
            pass  # JSONデコードエラー

    outputLog(f'JAP API ERROR')
    return False, None


