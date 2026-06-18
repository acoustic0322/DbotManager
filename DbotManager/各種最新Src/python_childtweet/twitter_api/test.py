import asyncio
import json
import random
import re
import time
from datetime import datetime
from typing import Any

from curl_cffi.requests import AsyncSession

from twitter_api import TwitterAPI


AUTH_TOKEN = "Bearer AAAAAAAAAAAAAAAAAAAAANRILgAAAAAAnNwIzUejRCOuH5E6I8xnZz4puTs%3D1Zv7ttfk8LF81IUq16cHjhLTvJu4FA33AGWWjCpTnA"
CSRF_TOKEN = "260ec4d6787d928a43a2cad143c350a059eb4e5cd599c9a6a868fea14fe9005f24fc2908b94285a65e78606ef524932bc9916b927e4634d51bf83d501cf73999d53060088c5bf994db1f2c93b4204d56"
COOKIES = 'guest_id_marketing=v1%3A177980626335485583; guest_id_ads=v1%3A177980626335485583; guest_id=v1%3A177980626335485583; personalization_id="v1_DittWsUSHvi47Ztzk3wFSg=="; __cuid=5bf42944-7375-4222-bd76-14eae9057d38; __cuid=5bf42944-7375-4222-bd76-14eae9057d38; g_state={"i_l":0,"i_ll":1779806267743,"i_b":"QlWB6p8YtLgRAU7/FlIWnqT2Pwij0d4/cAhnK17maBg","i_e":{"enable_itp_optimization":0},"i_et":1779806267636}; auth_token=2d8bfd6a4db81b4f2a57181da2febe870ef8c70e; lang=ja; twid=u%3D454898265; ct0=260ec4d6787d928a43a2cad143c350a059eb4e5cd599c9a6a868fea14fe9005f24fc2908b94285a65e78606ef524932bc9916b927e4634d51bf83d501cf73999d53060088c5bf994db1f2c93b4204d56'
DEFAULT_TWEET_ID = "2008834917497803068"
LIKE_ACCOUNT_DB_PATH = "like_accounts.db"
ACCOUNT_ACTION_DELAY_SECONDS_MIN = 3
ACCOUNT_ACTION_DELAY_SECONDS_MAX = 5
ACCOUNT_PARALLEL_LIMIT = 40


def extract_tweet_id(url_or_id: str) -> str:
    value = url_or_id.strip()
    if value.isdigit():
        return value

    match = re.search(r"/status/(\d+)", value)
    return match.group(1) if match else value


def normalize_proxy(proxy: str | None) -> str | None:
    if proxy and proxy.upper().startswith("SOCKS5://"):
        return proxy.replace("SOCKS5://", "socks5h://", 1)
    return proxy


def parse_cookie_string(cookie_str: str) -> dict[str, str]:
    cookies = {}
    for cookie_pair in cookie_str.split("; "):
        if "=" in cookie_pair:
            key, value = cookie_pair.split("=", 1)
            cookies[key.strip()] = value.strip()
    return cookies


def get_device_label(user_agent: str | None) -> str:
    if not user_agent:
        return "Default"
    if "iPhone" in user_agent or "iPad" in user_agent:
        return "iOS"
    if "Android" in user_agent:
        return "Android"
    return "Desktop"


def load_first_account() -> dict[str, Any] | None:
    from database import AccountDB

    accounts = AccountDB(LIKE_ACCOUNT_DB_PATH).get_active_accounts()
    return accounts[0] if accounts else None


