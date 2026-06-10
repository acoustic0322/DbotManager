import asyncio
import os
import random
import json
from datetime import datetime, time, timedelta
from curl_cffi.requests import AsyncSession
from database import AccountDB
from tweet import Tweeter
from user_agents import get_ua_for_account, get_sec_ch_ua

# 投稿設定
IMAGE_DIR = "投稿画像"
AUTH_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
IMAGE_PROBABILITY = 0.5  # 画像を添付する確率 (50%)
DEFAULT_LIMIT_COUNT_MIN = 3  # 上限回数が0または未設定の場合の最小投稿回数 (1日あたり)
DEFAULT_LIMIT_COUNT_MAX = 5  # 上限回数が0または未設定の場合の最大投稿回数 (1日あたり)

# 常駐ループの巡回間隔（秒）
CHECK_INTERVAL_SECONDS = 30

def normalize_proxy(proxy: str | None) -> str | None:
    if proxy and proxy.upper().startswith("SOCKS5://"):
        return proxy.replace("SOCKS5://", "socks5h://", 1)
    return proxy

def append_failed_tweet_log(account: dict, tweet_text: str, image_path: str | None, sheet_name: str | None, reason: str, diagnostics: dict | None):
    record = {
        "timestamp": datetime.now().isoformat(timespec="seconds"),
        "account_id": account.get("id"),
        "screen_name": account.get("screen_name"),
        "sheet_name": sheet_name,
        "tweet_text": tweet_text,
        "text_length": len(tweet_text or ""),
        "image_path": image_path,
        "reason": reason,
        "diagnostics": diagnostics or {},
    }
    with open("failed_tweets.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")

def is_time_in_range(time_range: str) -> bool:
    """現在時刻が指定された時間帯（例: '1:00～23:00'）の範囲内か判定する"""
    if not time_range:
        return True # 設定がなければ制限なし
        
    try:
        current_time = datetime.now().time()
        
        # 各種区切り文字に対応
        for sep in ('～', '〜', '-'):
            if sep in time_range:
                start_str, end_str = time_range.split(sep)
                break
        else:
            return True # 区切り文字がなければ制限なし
            
        def parse_time(t_str):
            t_str = t_str.strip()
            h, m = map(int, t_str.split(':'))
            return time(h, m)
            
        start_time = parse_time(start_str)
        end_time = parse_time(end_str)
        
        if start_time <= end_time:
            return start_time <= current_time <= end_time
        else:
            # 日をまたぐ場合（例: 22:00～5:00）
            return current_time >= start_time or current_time <= end_time
    except Exception as e:
        print(f"[WARN] 時間帯の解析に失敗しました ({time_range}): {e}. 時間帯チェックをスキップします。")
        return True

def get_random_image(directory: str) -> tuple[str, bool]:
    """
    指定ディレクトリからランダムに画像ファイルを取得する。
    画像がない場合はテスト用のダミー画像を一時生成して返す。
    """
    if not os.path.exists(directory):
        os.makedirs(directory)
        
    supported_extensions = ('.png', '.jpg', '.jpeg', '.gif')
    files = [
        os.path.join(directory, f) for f in os.listdir(directory)
        if f.lower().endswith(supported_extensions)
    ]
    
    if files:
        selected_image = random.choice(files)
        print(f"[IMAGE] Found {len(files)} images. Selected: '{selected_image}'")
        return selected_image, False
    else:
        print(f"[WARN] No images found in '{directory}'. Generating a fallback dummy image...")
        fallback_path = os.path.join(directory, "fallback_dummy.png")
        from PIL import Image
        img = Image.new('RGB', (100, 100), color='red')
        img.save(fallback_path)
        return fallback_path, True

