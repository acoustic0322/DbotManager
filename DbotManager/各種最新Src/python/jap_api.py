import requests

import config
from config import outputLog
#from config import jap_api_key

def proc_like_jap(tweet_name, tweet_id , jap_api_key, quantity = 10):

    # APIエンドポイント
    api_url = 'https://justanotherpanel.com/api/v2'

    action = 'add'            # アクションタイプ
    service_id = '7743'  # Japan Likes専用サービスID

    link = f'https://x.com/{tweet_name}/status/{tweet_id}'

#    outputLog(link)
    outputLog(f'jap_api_key={jap_api_key}')
    outputLog(f'link={link}')


    # リクエストデータ
    data = {
        'key': jap_api_key,
        'action': action,
        'service': service_id,
        'link': link,
        'quantity': quantity
    }

    try:
        # POSTリクエストの送信
        response = requests.post(api_url, data=data)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生
        
        # レスポンスのJSON解析
        result = response.json()

        if 'order' in result:
            return True, result['order']
        else:
            error_message = result.get('error', 'Unknown error occurred')
            outputLog(f'JAP API ERROR: {error_message}')
            return False, error_message

    except requests.exceptions.RequestException as e:
        error_message = f'HTTP Request Error: {str(e)}'
    except ValueError:
        error_message = 'Response is not a valid JSON'
    
    outputLog(f'JAP API ERROR: {error_message}')
    return False, error_message

def proc_bookmark_jap(tweet_name, tweet_id , jap_api_key , quantity = 10):

    # APIエンドポイント
    api_url = 'https://justanotherpanel.com/api/v2'

    action = 'add'            # アクションタイプ
    service_id = '1017'  # Japan Likes専用サービスID

    link = f'https://x.com/{tweet_name}/status/{tweet_id}'

#    outputLog(link)
    outputLog(f'jap_api_key={jap_api_key}')
    outputLog(f'link={link}')

    # リクエストデータ
    data = {
        'key': jap_api_key,
        'action': action,
        'service': service_id,
        'link': link,
        'quantity': quantity
    }

    try:
        # POSTリクエストの送信
        response = requests.post(api_url, data=data)
        response.raise_for_status()  # HTTPエラーがあれば例外を発生
        
        # レスポンスのJSON解析
        result = response.json()

        if 'order' in result:
            return True, result['order']
        else:
            error_message = result.get('error', 'Unknown error occurred')
            outputLog(f'JAP API ERROR: {error_message}')
            return False, error_message

    except requests.exceptions.RequestException as e:
        error_message = f'HTTP Request Error: {str(e)}'
    except ValueError:
        error_message = 'Response is not a valid JSON'
    
    outputLog(f'JAP API ERROR: {error_message}')
    return False, error_message


def get_available_service_id(api_key):
    """ 利用可能な service_id を取得する """
    api_url = 'https://justanotherpanel.com/api/v2'
    response = requests.get(api_url, params={'key': api_key, 'action': 'services'})
    
    if response.status_code == 200:
        try:
            services = response.json()
            for service in services:
                if 'Twitter Likes' in service['name']:  # サービス名でフィルタリング
                    print(service)
#                    return service['service']  # 有効な service_id を返す
        except ValueError:
            pass  # JSONデコードエラー
    return None  # 利用可能なサービスが見つからない場合



#print(get_available_service_id('7f7dc877aadbc0b7c996d6e48e95f1bf'))