import os
import sys
import time
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)).replace('\\scratch', ''))
from modules.ixbrowser.ixbrowser_local_api import IXBrowserClient

def reset_all_open_profiles():
    client = IXBrowserClient()
    open_list = client.get_open_profiles()
    
    if not open_list:
        logger.success("✅ IXBrowser上に「開いている（Open）」プロファイルはありません。すべてクリーンです！")
        return

    logger.warning(f"⚠️ IXBrowser上に {len(open_list)} 件の未クローズ（またはゴースト）プロファイルを発見しました。一括リセットを開始します...")
    
    # バッチで閉じる試行
    profile_ids = [p.get('profile_id', p.get('id')) for p in open_list]
    profile_ids = [pid for pid in profile_ids if pid]
    
    if profile_ids:
        logger.info(f"API経由で一括クローズを送信中...")
        client.close_profiles_batch(profile_ids)
        time.sleep(3)
        
    # それでも残っているものを1つずつ強制リセット
    open_list_after = client.get_open_profiles()
    if open_list_after:
        logger.warning(f"まだ {len(open_list_after)} 件がOpen状態です。個別の強制リセット（Open State Reset）を実行します。")
        for p in open_list_after:
            pid = p.get('profile_id', p.get('id'))
            if pid:
                logger.info(f"強制リセット中: Profile ID {pid}")
                client.reset_open_state(pid)
                time.sleep(0.5)
                
    # 最終確認
    final_list = client.get_open_profiles()
    if not final_list:
        logger.success("🎉 すべてのプロファイルの「Open」状態を強制解除し、クリーンアップしました！")
    else:
        logger.error(f"❌ まだ {len(final_list)} 件のプロファイルが残っています。IXBrowser本体を再起動してみてください。")

if __name__ == "__main__":
    reset_all_open_profiles()