def get_random_tweet_text(sheet_name: str) -> str:
    """スプレッドシートの指定したシート（A列）からランダムにツイート文を取得する"""
    try:
        from sheets_sync import get_sheet_client, SPREADSHEET_URL, TARGET_SHEET_NAME
        
        client = get_sheet_client()
        spreadsheet = client.open_by_url(SPREADSHEET_URL)
        
        # カンマや読点などで複数指定されている場合はランダムに1つ選択
        if sheet_name:
            for sep in (',', '、', '\n', '/'):
                if sep in sheet_name:
                    sheets = [s.strip() for s in sheet_name.split(sep) if s.strip()]
                    selected = random.choice(sheets)
                    print(f"[TEXT] 複数指定の中からシートをランダム選択しました: '{selected}' (全体: {sheet_name})")
                    sheet_name = selected
                    break
                    
        # シート名が未指定、または空欄の場合は、名前に「ツイート」が含まれる全シートからランダム選択
        if not sheet_name:
            worksheets = spreadsheet.worksheets()
            valid_sheets = [w.title for w in worksheets if "ツイート" in w.title]
            
            if not valid_sheets:
                raise ValueError("スプレッドシート内に名前に 'ツイート' が含まれる有効なシートが見つかりません。")
                
            sheet_name = random.choice(valid_sheets)
            print(f"[TEXT] シート名未指定のため、ツイート用シートからランダム選定しました: '{sheet_name}'")
            
        sheet = spreadsheet.worksheet(sheet_name)
            
        # A列の値を取得
        values = sheet.col_values(1)
        texts = [v.strip() for v in values if v.strip()]
        
        if not texts:
            raise ValueError(f"シート '{sheet_name}' に文章がありません。")
            
        # ヘッダー行があれば除外
        if len(texts) > 1 and texts[0] in ("ツイート本文", "tweet_text", "text", "ツイート", "文章"):
            texts = texts[1:]
            
        selected_text = random.choice(texts)
        print(f"[TEXT] Read {len(texts)} lines from sheet '{sheet_name}'. Selected: '{selected_text}'")
        return selected_text
    except Exception as e:
        fallback_text = f"テスト投稿（シート取得失敗） - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        print(f"[WARN] シート取得またはテキスト抽出に失敗しました (指定: {sheet_name}): {e}. フォールバックテキストを使用します: {fallback_text}")
        return fallback_text

def parse_limit_count(limit_val, screen_name: str) -> int:
    """
    回数制限の設定値（数値、または '3-5' などの範囲文字列）を解析し、
    具体的な回数（範囲の場合はその中からランダム）を決定して返す。
    """
    if limit_val is None:
        val_str = ""
    else:
        val_str = str(limit_val).strip()
        
    if not val_str or val_str == "0":
        limit = random.randint(DEFAULT_LIMIT_COUNT_MIN, DEFAULT_LIMIT_COUNT_MAX)
        print(f"[SCHEDULER] @{screen_name}: 上限回数が未設定のため、本日の投稿回数をランダムに {limit}回 に決定しました。")
        return limit
        
    # 各種区切り文字に対応して範囲指定をパース (例: '3～5', '3-5', '3〜5')
    for sep in ('～', '〜', '-'):
        if sep in val_str:
            try:
                parts = val_str.split(sep)
                low = int(parts[0].strip())
                high = int(parts[1].strip())
                if low <= high:
                    limit = random.randint(low, high)
                else:
                    limit = random.randint(high, low)
                print(f"[SCHEDULER] @{screen_name}: 範囲設定 '{val_str}' に基づき、本日の投稿回数を {limit}回 に決定しました。")
                return limit
            except Exception as e:
                print(f"[WARN] @{screen_name}: 回数範囲の解析に失敗しました ({val_str}): {e}")
                
    # 単一の数値の場合
    try:
        val_int = int(val_str)
        if val_int > 0:
            return val_int
    except ValueError:
        pass
        
    limit = random.randint(DEFAULT_LIMIT_COUNT_MIN, DEFAULT_LIMIT_COUNT_MAX)
    print(f"[SCHEDULER] @{screen_name}: 不正な上限設定 '{val_str}' のため、本日の投稿回数をランダムに {limit}回 に決定しました。")
    return limit

def get_max_limit_count(limit_val) -> int:
    """設定された回数上限（範囲指定含む）の最大値（上限）を取得する"""
    if limit_val is None:
        return DEFAULT_LIMIT_COUNT_MAX
    val_str = str(limit_val).strip()
    if not val_str or val_str == "0":
        return DEFAULT_LIMIT_COUNT_MAX
    for sep in ('～', '〜', '-'):
        if sep in val_str:
            try:
                parts = val_str.split(sep)
                high = int(parts[1].strip())
                return high
            except:
                pass
    try:
        return int(val_str)
    except:
        return DEFAULT_LIMIT_COUNT_MAX