def build_runtime_context(account: dict[str, Any] | None = None) -> dict[str, Any]:
    from user_agents import get_impersonate_for_ua, get_sec_ch_ua, get_ua_for_account

    if account:
        cookies = account["cookies"]
        account_id = int(account.get("id", 0))
        user_agent, _ = get_ua_for_account(account_id)
        browser = get_impersonate_for_ua(user_agent)
        sec_ch_ua = get_sec_ch_ua(user_agent)
        proxy = normalize_proxy(account.get("proxy"))
        screen_name = account.get("screen_name")
    else:
        cookies = parse_cookie_string(COOKIES)
        user_agent = None
        browser = "chrome142"
        sec_ch_ua = None
        proxy = None
        screen_name = None

    csrf_token = cookies.get("ct0", CSRF_TOKEN)
    proxies = {"http": proxy, "https": proxy} if proxy else None
    api = TwitterAPI(
        AUTH_TOKEN,
        csrf_token,
        cookies,
        proxy=proxy,
        user_agent=user_agent,
        sec_ch_ua=sec_ch_ua,
    )

    return {
        "account": account,
        "screen_name": screen_name,
        "cookies": cookies,
        "csrf_token": csrf_token,
        "user_agent": user_agent,
        "browser": browser,
        "sec_ch_ua": sec_ch_ua,
        "proxy": proxy,
        "proxies": proxies,
        "api": api,
    }


def print_runtime_context(ctx: dict[str, Any]) -> None:
    account = ctx.get("account")
    if account:
        print(f"[User] DB account: @{account['screen_name']}")
    else:
        print("[WARN] No DB account. Using constant COOKIES.")

    print(f"[UA] [{get_device_label(ctx['user_agent'])}] impersonate={ctx['browser']}")
    if ctx["user_agent"]:
        print(f"     {ctx['user_agent']}")
    print(f"[CH] {ctx['sec_ch_ua'] if ctx['sec_ch_ua'] else 'None'}")
    print(f"[Proxy] {ctx['proxy'] if ctx['proxy'] else 'None'}")


def get_default_referer(ctx: dict[str, Any]) -> str:
    if ctx.get("screen_name"):
        return f"https://x.com/{ctx['screen_name']}/likes"
    return "https://x.com/home"


def save_cookies_if_needed(ctx: dict[str, Any]) -> None:
    account = ctx.get("account")
    api = ctx["api"]
    if not account or not isinstance(api.cookies, dict):
        return

    from database import AccountDB

    account["cookies"].update(api.cookies)
    AccountDB(LIKE_ACCOUNT_DB_PATH).update_cookies(account["id"], account["cookies"])
    print(f"[Saved] CookieをDBに保存しました (@{account['screen_name']})")


def get_action_failure_reason(ctx: dict[str, Any], action: str) -> str:
    reason = getattr(ctx["api"], "last_error_summary", None)
    if reason:
        return reason
    if "auth_token" not in ctx["cookies"]:
        return "auth_token missing in cookies"
    if not ctx.get("csrf_token"):
        return "ct0/csrf token missing in cookies"
    return f"{action} returned False without explicit API error"


