import sys
import os
import time
import argparse
import random
import traceback
from loguru import logger

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ixbrowser.ixbrowser_controller import IXBrowserController
from modules.ixbrowser.bot_logic_dp import IXBrowserBotLogicDP
from modules.mutual_follow.db_manager import DBManager
from utils.ip_rotation import ensure_ip_rotated, create_standard_router
from utils.human_action import sleep_random
from utils.sleep_preventer import prevent_sleep
from modules.ai_generator import AIGenerator
from androidIP自動変更.androidIP_autochange import reset_mobile_data
from concurrent.futures import ThreadPoolExecutor
import concurrent.futures

try:
    logger.remove()
    logger.add(sys.stdout, level="INFO")
    logger.add("logs/engagement.log", rotation="1 day", encoding='utf-8')
except Exception:
    pass

DEFAULT_BATCH_SIZE = 3 # User requested 3

def execute_engagement(page, bot, url, username="unknown", tweet_keyword=None, target_id=None,
                       do_like=True, do_bookmark=True, do_rt=False, do_reply=False,
                       do_follow=False, do_tweet=False, reply_text=None, ai_gen=None, db=None, args=None, assigned_name=None):
    try:
        target_handle = "unknown"
        if target_id:
            target_handle = target_id.replace('@', '')
        elif url:
            import re
            m = re.search(r'x\.com/([^/]+)/status', url)
            target_handle = m.group(1) if m else "unknown"

        if do_tweet:
            tweet_text = reply_text
            if not tweet_text and ai_gen:
                import re
                clean_kw = re.sub(r'\s*Type-\d+', '', tweet_keyword or '').strip() or "日常生活"
                tweet_text = ai_gen.generate_tweet_text(username=username, category=clean_kw)

            if tweet_text == "ERROR:AI_RESTRICTED":
                logger.error(f"[{username}] AI RESTRICTED - Skipping tweet.")
                if db: db.update_sync_status(username, "実行失敗: AI制限中")
                return False, "AI_RESTRICTED"

            if not tweet_text:
                fallback_tweets = [
                    "今日も一日お疲れ様です！",
                    "最近忙しくてなかなか休めてないな😅",
                    "今日もがんばった！",
                    "ちょっと疲れたけど充実した一日だった",
                    "明日も頑張ろう💪",
                    "今日はゆっくり休みます😴",
                    "なんか今日いいことあった気がする😊",
                    "毎日あっという間に過ぎていくな～",
                ]
                tweet_text = random.choice(fallback_tweets)

            media_path = None
            if args.tweet_image and ai_gen and random.random() < 0.6:
                logger.info(f"[{username}] Generating high-quality AI image for tweet context...")
                media_path = ai_gen.generate_image(tweet_text, prefix=f"tweet_{username}")

            logger.info(f"[{username}] Posting new tweet: {tweet_text[:30]}...")
            if bot.post_tweet(tweet_text, media_path=media_path):
                logger.success(f"[{username}] Tweet posted{' with image: ' + media_path if media_path else ''}.")
                if db: db.record_daily_action(username, "tweet")
                if db: db.update_last_tweet_at(username)
            sleep_random(3, 5)

        if do_follow and target_handle != "unknown":
            logger.info(f"[{username}] Checking follow status for @{target_handle}...")
            if bot.follow_by_username(target_handle):
                if db: db.record_daily_action(username, "follow")
            sleep_random(2, 4)

        if do_like or do_rt or do_reply:
            logger.info(f"Visiting @{target_handle}'s profile to find the latest tweet...")
            # Use stealthy navigation (Search if possible)
            if hasattr(bot, 'navigate_to_profile'):
                bot.navigate_to_profile(target_handle)
            else:
                page.get(f"https://x.com/{target_handle}")
            sleep_random(5, 10)

            found_tweet = None
            logger.info(f"[{username}] Searching for tweet matching '{tweet_keyword or 'latest'}'...")
            for i in range(8):
                all_matches = []
                if tweet_keyword:
                    short_keyword = tweet_keyword[:15] if len(tweet_keyword) > 15 else tweet_keyword
                    articles = page.eles('css:article[data-testid="tweet"]')
                    for art in articles:
                        if short_keyword.lower() in art.text.lower():
                            all_matches.append(art)
                else:
                    all_matches = page.eles('css:article[data-testid="tweet"]')

                for potential in all_matches:
                    try:
                        sc = potential.ele("css:[data-testid='socialContext']", timeout=0.5)
                        if sc and ("Pinned" in sc.text or "ピン留め" in sc.text or "固定" in sc.text):
                            continue
                    except: pass
                    found_tweet = potential
                    break

                if found_tweet:
                    try:
                        found_tweet.scroll.to_see()
                        time.sleep(1)
                        found_tweet.click()
                        logger.success(f"[{username}] Found and clicked the target tweet!")
                        break
                    except Exception as e:
                        logger.debug(f"[{username}] Click failed, retrying search: {e}")
                        found_tweet = None

                logger.info(f"[{username}] Tweet not found in view, scrolling... ({i+1}/8)")
                page.scroll.down(800)
                time.sleep(1.5)

            if not found_tweet:
                if url:
                    logger.warning(f"[{username}] Could not find matching tweet on profile. Trying direct URL fallback.")
                    page.get(url)
                    sleep_random(3, 5)
                else:
                    logger.error(f"[{username}] ABORT: Could not find tweet '{tweet_keyword}' on @{target_handle}'s profile.")
                    return (do_follow or do_tweet), "NotFound"

            sleep_random(2, 4)
            html = page.html.lower() if page.html else ""
            title = page.title if page.title else ""
             # Additional Japanese Lock Patterns
            if "不審なアクティビティ" in html or "パスワードを変更してください" in html or \
               "本人確認" in title or "認証コードを入力" in html or "セキュリティ上の理由" in html:
                 return False, "LOCKED"
            if "account suspended" in html or "凍結" in html:
                logger.error("Our Account is explicitly suspended.")
                return False, "SUSPENDED"
            if "account/access" in page.url.lower():
                logger.warning("Our Account is locked/restricted (Access page).")
                return False, "LOCKED"
            if "doesn't exist" in html or "存在しません" in html:
                logger.warning("Target Tweet is unavailable (Deleted or Target Suspended).")
                return False, "NotFound"

            try:
                photo_ele = page.ele("css:[data-testid='tweetPhoto']", timeout=2)
                if photo_ele:
                    logger.info("🖼️ 画像を発見しました。人間のように画像をクリックして閲覧します。")
                    photo_ele.click(by_js=True)
                    viewing_time = random.uniform(4.0, 7.0)
                    logger.info(f"👉 画像を {viewing_time:.1f} 秒間 閲覧中...")
                    time.sleep(viewing_time)
                    close_btn = page.ele("css:[aria-label='Close']", timeout=2)
                    if not close_btn:
                        close_btn = page.ele("css:[aria-label='閉じる']", timeout=1)
                    if close_btn:
                        close_btn.click(by_js=True)
                    else:
                        page.run_js("document.dispatchEvent(new KeyboardEvent('keydown', {'key': 'Escape', 'keyCode': 27}));")
                    sleep_random(1.5, 3.0)
                else:
                    read_time = random.uniform(4.0, 7.5)
                    logger.info(f"📖 文字を {read_time:.1f} 秒間 閲覧中...")
                    time.sleep(read_time)
            except Exception as e:
                logger.warning(f"画像のクリック時に軽微なエラーが発生しました（スキップします）: {e}")

            try:
                scroll_dist = random.randint(200, 450)
                page.scroll.down(scroll_dist)
                time.sleep(random.uniform(1.0, 2.5))
                page.scroll.up(random.randint(50, 200))
                sleep_random(1, 2)
            except Exception:
                pass

            if do_like:
                like_btn = page.ele("css:[data-testid='like']", timeout=5)
                if like_btn:
                    if "unavailable" not in like_btn.attr('aria-label').lower():
                        like_btn.click(by_js=True)
                        logger.info(f"[{username}] Liked.")
                        if db: db.record_daily_action(username, "like")
                    else:
                        logger.info(f"[{username}] Already liked.")
                time.sleep(1)

            if do_bookmark:
                bookmark_btn = page.ele("css:[data-testid='bookmark']", timeout=5)
                if bookmark_btn:
                    bookmark_btn.click(by_js=True)
                    logger.info(f"[{username}] Bookmarked.")
                    if db: db.record_daily_action(username, "bookmark")
                time.sleep(1)

            if do_rt:
                rt_btn = page.ele("css:[data-testid='retweet']", timeout=5)
                if rt_btn:
                    rt_btn.click(by_js=True)
                    time.sleep(1)
                    confirm_rt = page.ele("css:[data-testid='retweetConfirm']", timeout=3)
                    if confirm_rt:
                        confirm_rt.click(by_js=True)
                        logger.info(f"[{username}] Retweeted.")
                        if db: db.record_daily_action(username, "rt")
                time.sleep(1)

            if do_reply:
                tweet_text_captured = ""
                try:
                    text_ele = page.ele("css:[data-testid='tweetText']", timeout=3)
                    if text_ele:
                        tweet_text_captured = text_ele.text
                        logger.info(f"Captured tweet text for AI context: {tweet_text_captured[:30]}...")
                except:
                    pass

                final_reply = reply_text
                if not final_reply and ai_gen and tweet_text_captured:
                    logger.info("Generating AI reply...")
                    final_reply = ai_gen.generate_reply(tweet_text_captured)
                    logger.info(f"AI Reply generated: {final_reply}")
                if not final_reply:
                    final_reply = "とても素敵なツイートですね！"

                reply_btn = page.ele("css:[data-testid='reply']", timeout=5)
                if reply_btn:
                    reply_btn.click(by_js=True)
                    sleep_random(2, 3)
                    editor = page.ele("css:[data-testid='tweetTextarea_0']", timeout=5)
                    if editor:
                        editor.input(final_reply)
                        time.sleep(1)
                        post_btn = page.ele("css:[data-testid='tweetButtonInline']", timeout=3)
                        if post_btn:
                            post_btn.click(by_js=True)
                            sleep_random(1.5, 3.0)
                            
                            # Check for critical errors after replying
                            error_popups = [
                                "問題が発生しました。やりなおしてください。",
                                "問題が発生しました",
                                "やりなおしてください",
                                "Something went wrong, but don't fret",
                                "Something went wrong",
                                "let's give it another shot"
                            ]
                            for err_txt in error_popups:
                                err_ele = page.ele(f"text:{err_txt}", timeout=1)
                                if err_ele:
                                    logger.error(f"Critical error toast detected after reply: '{err_txt}'")
                                    raise ValueError(f"CriticalError: Account is suspended/restricted. Reply failed with: {err_txt}")
                                    
                            logger.info(f"[{username}] Replied: {final_reply[:20]}...")
                            if db: db.record_daily_action(username, "reply")
                time.sleep(2)

        return True, "Success"

    except Exception as e:
        err_msg = str(e)
        logger.error(f"[{username}] Error during interaction: {err_msg}")
        if "criticalerror" in err_msg.lower() or "suspended" in err_msg.lower() or "凍結" in err_msg:
            return False, "CriticalError"
        return False, "UnknownError"