def generate_today_schedule(time_range: str, limit_count_raw, today_count: int, screen_name: str) -> list[datetime]:
    """
    指定された時間帯と上限回数、および本日すでに投稿した数から、
    本日（現在時刻以降）の投稿スケジュール（datetimeのリスト）をランダムに生成する。
    """
    limit_count = parse_limit_count(limit_count_raw, screen_name)
    
    remaining_count = max(0, limit_count - today_count)
    if today_count > 0:
        print(f"[SCHEDULER] @{screen_name}: 本日すでに {today_count}回 投稿されているため、本日の残りスケジュール回数は {remaining_count}回 になります（本日目標: {limit_count}回）。")
    else:
        print(f"[SCHEDULER] @{screen_name}: 本日は {limit_count}回 投稿するようにスケジュールを設定します。")
        
    if remaining_count <= 0:
        print(f"[SCHEDULER] @{screen_name}: 本日の残り投稿枠がありません。")
        return []
        
    now = datetime.now()
    today = now.date()
    
    # 時間帯のパース (例: '1:00～23:00')
    if not time_range:
        start_time = time(0, 0)
        end_time = time(23, 59)
    else:
        try:
            for sep in ('～', '〜', '-'):
                if sep in time_range:
                    start_str, end_str = time_range.split(sep)
                    break
            else:
                raise ValueError("時間帯の区切り文字が見つかりません。")
            
            def parse_t(t_str):
                h, m = map(int, t_str.strip().split(':'))
                return time(h, m)
                
            start_time = parse_t(start_str)
            end_time = parse_t(end_str)
        except Exception as e:
            print(f"[WARN] @{screen_name}: 時間帯 '{time_range}' のパースに失敗しました: {e}。デフォルトの 0:00〜23:59 を使用します。")
            start_time = time(0, 0)
            end_time = time(23, 59)
            
    # 今日の開始と終了日時
    start_dt = datetime.combine(today, start_time)
    end_dt = datetime.combine(today, end_time)
    
    # 日を跨ぐ場合（例：22:00～5:00）の対応
    if end_dt < start_dt:
        end_dt += timedelta(days=1)
        
    # 現在時刻が既に開始日時を過ぎている場合は、現在時刻を開始基準にする
    calc_start = max(now, start_dt)
    
    # 残りの秒数
    total_seconds = (end_dt - calc_start).total_seconds()
    if total_seconds <= 60:
        print(f"[SCHEDULER] @{screen_name}: 本日の残り時間がありません。")
        return []
        
    # サブインターバルに分割して、各区間からランダムに1点選ぶ（間隔の自動確保）
    interval_seconds = total_seconds / remaining_count
    schedule = []
    
    for i in range(remaining_count):
        sub_start = calc_start + timedelta(seconds=i * interval_seconds)
        # 範囲内のランダムな秒数を選択
        random_offset = random.uniform(0, interval_seconds)
        target_dt = sub_start + timedelta(seconds=random_offset)
        schedule.append(target_dt)
        
    schedule.sort()
    return schedule

def reset_daily_count_if_needed(db: AccountDB, acc: dict, today_str: str) -> bool:
    """日付が変更されている場合、DBの本日のツイートカウントを0にリセットする"""
    last_action_time = acc.get('last_action_time')
    last_date = ""
    if last_action_time:
        if isinstance(last_action_time, str):
            last_date = last_action_time.split(" ")[0]
        else:
            last_date = last_action_time.strftime("%Y-%m-%d")
            
    if last_date != today_str:
        print(f"[RESET] @{acc['screen_name']}: 日付が変更されたため本日のカウントをリセットします (前回: {last_date or '無し'} / 本日: {today_str})")
        conn = db._get_conn()
        cursor = conn.cursor()
        cursor.execute("UPDATE accounts SET today_tweet_count = 0, last_action_time = ? WHERE id = ?", (datetime.now(), acc['id']))
        conn.commit()
        conn.close()
        acc['today_tweet_count'] = 0
        return True
    return False