def append_failed_action_log(
    ctx: dict[str, Any],
    tweet_id: str,
    action: str,
    reason: str,
    result_snapshot: dict[str, Any] | None = None,
) -> None:
    account = ctx.get("account") or {}
    record = {
        "account_id": account.get("id"),
        "tweet_id": tweet_id,
        "execution_type": action,
        "reason": reason,
    }
    if result_snapshot:
        record["result_snapshot"] = {
            key: value
            for key, value in result_snapshot.items()
            if key in {
                "impression",
                "like",
                "bookmark",
                "impression_reason",
                "like_reason",
                "bookmark_reason",
            }
        }
    with open("failed_actions.jsonl", "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
    with open("failed_actions.txt", "a", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"account_id: {record['account_id']}\n")
        f.write(f"tweet_id: {record['tweet_id']}\n")
        f.write(f"execution_type: {record['execution_type']}\n")
        f.write(f"reason: {record['reason']}\n\n")
    print(
        f"[DIAG] account_id={record['account_id']} "
        f"execution_type={record['execution_type']} "
        f"reason={record['reason']}"
    )
    return


def log_failed_actions(ctx: dict[str, Any], tweet_id: str, results: dict[str, Any]) -> None:
    for action in ("impression", "like", "bookmark"):
        if action in results and not results.get(action):
            reason = results.get(f"{action}_reason") or get_action_failure_reason(ctx, action)
            append_failed_action_log(
                ctx,
                tweet_id,
                action,
                reason,
                results,
            )


async def test_single_like(tweet_id: str | None = None) -> bool:
    tweet_id = tweet_id or DEFAULT_TWEET_ID
    print("\n" + "=" * 50)
    print("テスト: 単体いいね")
    print("=" * 50)

    ctx = build_runtime_context(load_first_account())
    print_runtime_context(ctx)

    async with AsyncSession(
        impersonate=ctx["browser"],
        cookies=ctx["cookies"],
        proxies=ctx["proxies"],
    ) as session:
        result = await ctx["api"].like_tweet(
            tweet_id,
            session,
            referer=get_default_referer(ctx),
        )

    save_cookies_if_needed(ctx)
    if not result:
        append_failed_action_log(
            ctx,
            tweet_id,
            "like",
            get_action_failure_reason(ctx, "like"),
            {"like": result},
        )
    print("[OK] いいね成功" if result else "[NG] いいね失敗")
    return result


async def test_single_bookmark(tweet_id: str | None = None) -> bool:
    tweet_id = tweet_id or DEFAULT_TWEET_ID
    print("\n" + "=" * 50)
    print("テスト: 単体ブックマーク")
    print("=" * 50)

    ctx = build_runtime_context(load_first_account())
    print_runtime_context(ctx)

    async with AsyncSession(
        impersonate=ctx["browser"],
        cookies=ctx["cookies"],
        proxies=ctx["proxies"],
    ) as session:
        result = await ctx["api"].bookmark_tweet(
            tweet_id,
            session,
            referer=get_default_referer(ctx),
        )

    save_cookies_if_needed(ctx)
    if not result:
        append_failed_action_log(
            ctx,
            tweet_id,
            "bookmark",
            get_action_failure_reason(ctx, "bookmark"),
            {"bookmark": result},
        )
    print("[OK] ブックマーク成功" if result else "[NG] ブックマーク失敗")
    return result


async def test_natural_action(tweet_id: str | None = None) -> dict[str, bool]:
    tweet_id = tweet_id or DEFAULT_TWEET_ID
    print("\n" + "=" * 50)
    print("テスト: 自然フロー（いいね + ブックマーク）")
    print("=" * 50)

    ctx = build_runtime_context(load_first_account())
    print_runtime_context(ctx)

    async with AsyncSession(
        impersonate=ctx["browser"],
        cookies=ctx["cookies"],
        proxies=ctx["proxies"],
    ) as session:
        results = await ctx["api"].natural_action(
            tweet_id,
            session,
            do_like=True,
            do_bookmark=True,
        )

    save_cookies_if_needed(ctx)
    log_failed_actions(ctx, tweet_id, results)
    print("\n結果:")
    print(f"  インプレッション: {'[OK] 成功' if results.get('impression') else '[NG] 失敗'}")
    print(f"  いいね: {'[OK] 成功' if results.get('like') else '[NG] 失敗'}")
    print(f"  ブックマーク: {'[OK] 成功' if results.get('bookmark') else '[NG] 失敗'}")
    return results


async def test_check_ip() -> None:
    print("\n" + "=" * 50)
    print("Test: IP check")
    print("=" * 50)

    account = load_first_account()
    if not account:
        print("[ERROR] DB縺ｫ繧｢繧ｫ繧ｦ繝ｳ繝医′縺ゅｊ縺ｾ縺帙ｓ")
        return

    proxy = normalize_proxy(account.get("proxy"))
    print(f"[User] @{account['screen_name']}")
    print(f"[Proxy] {proxy if proxy else 'None'}")

    try:
        async with AsyncSession(proxy=proxy) as session:
            response = await session.get("https://api.ipify.org?format=json", timeout=15)
            print(f"[IP] {response.text}")
    except Exception as exc:
        print(f"[ERROR] IP確認失敗: {type(exc).__name__}: {exc}")


async def test_multiple_tweets(tweet_id: str | None = None) -> list[dict[str, bool]]:
    print("\n" + "=" * 50)
    print("テスト: 複数ツイート自然フロー")
    print("=" * 50)

    tweet_ids = [tweet_id or DEFAULT_TWEET_ID]
    extra = input("追加のURL/IDをカンマ区切りで入力（空欄なら1件のみ）: ").strip()
    if extra:
        tweet_ids.extend(extract_tweet_id(value) for value in extra.split(",") if value.strip())

    results = []
    for index, target_id in enumerate(tweet_ids, start=1):
        print(f"\n[{index}/{len(tweet_ids)}] Tweet ID: {target_id}")
        results.append(await test_natural_action(target_id))
        if index < len(tweet_ids):
            await asyncio.sleep(3)
    return results


async def test_concurrent_processing(tweet_id: str | None = None) -> list[dict[str, Any]]:
    """Process active accounts in small parallel batches."""
    tweet_id = tweet_id or DEFAULT_TWEET_ID
    print("\n" + "=" * 50)
    print(f"テスト: アカウント並列処理（バッチサイズ {ACCOUNT_PARALLEL_LIMIT}）")
    print("=" * 50)

    from database import AccountDB

    accounts = AccountDB(LIKE_ACCOUNT_DB_PATH).get_active_accounts()
    if not accounts:
        print("[ERROR] DB縺ｫ繧｢繧ｫ繧ｦ繝ｳ繝医′縺ゅｊ縺ｾ縺帙ｓ")
        return []

    total_accounts = len(accounts)
    random.shuffle(accounts)

    raw_limit = input(f"実行アカウント数 (空欄なら全{total_accounts}件): ").strip()
    if raw_limit:
        try:
            account_limit = int(raw_limit)
            if account_limit <= 0:
                raise ValueError
            accounts = accounts[:account_limit]
        except ValueError:
            print(f"[WARN] 入力が不正です。全{total_accounts}件で実行します。")

    async def process_account(account: dict[str, Any], account_num: int) -> dict[str, Any]:
        started_at = time.time()
        try:
            print(f"[{account_num}] @{account['screen_name']} start")
            ctx = build_runtime_context(account)
            print_runtime_context(ctx)

            if not ctx["csrf_token"]:
                raise ValueError("CSRF token (ct0) is missing in cookies")
            if "auth_token" not in ctx["cookies"]:
                raise ValueError("auth_token is missing in cookies")

            async with AsyncSession(
                impersonate=ctx["browser"],
                cookies=ctx["cookies"],
                proxies=ctx["proxies"],
            ) as session:
                action_result = await ctx["api"].natural_action(
                    tweet_id,
                    session,
                    do_like=True,
                    do_bookmark=True,
                )

            save_cookies_if_needed(ctx)
            impression_ok = bool(action_result.get("impression"))
            like_ok = bool(action_result.get("like"))
            bookmark_ok = bool(action_result.get("bookmark"))
            log_failed_actions(ctx, tweet_id, action_result)
            return {
                "account": account["screen_name"],
                "success": like_ok and bookmark_ok,
                "elapsed": time.time() - started_at,
                "account_num": account_num,
                "impression": impression_ok,
                "like": like_ok,
                "bookmark": bookmark_ok,
            }
        except Exception as exc:
            print(f"[ERROR] @{account['screen_name']}: {type(exc).__name__}: {exc}")
            return {
                "account": account["screen_name"],
                "success": False,
                "elapsed": time.time() - started_at,
                "account_num": account_num,
                "error_type": type(exc).__name__,
                "error": str(exc),
            }

    results = []
    indexed_accounts = list(enumerate(accounts, start=1))
    for batch_start in range(0, len(indexed_accounts), ACCOUNT_PARALLEL_LIMIT):
        batch = indexed_accounts[batch_start:batch_start + ACCOUNT_PARALLEL_LIMIT]
        batch_label = f"{batch[0][0]}-{batch[-1][0]}"
        print(f"[BATCH] アカウント処理中 {batch_label} / {len(accounts)}")
        batch_results = await asyncio.gather(
            *(process_account(account, index) for index, account in batch)
        )
        results.extend(batch_results)

        if any(
            "error" in result and any(
                marker in result["error"]
                for marker in ("TID Server", "Node.js executable not found", "WinError 2", "FileNotFoundError")
            )
            for result in batch_results
        ):
            print("[STOP] Node.js/TIDサーバーエラーを検知したため、以降の処理を停止します。")
            break

        if batch_start + ACCOUNT_PARALLEL_LIMIT < len(indexed_accounts):
            wait_seconds = random.uniform(ACCOUNT_ACTION_DELAY_SECONDS_MIN, ACCOUNT_ACTION_DELAY_SECONDS_MAX)
            print(f"[WAIT] 次のバッチまで {wait_seconds:.1f} 秒...")
            await asyncio.sleep(wait_seconds)

    print("\n結果:")
    for result in results:
        status = "[OK]" if result["success"] else "[NG]"
        print(f"{result['account_num']}. @{result['account']}: {status} ({result['elapsed']:.2f}s)")
        if "like" in result:
            print(f"   インプレッション={result.get('impression')} いいね={result['like']} ブックマーク={result['bookmark']}")
        if "error" in result:
            print(f"   {result['error_type']}: {result['error']}")

    print(f"\n成功: {sum(1 for item in results if item['success'])}/{len(results)}")
    return results


async def test_impression_preflight(tweet_id: str | None = None) -> list[dict[str, Any]]:
    """Check impression TID readiness without sending client_event."""
    tweet_id = tweet_id or DEFAULT_TWEET_ID
    print("\n" + "=" * 50)
    print("Test: impression-only preflight (no send)")
    print("=" * 50)

    raw_limit = input("Check account count (default 10): ").strip()
    try:
        limit = int(raw_limit) if raw_limit else 10
    except ValueError:
        limit = 10

    from database import AccountDB

    accounts = AccountDB(LIKE_ACCOUNT_DB_PATH).get_active_accounts()[:max(1, limit)]
    if not accounts:
        print("[ERROR] DB縺ｫ繧｢繧ｫ繧ｦ繝ｳ繝医′縺ゅｊ縺ｾ縺帙ｓ")
        return []

    candidates = [
        "/i/api/1.1/jot/client_event.json",
        "/1.1/jot/client_event.json",
    ]

    async def process_account(account: dict[str, Any], account_num: int) -> dict[str, Any]:
        started_at = time.time()
        ctx = build_runtime_context(account)
        print(f"[{account_num}] @{account['screen_name']} preflight")
        print_runtime_context(ctx)

        generated = []
        for path in candidates:
            tid = await ctx["api"]._generate_client_event_transaction_id(path, "POST")
            generated.append({
                "path": path,
                "ok": bool(tid),
                "tid_preview": f"{tid[:8]}...{tid[-8:]}" if tid else None,
                "reason": None if tid else getattr(ctx["api"], "last_error_summary", None),
            })

        ok = any(item["ok"] for item in generated)
        return {
            "account": account["screen_name"],
            "account_num": account_num,
            "success": ok,
            "elapsed": time.time() - started_at,
            "generated": generated,
            "tweet_id": tweet_id,
        }

    results = await asyncio.gather(
        *(process_account(account, index) for index, account in enumerate(accounts, start=1))
    )

    print("\nResult:")
    for result in results:
        status = "[OK]" if result["success"] else "[NG]"
        print(f"{result['account_num']}. @{result['account']}: {status} ({result['elapsed']:.2f}s)")
        for item in result["generated"]:
            if item["ok"]:
                print(f"   {item['path']}: TID OK {item['tid_preview']}")
            else:
                print(f"   {item['path']}: TID NG {item['reason']}")

    print(f"\nPreflight OK: {sum(1 for item in results if item['success'])}/{len(results)}")
    print("[INFO] No client_event request was sent.")
    return results


async def test_debug_comparison() -> None:
    print("\n" + "=" * 50)
    print("Debug: runtime context")
    print("=" * 50)
    print_runtime_context(build_runtime_context(load_first_account()))


async def test_speed_benchmark() -> None:
    print("\n" + "=" * 50)
    print("ベンチマーク")
    print("=" * 50)
    started_at = time.time()
    await test_debug_comparison()
    print(f"[TIME] 実行環境確認: {time.time() - started_at:.2f}s")


async def test_db_persistence(tweet_id: str | None = None) -> None:
    tweet_id = tweet_id or DEFAULT_TWEET_ID
    print("\n" + "=" * 50)
    print("テスト: DB保存 + Cookie更新")
    print("=" * 50)

    from database import AccountDB

    db = AccountDB(LIKE_ACCOUNT_DB_PATH)
    test_user_name = "test_user_001"
    db.upsert_account(test_user_name, parse_cookie_string(COOKIES), proxy=None)

    accounts = db.get_active_accounts()
    target_account = next((account for account in accounts if account["screen_name"] == test_user_name), None)
    if not target_account and accounts:
        target_account = accounts[0]
        print(f"[WARN] {test_user_name} not found, using @{target_account['screen_name']}")
    if not target_account:
        print("[ERROR] DB縺ｫ繧｢繧ｫ繧ｦ繝ｳ繝医′縺ゅｊ縺ｾ縺帙ｓ")
        return

    ctx = build_runtime_context(target_account)
    print_runtime_context(ctx)

    async with AsyncSession(
        impersonate=ctx["browser"],
        cookies=ctx["cookies"],
        proxies=ctx["proxies"],
    ) as session:
        await ctx["api"].natural_action(
            tweet_id,
            session,
            do_like=True,
            do_bookmark=False,
        )

    save_cookies_if_needed(ctx)


def prompt_tweet_id(choice: str) -> str | None:
    if choice == "10":
        return None

    print("\nツイートURLまたはIDを入力してください")
    print("例: https://x.com/username/status/1234567890")
    print("例: 1234567890")
    print(f"空欄ならデフォルト: {DEFAULT_TWEET_ID}")

    value = input("\nURL/ID: ").strip()
    tweet_id = extract_tweet_id(value) if value else DEFAULT_TWEET_ID
    print(f"[INFO] Tweet ID: {tweet_id}")
    return tweet_id


async def main() -> None:
    print("=" * 50)
    print("X API テストランナー")
    print("=" * 50)
    print("1: 単体いいね")
    print("2: 単体ブックマーク")
    print("3: 自然フロー")
    print("4: 複数ツイート")
    print("5: アカウント並列処理（件数指定可）")
    print("6: ベンチマーク")
    print("7: メインテスト一括実行")
    print("8: 実行環境デバッグ")
    print("9: DB保存テスト")
    print("10: IP確認")
    print("11: インプレッション事前確認（送信なし）")

    choice = input("\n選択 (1-11): ").strip()
    tweet_id = prompt_tweet_id(choice)

    if choice == "1":
        await test_single_like(tweet_id)
    elif choice == "2":
        await test_single_bookmark(tweet_id)
    elif choice == "3":
        await test_natural_action(tweet_id)
    elif choice == "4":
        await test_multiple_tweets(tweet_id)
    elif choice == "5":
        await test_concurrent_processing(tweet_id)
    elif choice == "6":
        await test_speed_benchmark()
    elif choice == "7":
        await test_single_like(tweet_id)
        await asyncio.sleep(2)
        await test_single_bookmark(tweet_id)
        await asyncio.sleep(2)
        await test_natural_action(tweet_id)
    elif choice == "8":
        await test_debug_comparison()
    elif choice == "9":
        await test_db_persistence(tweet_id)
    elif choice == "10":
        await test_check_ip()
    elif choice == "11":
        await test_impression_preflight(tweet_id)
    else:
        print("無効な選択です")

    print("\n" + "=" * 50)
    print("テスト完了")
    print("=" * 50)


if __name__ == "__main__":
    try:
        if asyncio.get_event_loop_policy().__class__.__name__ == "WindowsProactorEventLoopPolicy":
            asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n中断されました")
    except Exception as exc:
        print(f"\nエラーが発生しました: {type(exc).__name__}: {exc}")
        import traceback

        traceback.print_exc()
    finally:
        input("\nEnterキーで終了...")