def process_single_account(acc, i, total_needed, args, controller, ai_gen, db):
    username = acc['screen_name']
    logger.info(f"--- [Thread] Processing: {username} ({i+1}/{total_needed}) ---")
    # コマンドプロンプトのタイトルを変更
    if sys.platform == 'win32':
        os.system(f'title D-BOT [{i+1}/{total_needed}] @{username}')

    do_like = args.count > 0
    do_rt = args.rt_count > 0
    do_reply = args.reply_count > 0
    do_follow = args.follow_count > 0
    do_tweet = args.tweet_count > 0

    try:
        # [MODIFIED] 明示的に作成指示がない限り、新規作成は行わない (allow_create=args.recreate)
        profile_id = controller.get_or_create_profile(username, allow_create=args.recreate)
        
        if not profile_id:
            logger.error(f"[{username}] プロファイルが見つかりません。IXBrowser側で作成済みか確認してください。")
            if db: db.update_sync_status(username, "実行失敗: プロファイル未作成")
            return False, "ProfileMissing"

        # [NEW] 明示的な再作成指示がある場合、ここで強制リセット
        if args.recreate:
            logger.info(f"[{username}] 強制再作成フラグが有効です。プロファイルを再作成します...")
            new_pid = controller.full_profile_reset(profile_id, username)
            if new_pid:
                try:
                    import sqlite3
                    conn = sqlite3.connect('system.db')
                    conn.execute('UPDATE accounts SET profile_id = ? WHERE username = ?', (str(new_pid), username))
                    conn.commit()
                    conn.close()
                    profile_id = new_pid
                except: pass
            else:
                logger.error(f"[{username}] プロファイルの再作成に失敗しました。")
                return False, "RecreateError"

        page = controller.open_browser_dp(profile_id, screen_name=username, headless=(not args.visible))
        
        if page == "MISSING_PROFILE":
            # [MODIFIED] ここでも勝手に再作成せず、エラーとして終了する
            logger.error(f"[{username}] プロファイルがIXBrowser内に存在しません。自動再作成は禁止されています。")
            if db: db.update_sync_status(username, "実行失敗: プロファイル実体なし")
            return False, "MissingProfileInIX"

        if not page:
            logger.error(f"[{username}] Browser failed to open (Server Busy?).")
            if db: db.update_sync_status(username, "実行失敗: ブラウザ起動失敗(Server Busy等)")
            return False, "BrowserOpenError"

        db.update_sync_status(username, "実行中") # [NEW] Set running status
        bot = IXBrowserBotLogicDP(page)
        live_name = acc.get('assigned_name')
        current_keyword = args.keyword

        if do_tweet and ai_gen:
            db_category = acc.get('category', '日常生活')
            if db_category == '日常生活' and (not current_keyword or current_keyword == "unknown"):
                # 名前がない場合のみ、AI判定のために取得を試みる（最小限に抑える）
                if not live_name or str(live_name).lower() == 'nan' or str(live_name).strip() == "":
                    live_name = bot.get_display_name()
                    if live_name:
                        db.save_display_name(username, live_name)
                    else:
                        live_name = username
                db_category = ai_gen.determine_theme(str(live_name))
                db.update_category(username, db_category)
            current_keyword = db_category
            logger.info(f"[{username}] Using Category/Theme: {current_keyword}")

        auth_token = acc.get('auth_token')
        ct0 = acc.get('ct0')
        password = acc.get('password', '')
        use_b_column = str(password).startswith('__B__')
        if use_b_column:
            password = str(password)[5:]
        email = acc.get('email')
        totp_secret = acc.get('totp_secret')

        login_success, new_cookies = bot.login_with_token(
            auth_token, ct0=ct0, username=username,
            password=password, email=email, totp_secret=totp_secret
        )
        if login_success == "LOCKED":
            logger.warning(f"[{username}] アカウントロック検知。スキップします。")
            db.update_sync_status(username, "ロック")
            return False
        if login_success == "SUSPENDED":
            logger.error(f"[{username}] アカウント凍結検知。")
            db.update_account_status(username, is_suspended=True)
            db.update_sync_status(username, "凍結検知")
            return False

        if not login_success:
            logger.warning(f"[{username}] Token login failed. Trying password login...")
            if password and (email or username):
                result = bot.login_with_password(
                    username=username,
                    password=password,
                    email=email,
                    totp_secret=totp_secret
                )
                if isinstance(result, tuple):
                    login_success, new_cookies = result
                else:
                    login_success, new_cookies = result, {}
                
                # Check for explicit locked/suspended states first
                if login_success == "LOCKED":
                    logger.warning(f"[{username}] アカウントロック検知。スキップします。")
                    db.update_sync_status(username, "ロック")
                    return False
                if login_success == "SUSPENDED":
                    logger.error(f"[{username}] アカウント凍結検知。")
                    db.update_account_status(username, is_suspended=True)
                    db.update_sync_status(username, "凍結検知")
                    return False
                
                if login_success is True:
                    logger.success(f"[{username}] Password login successful.")
                    if new_cookies:
                        auth_token_new = new_cookies.get('auth_token')
                        ct0_new = new_cookies.get('ct0')
                        if auth_token_new and ct0_new:
                            try:
                                df_all = db.get_all_accounts_df()
                                mask = df_all['screen_name'] == username
                                if mask.any():
                                    df_all.loc[mask, 'auth_token'] = auth_token_new
                                    df_all.loc[mask, 'ct0'] = ct0_new
                                    db.save_accounts_df(df_all)
                                    logger.info(f"[{username}] 新しいトークンをDBに保存しました。")
                            except Exception as e:
                                logger.warning(f"[{username}] トークン保存失敗: {e}")
                else:
                    # B列使用時のみ042210を付けて再試行
                    if use_b_column and password and not password.endswith('042210'):
                        result2 = bot.login_with_password(
                            username=username,
                            password=password + '042210',
                            email=email,
                            totp_secret=totp_secret
                        )
                        if isinstance(result2, tuple):
                            login_success, new_cookies = result2
                        else:
                            login_success, new_cookies = result2, {}
                        
                        if login_success == "LOCKED":
                            logger.warning(f"[{username}] アカウントロック検知。スキップします。")
                            db.update_sync_status(username, "ロック")
                            return False
                        if login_success == "SUSPENDED":
                            logger.error(f"[{username}] アカウント凍結検知。")
                            db.update_account_status(username, is_suspended=True)
                            db.update_sync_status(username, "凍結検知")
                            return False
                    
                    if login_success is not True:
                        login_error_code = result2 if 'result2' in locals() else result
                        logger.error(f"[{username}] Password login failed ({login_error_code}). Skipping.")
                        db.update_sync_status(username, f"ログイン失敗: {login_error_code}")
                        return False
            else:
                logger.error(f"[{username}] Password login skipped: Missing credentials in database (Password is empty).")
                db.update_sync_status(username, "ログイン失敗 (パスワード未登録)")
                return False

        if not login_success:
            logger.error(f"[{username}] Login failed. Aborting engagement.")
            return False

        # ログイン成功後、最新のフォロー・フォロワー数を取得してDBに更新保存する
        try:
            counts = bot.get_follow_counts_via_api()
            if not counts:
                counts = bot.get_follow_counts_from_dom()
            if counts and db:
                db.update_follow_counts(username, counts['following'], counts['followers'])
                logger.info(f"[{username}] データベースのフォロー・フォロワー数を更新しました: {counts['following']} followings, {counts['followers']} followers.")
        except Exception as e:
            logger.warning(f"[{username}] データベースのフォロー・フォロワー数の更新に失敗しました: {e}")

        action_success, status = execute_engagement(
            page, bot, args.url, username=username,
            tweet_keyword=current_keyword, target_id=args.target_id,
            do_like=do_like, do_bookmark=do_like,
            do_rt=do_rt, do_reply=do_reply,
            do_follow=do_follow, do_tweet=do_tweet,
            reply_text=args.reply_text,
            ai_gen=ai_gen, db=db, args=args,
            assigned_name=acc.get('assigned_name')
        )
        if status == "CriticalError":
            db.update_account_status(username, is_suspended=True)
            db.update_sync_status(username, "凍結検知")
        elif action_success:
            db.update_sync_status(username, "完了") # [NEW] Set completed status
        else:
            db.update_sync_status(username, f"エラー: {status}")

        return True, "Success"

    except Exception as e:
        err_msg = str(e)
        logger.error(f"[{username}] Execution failed: {err_msg}")
        if db:
            if "lock" in err_msg.lower() or "checkpoint" in err_msg.lower():
                db.update_sync_status(username, "ロック検知")
            else:
                db.update_sync_status(username, f"実行失敗: {err_msg[:30]}")
        return False, err_msg
    finally:
        controller.close_browser(profile_id, screen_name=username)
        if 'page' in locals() and page and page != "MISSING_PROFILE":
            try: page.quit()
            except: pass
        if db and username:
            db.release_account(username)


