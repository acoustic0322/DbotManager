import os
import sys
import json
import sqlite3
import requests
import time
from DrissionPage import ChromiumPage, ChromiumOptions

# 親ディレクトリからモジュールを読み込めるようにパスを追加
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import x_login_manager
import ixBrowser_profile_manager

API_BASE = "http://127.0.0.1:53200/api/v2"

def get_account():
    # 親ディレクトリにある accounts.db に接続
    db_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "accounts.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT screen_name FROM accounts LIMIT 1")
    row = cursor.fetchone()
    conn.close()
    return row

def main():
    row = get_account()
    if not row:
        print("❌ データベースにアカウントがありません。先に sheets_sync.py pull を行ってください。")
        return
    username = row[0]
    
    print(f"ℹ️ アカウント: @{username}")
    
    # ixBrowserの既存プロファイルIDを探す
    profile_id = ixBrowser_profile_manager.find_profile_by_name(API_BASE, username)
    if not profile_id:
        print(f"❌ ixBrowser上に {username} のプロファイルが見つかりません。")
        return
        
    print(f"🌐 ixBrowserでプロファイル {profile_id} を起動中...")
    page, err = x_login_manager.open_ix_browser(API_BASE, profile_id)
    if not page:
        print(f"❌ ブラウザの起動に失敗しました: {err}")
        return
        
    try:
        # Xにアクセスしてログインチェック
        print("🔗 X.com にアクセスしています...")
        page.get("https://x.com")
        time.sleep(5)
        
        # ログイン確認
        if not (page.ele('css:[data-testid="AppTabBar_Home_Link"]', timeout=5) or \
                page.ele('css:[data-testid="SideNav_NewTweet_Button"]', timeout=2)):
            print("⚠️ ログインしていません。ブラウザ上でログインを完了させてください。")
            return
            
        print("🛡️ ネットワーク監視(CreateTweet)を開始します...")
        page.listen.start('CreateTweet')
        
        # ツイート入力欄を探す
        # 左メニューの「ポストする」ボタンをクリック
        post_btn = page.ele('css:[data-testid="SideNav_NewTweet_Button"]')
        if post_btn:
            print("🔘 「ポストする」ボタンをクリックします...")
            post_btn.click()
            time.sleep(2)
            
        # テキストエリアに入力
        textarea = page.ele('css:[data-testid="tweetTextarea_0"]')
        if textarea:
            test_text = f"デバッグ投稿 {int(time.time())}"
            print(f"⌨️ テストテキストを入力します: {test_text}")
            textarea.input(test_text)
            time.sleep(1.5)
            
            # 送信ボタンクリック
            send_btn = page.ele('css:[data-testid="tweetButton"]') or page.ele('css:[data-testid="tweetButtonInline"]')
            if send_btn:
                print("🚀 「ポストする」送信ボタンをクリックします...")
                send_btn.click()
                
                print("⏳ Xの送信リクエストをキャプチャ中...")
                res = page.listen.wait(timeout=15)
                if res:
                    print("\n" + "="*60)
                    print("🎉 最新の CreateTweet ペイロードを検出しました！")
                    print("="*60)
                    
                    post_data = res.request.postData
                    if isinstance(post_data, str):
                        try:
                            parsed = json.loads(post_data)
                            print(json.dumps(parsed, indent=2, ensure_ascii=False))
                        except Exception:
                            print(post_data)
                    else:
                        print(post_data)
                    print("="*60 + "\n")
                else:
                    print("❌ 制限時間内に CreateTweet リクエストをキャプチャできませんでした。")
            else:
                print("❌ 送信ボタンが見つかりません。")
        else:
            print("❌ テキストエリアが見つかりません。")
            
    finally:
        # ブラウザを閉じる
        print("🛑 ブラウザを終了しています...")
        x_login_manager.close_ix_browser(API_BASE, profile_id, page)

if __name__ == '__main__':
    main()