async def post_for_account(acc: dict, db: AccountDB):
    """特定アカウントのツイート投稿を処理する非同期タスク"""
    screen_name = acc['screen_name']
    
    # 複数アカウントが同時にスケジュールされた場合のタイミング分散（ジッター）
    delay = random.uniform(5.0, 20.0)
    print(f"[PROCESS] @{screen_name}: 同時実行防止のため {delay:.1f}秒 待機します...")
    await asyncio.sleep(delay)
    
    sheet_name = acc.get('tweet_sheet_name')
    print(f"[PROCESS] @{screen_name}: ツイート投稿を開始します...")
    
    # 最新のDB情報を取得して再確認
    conn = db._get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT today_tweet_count, tweet_limit_count FROM accounts WHERE id = ?", (acc['id'],))
    row = cursor.fetchone()
    conn.close()
    
    today_count = acc.get('today_tweet_count', 0)
    limit_count = acc.get('tweet_limit_count', 0)
    if row:
        today_count, limit_count = row
        
    limit_count = get_max_limit_count(limit_count)
        
    if today_count >= limit_count:
        print(f"[SKIP] @{screen_name}: 本日のツイート上限 ({limit_count}回) に達しているため投稿をスキップします。")
        return
        
    # 画像の選定
    image_path = None
    is_temporary = False
    if random.random() < IMAGE_PROBABILITY:
        print(f"[{screen_name}] 50%の判定：今回は【画像付き】でツイートします。")
        image_path, is_temporary = get_random_image(IMAGE_DIR)
    else:
        print(f"[{screen_name}] 50%の判定：今回は【文章のみ】でツイートします。")
        
    try:
        current_cookies = acc['cookies']
        csrf_token = current_cookies.get("ct0", "")
        
        # User-Agentの設定
        user_agent, _imp = get_ua_for_account(int(acc.get('id', 0)))
        sec_ch_ua = get_sec_ch_ua(user_agent)
        proxy = normalize_proxy(acc.get('proxy'))
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # セッションの初期化
        async with AsyncSession(impersonate=_imp, cookies=current_cookies, proxies=proxies) as session:
            # Tweeterインスタンスの初期化
            tweeter = Tweeter(
                auth_token=AUTH_TOKEN,
                csrf_token=csrf_token,
                cookies=current_cookies,
                proxy=proxy,
                user_agent=user_agent,
                sec_ch_ua=sec_ch_ua
            )
            
            # ツイート内容をスプレッドシートからランダム取得
            tweet_text = get_random_tweet_text(sheet_name)
            
            # 投稿実行
            success = await tweeter.post_tweet(
                text=tweet_text,
                session=session,
                image_path=image_path
            )

            updated_cookies = session.cookies.get_dict()
            if isinstance(tweeter.cookies, dict):
                updated_cookies.update(tweeter.cookies)
            if updated_cookies:
                final_cookies = current_cookies.copy()
                final_cookies.update(updated_cookies)
                db.update_cookies(acc['id'], final_cookies)
                print(f"[DB] @{screen_name}: Cookieを更新しました")
            
            if success:
                new_count = today_count + 1
                print(f"[SUCCESS] @{screen_name}: ツイートの投稿に成功しました！")
                
                # DB側のカウントを更新（成功時はエラー詳細をクリア）
                conn = db._get_conn()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE accounts 
                    SET today_tweet_count = ?, last_action_time = ?, error_detail = NULL
                    WHERE id = ?
                """, (new_count, datetime.now(), acc['id']))
                conn.commit()
                conn.close()
                print(f"[DB] @{screen_name}: 更新完了: 本日のツイート数 = {new_count} (上限: {limit_count})")
            else:
                reason = getattr(tweeter, 'last_error_summary', '不明なエラー')
                diagnostics = getattr(tweeter, 'last_tweet_diagnostics', {})
                append_failed_tweet_log(acc, tweet_text, image_path, sheet_name, reason, diagnostics)
                print(f"[DIAG] @{screen_name}: 失敗診断を failed_tweets.jsonl に保存しました")
                print(f"[FAILED] @{screen_name}: ツイートの投稿に失敗しました。 【原因: {reason}】")
                
                # DBのエラー詳細を更新
                conn = db._get_conn()
                cursor = conn.cursor()
                cursor.execute("""
                    UPDATE accounts 
                    SET error_detail = ?, last_action_time = ?
                    WHERE id = ?
                """, (reason, datetime.now(), acc['id']))
                conn.commit()
                conn.close()
                
    except Exception as e:
        print(f"[ERROR] @{screen_name}: 投稿処理中にエラーが発生しました: {e}")
    finally:
        # クリーンアップ
        if is_temporary and image_path and os.path.exists(image_path):
            try:
                os.remove(image_path)
                print(f"[CLEANUP] 一時フォールバック画像を削除しました: {image_path}")
            except Exception as e:
                print(f"[WARN] 一時フォールバック画像 {image_path} の削除に失敗しました: {e}")

async def main():
    db = AccountDB()
    
    # スケジュールと日付状態の管理用
    schedules = {}          # account_id -> list of datetime (予定投稿時刻リスト)
    scheduled_dates = {}    # account_id -> date (スケジュールを立てた日付)
    
    print("==================================================")
    print("  X非公式API 自動投稿スケジューラ (常駐稼働) 起動  ")
    print("==================================================")
    
    while True:
        try:
            today = datetime.now().date()
            today_str = today.strftime("%Y-%m-%d")
            
            # 1. アクティブアカウントをDBから常に取得して最新化
            accounts = db.get_active_accounts()
            active_ids = {acc['id'] for acc in accounts}
            
            # DBで非アクティブになったアカウントのスケジュールデータをクリーンアップ
            inactive_ids = set(schedules.keys()) - active_ids
            for uid in inactive_ids:
                print(f"[INFO] アカウントID {uid} は非アクティブになったため、スケジュールから除外します。")
                schedules.pop(uid, None)
                scheduled_dates.pop(uid, None)
                
            if not accounts:
                print("[INFO] アクティブなアカウントが登録されていません。30秒後に再確認します...")
                await asyncio.sleep(30)
                continue
                
            # 2. 各アカウントのスケジュール生成・更新チェック
            for acc in accounts:
                acc_id = acc['id']
                screen_name = acc['screen_name']
                
                # 日付が変わっていたらDB側のリセットを実行
                reset_daily_count_if_needed(db, acc, today_str)
                
                # 24時間待機チェック (制限エラー：344, 226 が記録されている場合)
                error_detail = acc.get('error_detail')
                last_action_time = acc.get('last_action_time')
                if error_detail and ("344" in error_detail or "226" in error_detail):
                    if last_action_time:
                        if isinstance(last_action_time, str):
                            try:
                                if "." in last_action_time:
                                    last_time = datetime.strptime(last_action_time.split(".")[0], "%Y-%m-%d %H:%M:%S")
                                else:
                                    last_time = datetime.strptime(last_action_time, "%Y-%m-%d %H:%M:%S")
                            except Exception:
                                last_time = datetime.now() - timedelta(days=2)
                        else:
                            last_time = last_action_time
                        
                        elapsed = datetime.now() - last_time
                        if elapsed < timedelta(hours=24):
                            remaining_hours = 24 - (elapsed.total_seconds() / 3600)
                            if scheduled_dates.get(acc_id) != today or acc_id not in schedules:
                                print(f"[SCHEDULER] @{screen_name}: 制限エラー({error_detail})のため、前回の投稿試行({last_time.strftime('%Y-%m-%d %H:%M:%S')})から24時間経過するまでスケジュールをスキップします (残り: {remaining_hours:.1f}時間)")
                                schedules[acc_id] = []
                                scheduled_dates[acc_id] = today
                            continue
                
                # 新しい日になった、またはスケジュールが未生成の場合
                if scheduled_dates.get(acc_id) != today or acc_id not in schedules:
                    print(f"\n[SCHEDULER] @{screen_name} の本日のスケジュールを算出します...")
                    
                    time_range = acc.get('tweet_time_range')
                    limit_count = acc.get('tweet_limit_count', 0)
                    today_count = acc.get('today_tweet_count', 0)
                    
                    # スケジュール生成
                    today_schedule = generate_today_schedule(time_range, limit_count, today_count, screen_name)
                    schedules[acc_id] = today_schedule
                    scheduled_dates[acc_id] = today
                    
                    if today_schedule:
                        print(f"[SCHEDULER] @{screen_name} の投稿予定時刻 ({len(today_schedule)}回):")
                        for t in today_schedule:
                            print(f"  - {t.strftime('%H:%M:%S')}")
                    else:
                        print(f"[SCHEDULER] @{screen_name} 本日はこれ以上投稿予定はありません。")
            
            # 3. スケジュール時刻の監視と実行
            now = datetime.now()
            for acc in accounts:
                acc_id = acc['id']
                if acc_id not in schedules or not schedules[acc_id]:
                    continue
                    
                # 予定時刻を過ぎたものがあるか確認
                upcoming_times = schedules[acc_id]
                triggered_times = [t for t in upcoming_times if t <= now]
                
                if triggered_times:
                    # 予定をスケジュールから除外
                    schedules[acc_id] = [t for t in upcoming_times if t > now]
                    
                    # 投稿を非同期タスクとして開始（他アカウントやループ自体をブロックしない）
                    asyncio.create_task(post_for_account(acc, db))
                    
        except Exception as e:
            print(f"[CRITICAL] 常駐メインループでエラーが発生しました: {e}")
            
        await asyncio.sleep(CHECK_INTERVAL_SECONDS)

if __name__ == "__main__":
    asyncio.run(main())