def main():
    parser = argparse.ArgumentParser(description="Bulk Like & Bookmark via IXBrowser")
    parser.add_argument("--url", help="Target Tweet URL (Fallback)")
    parser.add_argument("--target-id", help="Target user screen name (@ID)")
    parser.add_argument("--keyword", help="Tweet text keyword for search")
    parser.add_argument("--count", type=int, default=0, help="Number of Likes")
    parser.add_argument("--rt-count", type=int, default=0, help="Number of RTs")
    parser.add_argument("--reply-count", type=int, default=0, help="Number of Replies")
    parser.add_argument("--follow-count", type=int, default=0, help="Number of Follows")
    parser.add_argument("--tweet-count", type=int, default=0, help="Number of New Tweets")
    parser.add_argument("--reply-text", help="Text to reply with")
    parser.add_argument("--total-count", type=int, help="Total accounts to use (if different from Like count)")
    parser.add_argument("--skip-ip", action="store_true", help="Skip IP rotation")
    parser.add_argument("--recreate", action="store_true", help="Force delete and recreate IXBrowser profiles")
    parser.add_argument("--tweet-image", action="store_true", help="Generate and attach an AI image to the tweet")
    parser.add_argument("--sync-sheets", action="store_true", help="Sync credentials from Google Sheets before starting")
    parser.add_argument("--visible", action="store_true", default=False, help="Run browser in visible mode (not headless)")
    args = parser.parse_args()

    logger.info(f"Starting Bulk Engagement Script")
    logger.info(f"Target URL: {args.url}")
    logger.info(f"Target User: {args.target_id}")
    logger.info(f"Arguments: counts(L:{args.count}, RT:{args.rt_count}, Rep:{args.reply_count}, Tw:{args.tweet_count}), Keyword:{args.keyword}, ImageGen:{'ON' if args.tweet_image else 'OFF'}")

    if not (args.url or args.target_id or args.tweet_count > 0 or args.recreate):
        if not args.keyword:
            logger.warning("⚠️ ターゲットやアクションが指定されていません。ログイン確認のみ行います。")

    prevent_sleep()
    db = DBManager()

    # スプレッドシートからパスワード・TOTP同期 (オプション)
    if getattr(args, 'sync_sheets', False):
        logger.info("Connecting to Google Sheets for credential sync...")
        try:
            import gspread
            from google.oauth2.service_account import Credentials
            DEFAULT_BATCH_SIZE = 4 # Increased for better throughput
            SPREADSHEET_ID = '1ikjVkNydwonlG2cvKAu4BKRfzu4ZEuJLXnHBAE6efbw'
            SHEET_GID = 188292514
            scopes = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
            
            if not os.path.exists('data/google_credentials.json'):
                logger.warning("Google credentials file not found. Skipping sync.")
            else:
                creds = Credentials.from_service_account_file('data/google_credentials.json', scopes=scopes)
                gc = gspread.authorize(creds)
                logger.info(f"Opening spreadsheet: {SPREADSHEET_ID}")
                spreadsheet = gc.open_by_key(SPREADSHEET_ID)
                
                worksheet = None
                for sheet in spreadsheet.worksheets():
                    if sheet.id == SHEET_GID:
                        worksheet = sheet
                        break
                
                if worksheet:
                    logger.info("Fetching values from spreadsheet...")
                    rows = worksheet.get_all_values()
                    logger.info(f"Syncing {len(rows)-1} rows with database...")
                    df_all = db.get_all_accounts_df()
                    for row in rows[1:]:
                        if len(row) < 7:
                            continue
                        username = str(row[0]).strip().replace('@', '')
                        password_c = str(row[2]).strip()
                        password_b = str(row[1]).strip() if len(row) > 1 else ''
                        
                        if password_c:
                            password = password_c
                        else:
                            password = f"__B__{password_b}"
                        totp = str(row[6]).strip()
                        if not username:
                            continue
                        mask = df_all['screen_name'] == username
                        if mask.any():
                            if password:
                                df_all.loc[mask, 'password'] = password
                            if totp:
                                df_all.loc[mask, 'totp_secret'] = totp
                    db.save_accounts_df(df_all)
                    logger.success("スプレッドシートからパスワード・TOTP同期完了")
        except Exception as e:
            logger.warning(f"スプレッドシート同期失敗: {e}")
    else:
        logger.debug("Skipping Google Sheets sync (use --sync-sheets to enable)")

    # Load Settings
    PROGRESS_FILE = 'data/task_progress.json'

    def update_progress(total, success, fail, status="running", success_list=None, fail_list=None):
        try:
            import json
            with open(PROGRESS_FILE, 'w', encoding='utf-8') as f:
                json.dump({
                    "total": total,
                    "success": success,
                    "fail": fail,
                    "status": status,
                    "success_list": success_list or [],
                    "fail_list": fail_list or [],
                    "timestamp": time.time()
                }, f)
        except Exception as e:
            logger.warning(f"Failed to update progress file: {e}")

    settings = {}
    if os.path.exists('data/settings.json'):
        import json
        with open('data/settings.json', 'r', encoding='utf-8') as f:
            settings = json.load(f)

    gemini_keys = settings.get("GEMINI_API_KEYS", settings.get("gemini_api_key", []))
    openai_keys = settings.get("OPENAI_API_KEYS", [])
    
    # If settings is empty or missing keys, fallback to config.json
    if not gemini_keys and not openai_keys:
        try:
            with open('config.json', 'r', encoding='utf-8') as f:
                conf = json.load(f)
                gemini_keys = conf.get("GEMINI_API_KEYS", [])
                openai_keys = [conf.get("OPENAI_API_KEY")] if conf.get("OPENAI_API_KEY") else []
        except: pass

    ai_gen = AIGenerator(api_keys=gemini_keys, openai_keys=openai_keys)

    try:
        df = db.get_all_accounts_df()
        total_in_db = len(df)
        targets = df[df['Select'] == True]
        selected_count = len(targets)
        logger.info(f"DBから読み込み完了: 合計 {total_in_db}件 / 選択済み {selected_count}件")
    except Exception as e:
        logger.error(f"Failed to load accounts from DB: {e}")
        return

    if targets.empty:
        logger.error(f"実行対象のアカウントが0件です（DB合計: {total_in_db}件）。メインPCのダッシュボードでアカウントを選択してから実行してください。")
        return

    # --- PC別事前割り当て（Pre-Assignment Distribution / 同時起動対応） ---
    # アルゴリズムは ORDER BY username ASC + idx % num_pcs で完全に決定論的（同じ入力＝同じ出力）です。
    # 両PCが同時に起動して全く同時に実行しても、DBには全く同じ割り当て（同じ値）を書き込むだけなので競合しません。
    try:
        with open('config.json', 'r', encoding='utf-8') as f:
            cfg = json.load(f)
        pc_map = cfg.get('PC_MAP', {})
        all_pc_ids = sorted(set(pc_map.values()))  # ['PC_01', 'PC_02', ...]
        num_pcs = max(1, len(all_pc_ids))
        my_pc_index = all_pc_ids.index(db.pc_name) if db.pc_name in all_pc_ids else 0
        logger.info(f"📡 PC構成: {all_pc_ids} / このPC: {db.pc_name} (index={my_pc_index})")
    except Exception as e:
        logger.warning(f"PC_MAP読み込み失敗、単独モードで実行: {e}")
        all_pc_ids = [db.pc_name]
        num_pcs = 1
        my_pc_index = 0

    # 全対象アカウントを取得してPC別に等分して割り当てる
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        p = db._placeholder()

        # 1. 既に有効なPCが割り当てられているアカウント数をカウントする
        pc_counts = {pc: 0 for pc in all_pc_ids}
        for pc in all_pc_ids:
            cursor.execute(f"SELECT COUNT(*) FROM accounts WHERE selected=1 AND is_alive=1 AND assigned_pc={p}", (pc,))
            row = cursor.fetchone()
            pc_counts[pc] = list(row.values())[0] if isinstance(row, dict) else row[0]

        # 2. 未割り当て、または無効なPC名が入っているアカウントを取得（決定論的ソート）
        placeholders_str = ", ".join([p] * len(all_pc_ids))
        cursor.execute(f"""
            SELECT username FROM accounts 
            WHERE selected=1 AND is_alive=1 
            AND (assigned_pc IS NULL OR assigned_pc = '' OR assigned_pc NOT IN ({placeholders_str}))
            ORDER BY username ASC
        """, tuple(all_pc_ids))
        unassigned_usernames = [row['username'] if isinstance(row, dict) else row[0] for row in cursor.fetchall()]
        total_unassigned = len(unassigned_usernames)

        if total_unassigned > 0:
            logger.info(f"🔀 未割り当ての {total_unassigned} 件をPCに自動振り分け中...（既存の固定担当: {pc_counts}）")
            # 決定論的に、割り当て件数が一番少ないPCへ優先して割り振る
            for uname in unassigned_usernames:
                target_pc = min(pc_counts, key=pc_counts.get)
                cursor.execute(f"UPDATE accounts SET assigned_pc={p} WHERE username={p}", (target_pc, uname))
                pc_counts[target_pc] += 1
            if db.db_type == "postgres":
                conn.commit()
            logger.success(f"✅ 新規アカウントの割り当て完了。最新の担当状況: {pc_counts}")
        else:
            logger.info(f"ℹ️ すべてのアカウントが既に割り当て済みです。既存の割り当てを100%固定・維持します: {pc_counts}")
    except Exception as e:
        logger.warning(f"事前割り当て失敗（既存の割り当て設定のまま実行します）: {e}")

    # このPCの担当件数を確定
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        p = db._placeholder()
        cursor.execute(f"SELECT COUNT(*) FROM accounts WHERE selected=1 AND is_alive=1 AND assigned_pc={p}", (db.pc_name,))
        row = cursor.fetchone()
        my_target_count = list(row.values())[0] if isinstance(row, dict) else row[0]
    except Exception as e:
        logger.warning(f"担当件数の取得失敗: {e}")
        my_target_count = len(targets) // max(1, num_pcs)

    total_needed = args.total_count or my_target_count
    logger.info(f"📊 このPC({db.pc_name})の担当アカウント数: {total_needed} 件 / 全{num_pcs}台中")

    controller = IXBrowserController()
    controller.wait_until_api_ready(timeout=60)
    success_count = 0
    fail_count = 0
    success_accounts = []
    fail_accounts = []

    # Load batch size from config
    batch_size = 5
    try:
        if os.path.exists('config.json'):
            with open('config.json', 'r', encoding='utf-8') as f:
                cfg = json.load(f)
                batch_size = cfg.get("MAX_WORKERS", 5)
    except Exception as e:
        logger.warning(f"Failed to load batch size from config.json: {e}")

    # 起動時の割り当てターゲットのユーザー名リスト（スナップショット）を取得して固定する
    my_target_usernames = []
    try:
        conn = db.get_connection()
        cursor = conn.cursor()
        p = db._placeholder()
        # 起動時の selected=1 AND is_alive=1 且つ、このPCが担当するアカウントのリスト
        cursor.execute(f"SELECT username FROM accounts WHERE selected=1 AND is_alive=1 AND assigned_pc={p}", (db.pc_name,))
        rows = cursor.fetchall()
        my_target_usernames = [r['username'] if isinstance(r, dict) else r[0] for r in rows]
        logger.info(f"🔒 起動時割り当てターゲットのスナップショットを作成しました ({len(my_target_usernames)} 件)")
    except Exception as e:
        logger.warning(f"起動時ターゲットリストの取得失敗 (動的フォールバックモードで続行): {e}")
        my_target_usernames = None

    processed_count = 0
    retry_count = 0
    while processed_count < total_needed:
        # Get next batch of available accounts by claiming them
        chunk = []
        for _ in range(batch_size):
            if processed_count + len(chunk) >= total_needed:
                break
            acc = db.get_next_account(my_target_usernames)
            if acc:
                # Rename 'username' to 'screen_name' for compatibility with existing code
                acc['screen_name'] = acc['username']
                chunk.append(acc)
            else:
                break
        
        if not chunk:
            if processed_count == 0:
                logger.warning("No available accounts to claim. They might be already in use by other PCs or not selected.")
            else:
                logger.info("No more accounts available to claim. Finishing...")
            break

        # Progress display in console title
        if sys.platform == 'win32':
            os.system(f'title D-BOT [全:{total_needed} 完了:{success_count} 失敗:{fail_count}]')

        logger.info(f"\n" + "="*60)
        logger.info(f"🚀 進捗状況: 全 {total_needed} アカウント中 {processed_count} 件処理開始 (Distributed Mode)")
        logger.info(f"✅ 完了済み: {success_count} | ❌ 失敗: {fail_count}")
        logger.info("="*60 + "\n")

        if not args.skip_ip:
            update_progress(total_needed, success_count, fail_count, "IP回転中...", success_accounts, fail_accounts)
            logger.info(f"--- Starting Batch IP Rotation (New Android Script) ---")
            if reset_mobile_data():
                logger.success("IP Rotation successful.")
                controller.wait_until_api_ready(timeout=60)
            else:
                logger.error("IP Rotation failed. Aborting batch for safety.")
                # Release claimed accounts since we are skipping this batch
                for acc in chunk:
                    db.release_account(acc['screen_name'])
                continue

        update_progress(total_needed, success_count, fail_count, "実行中", success_accounts, fail_accounts)
        logger.info(f"Processing batch of {len(chunk)} accounts in parallel...")
        with ThreadPoolExecutor(max_workers=batch_size) as executor:
            future_to_acc = {executor.submit(process_single_account, acc, processed_count+j, total_needed, args, controller, ai_gen, db): acc.get('screen_name') for j, acc in enumerate(chunk)}
            
            for future in concurrent.futures.as_completed(future_to_acc):
                uname = future_to_acc[future]
                try:
                    res = future.result(timeout=600)
                    success = res[0] if isinstance(res, tuple) else res
                    msg = res[1] if isinstance(res, tuple) else "Error"
                    
                    if success:
                        success_count += 1
                        success_accounts.append(uname)
                    else:
                        fail_count += 1
                        fail_accounts.append({"name": uname, "reason": msg})
                except Exception as e:
                    logger.error(f"[{uname}] Thread error: {e}")
                    fail_count += 1
                    fail_accounts.append({"name": uname, "reason": str(e)})
                    try:
                        db.update_sync_status(uname, f"実行失敗: {str(e)[:30]}")
                        db.release_account(uname)
                    except: pass
                
                processed_count += 1
                update_progress(total_needed, success_count, fail_count, "実行中", success_accounts, fail_accounts)
                if sys.platform == 'win32':
                    os.system(f'title D-BOT [全:{total_needed} 完了:{success_count} 失敗:{fail_count}]')

    # 最終結果の表示
    if sys.platform == 'win32':
        os.system(f'title D-BOT [完了!] 全:{total_needed} 完了:{success_count} 失敗:{fail_count}')
        
    logger.info("\n" + "★"*30)
    logger.success(f"全タスク完了！")
    logger.info(f"  ● 総アカウント数: {total_needed}")
    logger.info(f"  ● 実行終了（成功）: {success_count}")
    logger.info(f"  ● 失敗アカウント数: {fail_count}")
    logger.info("★"*30 + "\n")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Stopped by user.")
    except Exception as e:
        logger.exception(f"Fatal Error: {e}")
        print("Press Enter to exit...")
        input()