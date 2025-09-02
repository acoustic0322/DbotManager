# test2_verbose_complete.py
# -*- coding: utf-8 -*-
import os, json, re, sys, traceback, json
from typing import List, Optional, Tuple, Generator, Any

from curl_cffi import requests as requests  # ブラウザ指紋つきHTTP
from get_x_cookies_firefox import get_x_cookies_from_firefox
from datetime import datetime, timezone, timedelta

def _log(msg: str):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{now}] {msg}", flush=True)

# ============== Cookie & Session ==============
def _set_cookies(s: requests.Session, auth_token: str, ct0: str):
    for dom in [".x.com", ".twitter.com"]:
        s.cookies.set("auth_token", auth_token, domain=dom)
        s.cookies.set("ct0", ct0, domain=dom)

def _new_session() -> requests.Session:
    return requests.Session(impersonate="chrome124")  # 必要なら chrome130/119 に変更可

# ============== features / fieldToggles（既定） ==============
def _default_features() -> dict:
    return {
        "rweb_lists_timeline_redesign_enabled": True,
        "responsive_web_graphql_exclude_directive_enabled": True,
        "verified_phone_label_enabled": False,
        "creator_subscriptions_tweet_preview_api_enabled": True,
        "responsive_web_graphql_skip_user_profile_image_extensions_enabled": False,
        "tweetypie_unmention_optimization_enabled": True,
        "responsive_web_edit_tweet_api_enabled": True,
        "graphql_is_translatable_rweb_tweet_is_translatable_enabled": True,
        "view_counts_everywhere_api_enabled": True,
        "longform_notetweets_consumption_enabled": True,
        "tweet_awards_web_tipping_enabled": False,
        "freedom_of_speech_not_reach_fetch_enabled": True,
        "standardized_nudges_misinfo": True,
        "tweet_with_visibility_results_prefer_gql_limited_actions_policy_enabled": True,
        "responsive_web_graphql_timeline_navigation_enabled": True,
        "responsive_web_enhance_cards_enabled": False,
    }

def _default_field_toggles() -> dict:
    return { "withArticleRichContentState": False, "withAuxiliaryUserLabels": False }

# ============== main.js 探索 ==============
def _fetch_main_js_urls_with_session(s: requests.Session) -> List[str]:
    pages = ["https://x.com/home"]
    h = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "ja,en-US;q=0.9",
        "Referer": "https://x.com/",
    }
    rx = re.compile(r'https://abs\.twimg\.com/responsive-web/(?:client-web|client-web-legacy)/[^"]+?\.js')
    urls, seen = [], set()
    for p in pages:
        r = s.get(p, headers=h, timeout=15, allow_redirects=True)
        _log(f"[STEP] GET {p} -> {r.status_code}")
        if r.ok:
            for u in rx.findall(r.text):
                if u not in seen:
                    seen.add(u); urls.append(u)
    return urls

def _unescape_js(s: str) -> str:
    return (s.replace("\\x20", " ")
             .replace("\\x3d", "=")
             .replace("\\x2F", "/")
             .replace("\\u003d", "=")
             .replace("\\u002F", "/")
             .replace("\\u0025", "%")
             .replace("\\u0026", "&"))

# ============== Bearer 抽出 ==============
def _extract_bearer_from_js(txt: str) -> Optional[str]:
    t = _unescape_js(txt)
    patterns = [
        r'Bearer\s+([A-Za-z0-9%-]{80,})',
        r'["\']Authorization["\']\s*:\s*["\']Bearer\s*([A-Za-z0-9%-]{80,})',
        r'Bearer\\x20([A-Za-z0-9%-]{80,})',
        r'Bearer%20([A-Za-z0-9%-]{80,})',
    ]
    for pat in patterns:
        m = re.search(pat, t, flags=re.I)
        if m: return m.group(1)
    return None

def fetch_web_bearer_token_with_session(s: requests.Session) -> str:
    js_urls = _fetch_main_js_urls_with_session(s)
    _log(f"[STEP] main.js候補 {len(js_urls)} 件")
    for i, js_url in enumerate(js_urls, 1):
        r = s.get(js_url, headers={"Accept": "*/*", "Referer": "https://x.com/"}, timeout=15)
        _log(f"[STEP] ({i}) GET main.js -> {js_url} {r.status_code}")
        if not r.ok: continue
        b = _extract_bearer_from_js(r.text)
        if b:
            _log("[STEP] Bearer を JS から取得")
            return b
    _log("[WARN] Bearer 抽出失敗。固定値にフォールバックします")
    return "AAAAAAAAAAAAAAAAAAAAANRILgAAAAA7xVpN0HbUjmLZ7l1nvBfAvVw94w%3D9QoU2QAnrD6J1Yb2rZLoB6nKgnCMvO14Gw1uvn2nYzQWznnKkY"

# ============== queryId 抽出 ==============
def _extract_query_id_from_js(txt: str) -> Optional[str]:
    t = _unescape_js(txt)
    pats = [
        r'"UserTweets"\s*:\s*\{\s*"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"',
        r'"operationName"\s*:\s*"UserTweets"[^}]{0,2000}?"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"',
        r'"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"[^}]{0,2000}?"operationName"\s*:\s*"UserTweets"',
        r'/i/api/graphql/([A-Za-z0-9_-]{10,})/UserTweets',
    ]
    for pat in pats:
        m = re.search(pat, t, flags=re.I | re.DOTALL)
        if m: return m.group(1)
    return None

def fetch_usertweets_query_id_with_session(s: requests.Session) -> str:
    js_urls = _fetch_main_js_urls_with_session(s)
    for i, js_url in enumerate(js_urls, 1):
        r = s.get(js_url, headers={"Accept": "*/*", "Referer": "https://x.com/"}, timeout=15)
        if not r.ok: continue
        q = _extract_query_id_from_js(r.text)
        if q:
            _log(f"[STEP] queryId を JS から取得: {q}")
            return q
    _log("[WARN] queryId 抽出失敗。既知値にフォールバックします")
    return "jXozWifCk6Vtw7izZseDXA"  # 古い可能性あり

# ============== 日時ユーティリティ ==============

def _normalize_created_at(raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    raw: 例 'Sat May 04 06:20:38 +0000 2024' / 'Wed Aug 14 03:21:00 +0000 2025'
    戻り値: (UTC文字列, JST文字列) いずれも 'YYYY-mm-dd HH:MM:SS'
    パース不能時は (raw, None)
    """

    print("_normalize_created_at1")

    # 英語略月→数値（ロケールに依存しない）
    _MONTHS = {
        "Jan":1,"Feb":2,"Mar":3,"Apr":4,"May":5,"Jun":6,
        "Jul":7,"Aug":8,"Sep":9,"Sept":9,"Oct":10,"Nov":11,"Dec":12
    }

# 例: "Sat May 04 06:20:38 +0000 2024"
#     "Wed Aug 14 03:21:00 +0000 2025"
#     "Sat, 04 May 2024 06:20:38 +00:00" などの亜種もある程度吸収
    _RE_X_TIME = re.compile(
        r"""^\s*
            (?:[A-Za-z]{3},?\s+)?      # 先頭の曜日（任意, カンマ付も許容）
            (?:(\d{1,2})\s+)?          # 先頭に日が来るパターンも一応許容（任意）
            ([A-Za-z]{3,4})\s+         # 月 (May, Sept など)
            (\d{1,2})\s+               # 日
            (\d{2}):(\d{2}):(\d{2})\s+  # 時:分:秒
            (Z|UTC|[+-]\d{2}:?\d{2}|[+-]\d{4})\s+  # タイムゾーン
            (\d{4})                     # 年
            \s*$""",
        re.VERBOSE
    )

    print(raw)

    if not raw:
        return None, None

    print("_normalize_created_at2")

    s = raw.strip()

    # まずは元の書式での高速トライ（通ればそれでOK）
    try:
        dt = datetime.strptime(s, "%a %b %d %H:%M:%S %z %Y")
        utc = dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        jst = dt.astimezone(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")
        print("return utc, jst")
        return utc, jst
    except Exception:
        print("test")
        pass  # 落ちたらロケール非依存の正規表現パースへ

    # タイムゾーンの「+HH:MM」→「+HHMM」に正規化（strptime 互換のため）
    s_norm = re.sub(r"([+-]\d{2}):(\d{2})\b", r"\1\2", s)
    # ' Z ' / ' UTC ' を +0000 に正規化
    s_norm = re.sub(r"\b(?:Z|UTC)\b", "+0000", s_norm)

    # 正規表現でパース（ロケール非依存）
    m = _RE_X_TIME.match(s_norm)
    if m:
        # m.groups() = (opt_day_lead, mon_abbr, day, hh, mm, ss, tz, year)
        _, mon_abbr, day, hh, mm, ss, tz, year = m.groups()
        mon_abbr = mon_abbr[:4]  # 'Sept' も許容
        month = _MONTHS.get(mon_abbr)
        if month:
            # タイムゾーンを timedelta に
            if tz in ("Z", "UTC", "+0000"):
                offset = timedelta(0)
            else:
                tz_clean = tz.replace(":", "")  # +HHMM へ
                sign = 1 if tz_clean[0] == "+" else -1
                th = int(tz_clean[1:3])
                tm = int(tz_clean[3:5])
                offset = sign * timedelta(hours=th, minutes=tm)

            try:
                dt = datetime(
                    year=int(year),
                    month=month,
                    day=int(day),
                    hour=int(hh),
                    minute=int(mm),
                    second=int(ss),
                    tzinfo=timezone(offset),
                )
                utc = dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
                jst = dt.astimezone(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")
                return utc, jst
            except Exception:
                pass

    # 最後の保険：そのまま返す
    return s, None


def _normalize_created_at_bk1(raw: Optional[str]) -> Tuple[Optional[str], Optional[str]]:
    """
    raw: 'Wed Aug 14 03:21:00 +0000 2025' のようなXの標準形式想定
    戻り値: (UTC文字列, JST文字列) いずれも 'YYYY-mm-dd HH:MM:SS' 形式
    """


    if not raw:
        return None, None
    try:
        dt = datetime.strptime(raw, "%a %b %d %H:%M:%S %z %Y")
        utc = dt.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        jst = dt.astimezone(timezone(timedelta(hours=9))).strftime("%Y-%m-%d %H:%M:%S")
        return utc, jst
    except Exception:
        # 解析できない場合はそのまま返す
        return raw, None

# ============== 汎用ツイート抽出（created_at対応） ==============
def _extract_basic_from_legacy_like(node: dict) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    """
    node: legacyに似た構造を想定
    戻り値: (tweet_id, text, created_at_raw)
    """
    if not isinstance(node, dict):
        return None, None, None
    tid = node.get("id_str") or node.get("rest_id")
    text = node.get("full_text") or node.get("text")
    created = node.get("created_at")
    return tid, text, created

def _extract_from_tweet_node(node: dict) -> Optional[Tuple[str, str, Optional[str]]]:
    # パターン1: 直Tweet
    legacy = node.get("legacy")
    rest_id = node.get("rest_id") or (legacy or {}).get("id_str")
    if rest_id:
        text = (legacy or {}).get("full_text") or (node.get("note_tweet_results", {}).get("result", {}) or {}).get("text") or node.get("text")
        created_at = (legacy or {}).get("created_at")
        if text:
            print("created1")
            print(created_at)
            return rest_id, text, created_at
    # パターン2: TweetWithVisibilityResults
    tw = node.get("tweet")
    if isinstance(tw, dict):
        leg2 = tw.get("legacy")
        rest_id = tw.get("rest_id") or (leg2 or {}).get("id_str")
        if rest_id:
            text = (leg2 or {}).get("full_text") or (tw.get("note_tweet_results", {}).get("result", {}) or {}).get("text") or tw.get("text")
            created_at = (leg2 or {}).get("created_at")
            if text:
                print("created2")
                print(created_at)
                return rest_id, text, created_at
    return None

    from typing import Any, Optional

def _find_created_nearby(context: Any, target_id: str) -> Optional[str]:
    """
    同じレスポンスJSON内を再帰スキャンし、target_id に一致する
    legacy.id_str/rest_id の created_at を返す（最初に見つかった1件）。
    """
    target_id = str(target_id)
    found: Optional[str] = None

    def walk(x: Any):
        nonlocal found
        if found is not None:
            return
        if isinstance(x, dict):
            legacy = x.get("legacy")
            if isinstance(legacy, dict):
                tid = x.get("rest_id") or legacy.get("id_str")
                if tid is not None and str(tid) == target_id:
                    ca = legacy.get("created_at")
                    if ca:
                        found = ca
                        return
            # 続きを探索
            for v in x.values():
                if found is None:
                    walk(v)
        elif isinstance(x, list):
            for v in x:
                if found is None:
                    walk(v)

    walk(context)
    print("found")
    print(found)

    return found


def _yield_tweet_candidates(obj: Any):
    """
    (tweet_id, text, created_at) を yield。
    _extract_from_tweet_node が created_at を返せない場合は、
    同一JSON内をスキャンして補完する。
    """

    try:
        if isinstance(obj, dict):
            # 1) tweet_results.result -> 最有力
            tr = obj.get("tweet_results")
            if isinstance(tr, dict):
                print("_yield_tweet_candidates:1")
                res = tr.get("result") or {}
                cand = _extract_from_tweet_node(res)
                if cand:
                    print(cand)
                    rid, text, created_at = cand
                    if not created_at:
                        created_at = _find_created_nearby(obj, rid) or _find_created_nearby(res, rid)
                    yield (rid, text, created_at)

            # 2) この dict 自身が Tweet node の場合
#            print("_yield_tweet_candidates:2")
            cand2 = _extract_from_tweet_node(obj)
            if cand2:
                print(cand2)
                rid, text, created_at = cand2
                if not created_at:
                    created_at = _find_created_nearby(obj, rid)
                yield (rid, text, created_at)

            # 3) よくある容器の中を辿る
            tm = obj.get("timelineModule")
            if isinstance(tm, dict):
                for it in tm.get("items", []):
                    yield from _yield_tweet_candidates(it)

            content = obj.get("content")
            if isinstance(content, dict):
                ic = content.get("itemContent")
                if isinstance(ic, dict):
                    yield from _yield_tweet_candidates(ic)

            item = obj.get("item")
            if isinstance(item, dict):
                yield from _yield_tweet_candidates(item)

            moduleItems = obj.get("moduleItems")
            if isinstance(moduleItems, list):
                for it in moduleItems:
                    yield from _yield_tweet_candidates(it)

            # 4) 汎用再帰（最後）
            for v in obj.values():
                yield from _yield_tweet_candidates(v)

        elif isinstance(obj, list):
            for v in obj:
                yield from _yield_tweet_candidates(v)
    except Exception:
        return


def _yield_tweet_candidates_bk1(obj: Any):
    try:
        if isinstance(obj, dict):
            tr = obj.get("tweet_results")
            if isinstance(tr, dict):
                res = tr.get("result") or {}
                cand = _extract_from_tweet_node(res)
                if cand: yield cand
            cand2 = _extract_from_tweet_node(obj)
            if cand2: yield cand2
            tm = obj.get("timelineModule")
            if isinstance(tm, dict):
                for it in tm.get("items", []):
                    yield from _yield_tweet_candidates(it)
            content = obj.get("content")
            if isinstance(content, dict):
                ic = content.get("itemContent")
                if isinstance(ic, dict):
                    yield from _yield_tweet_candidates(ic)
            item = obj.get("item")
            if isinstance(item, dict):
                yield from _yield_tweet_candidates(item)
            moduleItems = obj.get("moduleItems")
            if isinstance(moduleItems, list):
                for it in moduleItems:
                    yield from _yield_tweet_candidates(it)
            # 再帰
            for v in obj.values():
                yield from _yield_tweet_candidates(v)
        elif isinstance(obj, list):
            for v in obj:
                yield from _yield_tweet_candidates(v)
    except Exception:
        return

def _find_first_tweet_in_json(obj: Any) -> Optional[dict]:
    for rid, text, created in _yield_tweet_candidates(obj):
        return {"tweet_id": rid, "text": text, "created_at": created}
    return None

# ============== GraphQL (UserTweets) ==============
def fetch_latest_tweet_via_graphql(s: requests.Session, headers: dict, user_id: str, query_id: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    url = f"https://x.com/i/api/graphql/{query_id}/UserTweets"
    params = {
        "variables": json.dumps({
            "userId": user_id, "count": 1,
            "withQuickPromoteEligibilityTweet": True,
            "includePromotedContent": True,
            "withVoice": True,
            "withV2Timeline": True
        }, separators=(",", ":")),
        "features": json.dumps(_default_features(), separators=(",", ":")),
        "fieldToggles": json.dumps(_default_field_toggles(), separators=(",", ":")),
    }
    r = s.get(url, headers=headers, params=params, timeout=15)
    _log(f"[STEP] graphql(UserTweets) -> {r.status_code}")
    if r.status_code != 200:
        return False, None, r.text[:800]
    data = r.json()
    try:
        instructions = data["data"]["user"]["result"]["timeline_v2"]["timeline"]["instructions"]
        if isinstance(instructions, dict): instructions = [instructions]
        entries = []
        for ins in instructions:
            es = ins.get("entries")
            if isinstance(es, list): entries.extend(es)
        for e in entries:
            eid = str(e.get("entryId", ""))
            if eid.startswith(("tweet-", "profile-conversation-")):
                found = _find_first_tweet_in_json(e)
                if found: return True, found, None
        found = _find_first_tweet_in_json(data)
        if found: return True, found, None
        return False, None, "parse error (graphql): tweet not found"
    except Exception:
        found = _find_first_tweet_in_json(data)
        if found: return True, found, None
        return False, None, "parse error (graphql): tweet not found"

# ============== v2 timeline/profile（features付き） ==============
def _parse_profile_v2_with_global_objects(data: dict) -> Optional[dict]:
    gos = data.get("globalObjects", {}).get("tweets", {})
    if not gos: return None
    try:
        instructions = data["timeline"]["instructions"]
        if isinstance(instructions, dict): instructions = [instructions]
        entries = []
        for i in instructions:
            es = i.get("entries")
            if isinstance(es, list): entries.extend(es)
        for e in entries:
            eid = str(e.get("entryId", ""))
            if eid.startswith("tweet-"):
                tid = eid.split("-", 1)[1]
                tw = gos.get(tid)
                if isinstance(tw, dict):
                    text = tw.get("full_text") or tw.get("text")
                    created = tw.get("created_at")
                    if text:
                        return {"tweet_id": tid, "text": text, "created_at": created}
    except Exception:
        return None
    return None

def fetch_latest_tweet_via_profile_v2(s: requests.Session, headers: dict, user_id: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    url = f"https://x.com/i/api/2/timeline/profile/{user_id}.json"
    params = {
        "count": 20,
        "includePromotedContent": "true",
        "features": json.dumps(_default_features(), separators=(",", ":")),
        "fieldToggles": json.dumps(_default_field_toggles(), separators=(",", ":")),
    }
    r = s.get(url, headers=headers, params=params, timeout=15)
    _log(f"[STEP] v2 timeline(profile) -> {r.status_code}")
    if r.status_code != 200:
        return False, None, r.text[:800]
    data = r.json()

    got = _parse_profile_v2_with_global_objects(data)
    if got: return True, got, None

    try:
        instructions = data.get("timeline", {}).get("instructions")
        if isinstance(instructions, dict): instructions = [instructions]
        all_entries = []
        if isinstance(instructions, list):
            for ins in instructions:
                es = ins.get("entries")
                if isinstance(es, list): all_entries.extend(es)
        for e in all_entries:
            eid = str(e.get("entryId", ""))
            if eid.startswith(("tweet-", "profile-conversation-")):
                found = _find_first_tweet_in_json(e)
                if found: return True, found, None
        found_any = _find_first_tweet_in_json(data)
        if found_any: return True, found_any, None
        return False, None, "parse error (v2): tweet not found"
    except Exception as ex:
        found_any = _find_first_tweet_in_json(data)
        if found_any: return True, found_any, None
        return False, None, f"parse error (v2): {ex}"

# ============== v1.1 user_timeline フォールバック ==============
def fetch_latest_tweets_via_user_timeline_v11(
    s: requests.Session,
    headers: dict,
    user_id: str,
    limit: int = 5,
    include_rts: bool = True,
    mode: str = "all"  # "all"=混在, "tweets"=ツイートのみ, "replies"=リプライのみ
) -> Tuple[bool, Optional[List[dict]], Optional[str]]:
    """
    v1.1 statuses/user_timeline から“複数件”の最新ツイートを返す。
    mode:
        - "all"     : ツイートもリプライも返す
        - "tweets"  : リプライ以外のみ返す
        - "replies" : リプライのみ返す
    """
    url = "https://x.com/i/api/1.1/statuses/user_timeline.json"

    # modeに応じてexclude_replies設定
    if mode == "tweets":
        exclude_replies = True
    elif mode == "replies":
        exclude_replies = False
    else:
        exclude_replies = None

    req_count = max(1, min(200, max(limit * 2, 20)))
    params = {
        "user_id": user_id,
        "count": req_count,
        "include_rts": include_rts,
        "trim_user": True,
        "tweet_mode": "extended",
    }
    if exclude_replies is not None:
        params["exclude_replies"] = exclude_replies

    r = s.get(url, headers=headers, params=params, timeout=15)
    _log(f"[STEP] v1.1 user_timeline (multi, mode={mode}) -> {r.status_code}")
    if r.status_code != 200:
        return False, None, r.text[:800]

    try:
        arr = r.json()
        if not isinstance(arr, list) or not arr:
            return False, None, "parse error (v1.1): empty or non-list"

        results: List[dict] = []
        for tw in arr:
            tid = tw.get("id_str") or (tw.get("id") and str(tw.get("id")))
            if not tid:
                continue
            text = tw.get("full_text") or tw.get("text")
            if not text:
                continue

            created = tw.get("created_at")
            reply_to_id = tw.get("in_reply_to_status_id_str")
            is_reply = bool(reply_to_id)

            # modeがrepliesならリプライのみ残す
            if mode == "replies" and not is_reply:
                continue
            # modeがtweetsなら通常ツイートのみ残す
            if mode == "tweets" and is_reply:
                continue

            results.append({
                "tweet_id": tid,
                "text": text,
                "created_at": created,
                "type": "reply" if is_reply else "tweet",
                "reply_to_tweet_id": reply_to_id if is_reply else None
            })

            if len(results) >= limit:
                break

        if results:
            return True, results, None
        return False, None, f"parse error (v1.1): no {mode} found"
    except Exception as ex:
        return False, None, f"parse error (v1.1): {ex}"

# ============== screen_name 取得（v1.1 users/show） ==============
def fetch_screen_name_by_user_id(s: requests.Session, headers: dict, user_id: str) -> Optional[str]:
    url = "https://x.com/i/api/1.1/users/show.json"
    r = s.get(url, headers=headers, params={"user_id": user_id}, timeout=12)
    _log(f"[STEP] users/show -> {r.status_code}")
    if not r.ok: return None
    try:
        data = r.json()
        return data.get("screen_name")
    except Exception:
        return None

# ============== v2 search/adaptive フォールバック ==============
def fetch_latest_tweet_via_search_adaptive(s: requests.Session, headers: dict, screen_name: str) -> Tuple[bool, Optional[dict], Optional[str]]:
    url = "https://x.com/i/api/2/search/adaptive.json"
    params = {
        "q": f"from:{screen_name} -is:retweet",
        "tweet_search_mode": "live",
        "count": 20,
        "query_source": "typed_query",
        "tweet_mode": "extended",
    }
    r = s.get(url, headers=headers, params=params, timeout=15)
    _log(f"[STEP] v2 search/adaptive -> {r.status_code}")
    if r.status_code != 200:
        return False, None, r.text[:800]
    try:
        data = r.json()
        gos = data.get("globalObjects", {}).get("tweets", {})
        if isinstance(gos, dict) and gos:
            latest = None
            for tid, tw in gos.items():
                if latest is None or int(tid) > int(latest[0]):
                    latest = (tid, tw)
            if latest:
                tid, tw = latest
                text = tw.get("full_text") or tw.get("text")
                created = tw.get("created_at")
                if text:
                    return True, {"tweet_id": tid, "text": text, "created_at": created}, None
        found = _find_first_tweet_in_json(data)
        if found: return True, found, None
        return False, None, "parse error (search): not found"
    except Exception as ex:
        return False, None, f"parse error (search): {ex}"

def get_tweets(profile, user_id, screen_name):
    """
    成功時: dict を返します:
      {
        "tweet_id": str,
        "text": str,
        "created_at_raw": str|None,     # X既定の文字列
        "created_at_utc": str|None,     # 'YYYY-mm-dd HH:MM:SS'
        "created_at_jst": str|None      # 'YYYY-mm-dd HH:MM:SS'
      }
    失敗時: None
    """
    try:
        _log("[START] test2_verbose_complete")
        _log(f"[STEP] profile = {profile}")
        a, c, e = get_x_cookies_from_firefox(profile)
        _log(f"[STEP] cookie fetch -> err={e}")
        _log(f"auth_token={a}")
        _log(f"ct0={c[:24]}...")
        if e:
            _log("Cookie取得エラー、終了"); return None

        s = _new_session()
        _set_cookies(s, a, c)

        bearer   = fetch_web_bearer_token_with_session(s)
        query_id = fetch_usertweets_query_id_with_session(s)
        _log(f"[STEP] bearer(head)={bearer[:20]}..., query_id={query_id}")

        headers = {
            "authorization": f"Bearer {bearer}",
            "x-csrf-token": c,
            "x-twitter-auth-type": "OAuth2Session",
            "x-twitter-active-user": "yes",
            "x-twitter-client-language": "ja",
            "accept-language": "ja,en-US;q=0.9",
            "referer": "https://x.com/",
            "origin": "https://x.com",
            "accept": "*/*",
        }
        auth = s.get("https://x.com/i/api/1.1/account/settings.json", headers=headers, timeout=12)
        _log(f"[STEP] auth check -> {auth.status_code}")
        if not auth.ok:
            _log(auth.text[:400]); _log("X 認証が無効です"); return None

        # お好みで有効化。現状は v1.1 を優先（安定しやすい）

#        ok, replies, err = fetch_replies_to_me(s, headers, screen_name, limit=5)
#        if ok:
#            for r in replies:
#                print(f"Reply from tweet {r['reply_to_tweet_id']}: {r['text']}")

# リプライ取得機能一旦保留
#        ok, replies, err = fetch_replies_to_me_graphql(s, headers, "@OnSounds", limit=5)
#        if ok:
#            for r in replies:
#                print(r["tweet_id"], r["text"], r["created_at"])
#        else:
#            print("Error:", err)

        # 3) v1.1 user_timeline（既定で True）
        if True:

            ok3, payload3, err3 = fetch_latest_tweets_via_user_timeline_v11(
                s, headers, user_id,
                limit=5,              # 返す件数
                mode = "tweets"       # replies にすると自分が他のアカウントに行ったリプライを取得できる
            )

            if ok3 and isinstance(payload3, list):
                results = []
                for tw in payload3:
                    utc_str, jst_str = _normalize_created_at(tw.get("created_at"))
                    _log(f"[DONE v1.1 timeline] tweet_id={tw['tweet_id']}")
                    _log(f"text={tw['text']}")
                    _log(f"created_at(raw)={tw.get('created_at')} / UTC={utc_str} / JST={jst_str}")
                    results.append({
                        "tweet_id": tw["tweet_id"],
                        "text": tw["text"],
                        "created_at_raw": tw.get("created_at"),
                        "created_at_utc": utc_str,
                        "created_at_jst": jst_str,
                        "user_id": '',
                        "check_time": '',
                        "type": tw["type"] ,
                        "reply_to_tweet_id": tw["reply_to_tweet_id"]
                    })
                return results
            _log(f"[WARN] v1.1 timeline 失敗 -> {err3}")

    except Exception:
        traceback.print_exc()
        return None

def get_replies(profile, user_id, screen_name, kind="tweets", limit=5):
    """
    kind:
      - "tweets"           : 通常ツイートのみ
      - "replies_outgoing" : 自分が送ったリプ（in_reply_to_* があるツイ）
      - "replies_incoming" : 自分宛のリプ（to:screen_name）
    戻り値: 成功時 list[dict] / 失敗時 None
    """
    s, headers = _session_and_headers_from_firefox_profile(profile)
    if not s: return None

    if kind == "tweets":
        ok, payload, err = fetch_latest_tweets_via_user_timeline_v11(
            s, headers, user_id, limit=limit, mode="tweets"
        )
        if not ok or not isinstance(payload, list): 
            _log(f"[WARN] tweets失敗: {err}"); 
            return None
        return _normalize_result_rows(payload)

    elif kind == "replies_outgoing":
        ok, payload, err = fetch_latest_tweets_via_user_timeline_v11(
            s, headers, user_id, limit=limit, mode="replies"
        )
        if not ok or not isinstance(payload, list):
            _log(f"[WARN] outgoing replies 失敗: {err}")
            return None
        # v1.1 側で type="reply" / reply_to_tweet_id セット済み
        return _normalize_result_rows(payload)

    elif kind == "replies_incoming_test":
        ok, rows, err = fetch_replies_to_my_tweets(s, headers, user_id="2446855615",
                                           total_limit=20, lookback_tweets=40)
        if ok:
            for r in rows:
                print(r["created_at_jst"], r["text"], "parent=", r["parent_tweet_id"])
        else:
            print("ERR:", err)

    elif kind == "replies_incoming":
        print("replies_incoming")
        # GraphQL SearchTimeline（to:screen_name）を優先
        ok, rows, err = fetch_replies_to_me_graphql(s, headers, screen_name, limit=limit)
#        print("ok=",ok)
        print("rows=",rows)
#        print("err=",err)
        if not ok or not isinstance(rows, list):
            _log(f"[WARN] incoming replies graphql失敗: {err}")
            # フォールバック: v2 search/adaptive
            sn = screen_name.lstrip("@")
            ok2, row2, err2 = fetch_latest_tweet_via_search_adaptive(s, headers, sn)
            if not ok2 or not row2:
                _log(f"[WARN] incoming replies fallback失敗: {err2}")
                return None
            rows = [row2]

        # incoming は type を "reply_to_me" に寄せ、相手の reply_to は不要のことが多い
        normalized = []
        for r in rows:
            print("r.get(created_at)")
            print(r.get("created_at"))
            utc_str, jst_str = _normalize_created_at(r.get("created_at"))
            normalized.append({
                "tweet_id": r["tweet_id"],
                "text": r["text"],
                "created_at": r.get("created_at"),
                "created_at_raw": r.get("created_at"),
                "created_at_utc": utc_str,
                "created_at_jst": jst_str,
                "user_id": '',
                "check_time": '',
                "type": "reply_to_me",
                "reply_to_tweet_id": r.get("reply_to_tweet_id")  # 取れるときは保持
            })
        print(_normalize_result_rows(normalized))
        return _normalize_result_rows(normalized)

    else:
        _log(f"[ERR] unknown kind={kind}")
        return None


import time

def fetch_replies_to_me(s, headers, screen_name, limit=5, retries=3, wait=5):
    if screen_name.startswith("@"):
        screen_name = screen_name[1:]

    url = "https://x.com/i/api/2/search/adaptive.json"
    params = {
        "q": f"to:{screen_name}",
        "tweet_search_mode": "relevancy",
        "count": max(10, limit * 2),
        "query_source": "typed_query",
        "tweet_mode": "extended",
    }

    for attempt in range(retries):
        r = s.get(url, headers=headers, params=params, timeout=15)
        _log(f"[STEP] search/adaptive (to:{screen_name}) -> {r.status_code}")
        if r.status_code == 200:
            break
        if attempt < retries - 1:
            time.sleep(wait)
    else:
        return False, None, f"HTTP {r.status_code}"

    try:
        data = r.json()
        gos = data.get("globalObjects", {}).get("tweets", {})
        results = []
        for tid, tw in gos.items():
            text = tw.get("full_text") or tw.get("text")
            created = tw.get("created_at")
            reply_to_id = tw.get("in_reply_to_status_id_str")
            results.append({
                "tweet_id": tid,
                "text": text,
                "created_at": created,
                "reply_to_tweet_id": reply_to_id
            })
            if len(results) >= limit:
                break

        if results:
            return True, results, None
        return False, None, "no replies found"
    except Exception as ex:
        return False, None, f"parse error: {ex}"

import re

from typing import Optional, Set, List, Tuple
import re

def fetch_searchtimeline_query_id_with_session(
    s: requests.Session,
    prefer: str = "adaptive",   # "adaptive" | "search" | "auto"
) -> Optional[Tuple[str, str]]:
    """
    (operationName, queryId) を返す。優先度は prefer で指定可能。
    優先度: HTML直書き > JS直書きURL > JS同一オブジェクト > 近傍(±6000) >> 広域(距離<=1200のみ)
    """
    _log("fetch_searchtimeline_query_id_with_session")

    MAX_GAP_WIDE = 50000
    OBJ_GAP = 2000
    VICINITY = 6000
    WIDE_ACCEPT_GAP = 1200

    OP_ANY  = r'(?:operationName|opName)\s*[:=]\s*(?:["\']?)([A-Za-z0-9_.$-]+)'
    QID_ANY = r'(?:queryId|queryID|qid|id|docId|documentId)\s*[:=]\s*(?:["\']?)([A-Za-z0-9_-]{6,80})'

    pat_op_then_qid_any = re.compile(OP_ANY + r'.{0,' + str(MAX_GAP_WIDE) + r'}?' + QID_ANY,
                                     re.IGNORECASE | re.DOTALL)
    pat_qid_then_op_any = re.compile(QID_ANY + r'.{0,' + str(MAX_GAP_WIDE) + r'}?' + OP_ANY,
                                     re.IGNORECASE | re.DOTALL)
    pat_named_map_any = re.compile(r'["\']?([A-Za-z0-9_.$-]+)["\']?\s*:\s*\{\s*' + QID_ANY,
                                   re.IGNORECASE | re.DOTALL)

    pat_url_plain = re.compile(r'/i/api/graphql/([A-Za-z0-9_-]{6,80})/([^"\s/]+)', re.IGNORECASE)
    pat_url_u002f = re.compile(r'\\u002Fi\\u002Fapi\\u002Fgraphql\\u002F([A-Za-z0-9_-]{6,80})\\u002F([^"\\s/]+)', re.IGNORECASE)
    pat_url_x2f   = re.compile(r'\\x2Fi\\x2Fapi\\x2Fgraphql\\x2F([A-Za-z0-9_-]{6,80})\\x2F([^"\\s/]+)', re.IGNORECASE)

    pat_obj_op_qid = re.compile(
        r'\{[^{}]{0,' + str(OBJ_GAP) + r'}"operationName"\s*:\s*"([^"]+)"[^{}]{0,' + str(OBJ_GAP) +
        r'}"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"[^{}]{0,' + str(OBJ_GAP) + r'}\}',
        re.IGNORECASE | re.DOTALL
    )
    pat_obj_qid_op = re.compile(
        r'\{[^{}]{0,' + str(OBJ_GAP) + r'}"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"[^{}]{0,' + str(OBJ_GAP) +
        r'}"operationName"\s*:\s*"([^"]+)"[^{}]{0,' + str(OBJ_GAP) + r'}\}',
        re.IGNORECASE | re.DOTALL
    )

    pat_op_names = re.compile(
        r'(?:operationName|opName)\s*[:=]\s*["\']?(SearchTimeline|AdaptiveSearchTimeline|SearchTimelineQuery|AdaptiveSearchTimelineQuery)\b',
        re.IGNORECASE
    )
    pat_qid_near = re.compile(QID_ANY, re.IGNORECASE)

    pairs: List[Tuple[str, str, str, int]] = []
    seen: Set[Tuple[str, str]] = set()

    def _add(op: str, qid: str, source: str, gap: int = 0):
        k = (op, qid)
        if k in seen:
            return
        seen.add(k)
        pairs.append((op, qid, source, gap))

    # 1) HTML直書き
    for url in [
        "https://x.com/home",
        "https://x.com/explore",
        "https://x.com/search?q=a&src=typed_query",
        "https://x.com/i/connect_people",
    ]:
        try:
            r = s.get(url, headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://x.com/",
                "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
            }, timeout=15)
            _log(f"[STEP] GET {url} -> {r.status_code}")
            if not r.ok: continue
            text = r.text
            for pat in (pat_url_plain, pat_url_u002f, pat_url_x2f):
                for m in pat.finditer(text):
                    qid, op = m.group(1), m.group(2)
                    _add(op, qid, 'html_url', 0)
        except Exception as e:
            _log(f"[WARN] HTML scan {url}: {e}")

    # 2) JS 取得
    js_urls: Set[str] = set()
    try:
        js_urls = set(_fetch_main_js_urls_with_session(s))
    except Exception as e:
        _log(f"[WARN] _fetch_main_js_urls_with_session failed: {e}")
    _log(f"[DEBUG] _fetch_main_js_urls_with_session -> {len(js_urls)} urls")
    for u in list(js_urls)[:10]:
        _log(f"[DEBUG] JS seed: {u}")

    # 3) JS 走査
    for js_url in js_urls:
        try:
            r = s.get(js_url, headers={"Accept":"*/*","Referer":"https://x.com/"}, timeout=15)
        except Exception as e:
            _log(f"[WARN] GET {js_url}: {e}")
            continue
        if not r.ok: continue
        text = r.text

        # (A) URL直書き
        for pat in (pat_url_plain, pat_url_u002f, pat_url_x2f):
            for m in pat.finditer(text):
                qid, op = m.group(1), m.group(2)
                _add(op, qid, 'js_url', 0)

        # (B) 同一オブジェクト
        for m in pat_obj_op_qid.finditer(text):
            op, qid = m.group(1), m.group(2)
            _add(op, qid, 'js_object', 0)
        for m in pat_obj_qid_op.finditer(text):
            qid, op = m.group(1), m.group(2)
            _add(op, qid, 'js_object', 0)

        # (C) 近傍（SearchTimeline系のみ、±6000）
        for nm in pat_op_names.finditer(text):
            op = nm.group(1)
            start = max(0, nm.start() - VICINITY)
            end   = min(len(text), nm.end() + VICINITY)
            window = text[start:end]
            mq = pat_qid_near.search(window)
            if mq:
                qid = mq.group(1)
                gap = abs((start + mq.start()) - nm.start())
                _add(op, qid, 'js_vicinity', gap)

        # (D) 広域（距離が小さいものだけ）
        for m in pat_op_then_qid_any.finditer(text):
            op, qid = m.group(1), m.group(2)
            gap = len(m.group(0))
            if gap <= WIDE_ACCEPT_GAP:
                _add(op, qid, 'js_wide', gap)
        for m in pat_qid_then_op_any.finditer(text):
            qid, op = m.group(1), m.group(2)
            gap = len(m.group(0))
            if gap <= WIDE_ACCEPT_GAP:
                _add(op, qid, 'js_wide', gap)
        for m in pat_named_map_any.finditer(text):
            op, qid = m.group(1), m.group(2)
            _add(op, qid, 'js_wide', 200)

    _log(f"[DEBUG] collected op/qid candidates: {len(pairs)}")

    # 選抜
    def _pref_source(src: str) -> int:
        return {'html_url':0, 'js_url':1, 'js_object':2, 'js_vicinity':3, 'js_wide':9}.get(src, 9)

    def _pref_op(op: str) -> int:
        op_l = op.lower()
        blacklist = (
            "bookmark","community","list","home","foryou","following","who",
            "notification","inbox","dm","audio","live","explore","trend",
            "video","ads","ad","unified","module"
        )
        if any(b in op_l for b in blacklist):
            return 100
        flat = op.replace(".", "").replace("_","").lower()
        # ← ここが重要: Adaptive を最優先
        if prefer == "adaptive":
            order = ["adaptivesearchtimeline", "searchtimeline",
                     "adaptivesearchtimelinequery", "searchtimelinequery"]
        elif prefer == "search":
            order = ["searchtimeline", "adaptivesearchtimeline",
                     "searchtimelinequery", "adaptivesearchtimelinequery"]
        else:  # auto
            order = ["adaptivesearchtimeline", "searchtimeline",
                     "searchtimelinequery", "adaptivesearchtimelinequery"]
        if flat in order:
            return order.index(flat)
        if "search" in op_l and "timeline" in op_l:
            return 10
        return 50

    if not pairs:
        _log("None")
        return None

    pairs.sort(key=lambda t: (_pref_source(t[2]), _pref_op(t[0]), t[3]))
    best_op, best_qid, best_src, best_gap = pairs[0]
    if _pref_op(best_op) >= 100:
        _log("None")
        return None
    _log(f"[STEP] PICK src={best_src} operationName={best_op}, queryId={best_qid}")
    return (best_op, best_qid)

# 追加: 複数候補を返す収集関数
from typing import Optional, Set, List, Tuple
import re

def collect_searchtimeline_pairs_with_session(s: requests.Session) -> List[Tuple[str, str, str, int]]:
    """
    (operationName, queryId, source, gap) の候補を優先度順に返す。
    source: html_url > js_url > js_object > js_vicinity > js_wide
    gap   : 近さ（小さいほど信頼）
    """
    _log("collect_searchtimeline_pairs_with_session")

    MAX_GAP_WIDE = 50000
    OBJ_GAP = 2000
    VICINITY = 6000
    WIDE_ACCEPT_GAP = 1200

    OP_ANY  = r'(?:operationName|opName)\s*[:=]\s*(?:["\']?)([A-Za-z0-9_.$-]+)'
    QID_ANY = r'(?:queryId|queryID|qid|id|docId|documentId)\s*[:=]\s*(?:["\']?)([A-Za-z0-9_-]{6,80})'

    pat_op_then_qid_any = re.compile(OP_ANY + r'.{0,' + str(MAX_GAP_WIDE) + r'}?' + QID_ANY,
                                     re.IGNORECASE | re.DOTALL)
    pat_qid_then_op_any = re.compile(QID_ANY + r'.{0,' + str(MAX_GAP_WIDE) + r'}?' + OP_ANY,
                                     re.IGNORECASE | re.DOTALL)
    pat_named_map_any = re.compile(r'["\']?([A-Za-z0-9_.$-]+)["\']?\s*:\s*\{\s*' + QID_ANY,
                                   re.IGNORECASE | re.DOTALL)

    pat_url_plain = re.compile(r'/i/api/graphql/([A-Za-z0-9_-]{6,80})/([^"\s/]+)', re.IGNORECASE)
    pat_url_u002f = re.compile(r'\\u002Fi\\u002Fapi\\u002Fgraphql\\u002F([A-Za-z0-9_-]{6,80})\\u002F([^"\\s/]+)', re.IGNORECASE)
    pat_url_x2f   = re.compile(r'\\x2Fi\\x2Fapi\\x2Fgraphql\\x2F([A-Za-z0-9_-]{6,80})\\x2F([^"\\s/]+)', re.IGNORECASE)

    pat_obj_op_qid = re.compile(
        r'\{[^{}]{0,' + str(OBJ_GAP) + r'}"operationName"\s*:\s*"([^"]+)"[^{}]{0,' + str(OBJ_GAP) +
        r'}"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"[^{}]{0,' + str(OBJ_GAP) + r'}\}',
        re.IGNORECASE | re.DOTALL
    )
    pat_obj_qid_op = re.compile(
        r'\{[^{}]{0,' + str(OBJ_GAP) + r'}"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"[^{}]{0,' + str(OBJ_GAP) +
        r'}"operationName"\s*:\s*"([^"]+)"[^{}]{0,' + str(OBJ_GAP) + r'}\}',
        re.IGNORECASE | re.DOTALL
    )

    pat_op_names = re.compile(
        r'(?:operationName|opName)\s*[:=]\s*["\']?(SearchTimeline|AdaptiveSearchTimeline|SearchTimelineQuery|AdaptiveSearchTimelineQuery)\b',
        re.IGNORECASE
    )
    pat_qid_near = re.compile(QID_ANY, re.IGNORECASE)

    pairs: List[Tuple[str, str, str, int]] = []  # (op, qid, src, gap)
    seen: Set[Tuple[str, str]] = set()

    def _add(op: str, qid: str, src: str, gap: int = 0):
        # 除外：よく紛れる別物
        op_l = op.lower()
        blacklist = ("bookmark","community","list","home","foryou","following","who",
                     "notification","inbox","dm","audio","live","explore","trend",
                     "video","ads","ad","unified","module")
        if any(b in op_l for b in blacklist):
            return
        key = (op, qid)
        if key in seen:
            return
        seen.add(key)
        pairs.append((op, qid, src, gap))

    # 1) HTML 直書き（最優先）
    for url in [
        "https://x.com/home",
        "https://x.com/explore",
        "https://x.com/search?q=a&src=typed_query",
        "https://x.com/i/connect_people",
    ]:
        try:
            r = s.get(url, headers={
                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                "Referer": "https://x.com/",
                "Accept-Language": "ja,en-US;q=0.9,en;q=0.8",
            }, timeout=15)
            _log(f"[STEP] GET {url} -> {r.status_code}")
            if not r.ok: continue
            text = r.text
            for pat in (pat_url_plain, pat_url_u002f, pat_url_x2f):
                for m in pat.finditer(text):
                    qid, op = m.group(1), m.group(2)
                    _add(op, qid, "html_url", 0)
        except Exception as e:
            _log(f"[WARN] HTML scan {url}: {e}")

    # 2) JS 一覧
    js_urls: Set[str] = set()
    try:
        js_urls = set(_fetch_main_js_urls_with_session(s))
    except Exception as e:
        _log(f"[WARN] _fetch_main_js_urls_with_session failed: {e}")
    _log(f"[DEBUG] _fetch_main_js_urls_with_session -> {len(js_urls)} urls")
    for u in list(js_urls)[:10]:
        _log(f"[DEBUG] JS seed: {u}")

    # 3) JS 走査（直書き > 同一オブジェクト > 近傍 > 広域(距離しきい値)）
    for js_url in js_urls:
        try:
            r = s.get(js_url, headers={"Accept":"*/*","Referer":"https://x.com/"}, timeout=15)
        except Exception as e:
            _log(f"[WARN] GET {js_url}: {e}")
            continue
        if not r.ok: continue
        text = r.text

        for pat in (pat_url_plain, pat_url_u002f, pat_url_x2f):
            for m in pat.finditer(text):
                qid, op = m.group(1), m.group(2)
                _add(op, qid, "js_url", 0)

        for m in pat_obj_op_qid.finditer(text):
            op, qid = m.group(1), m.group(2)
            _add(op, qid, "js_object", 0)
        for m in pat_obj_qid_op.finditer(text):
            qid, op = m.group(1), m.group(2)
            _add(op, qid, "js_object", 0)

        for nm in pat_op_names.finditer(text):
            op = nm.group(1)
            start = max(0, nm.start() - VICINITY)
            end   = min(len(text), nm.end() + VICINITY)
            window = text[start:end]
            mq = pat_qid_near.search(window)
            if mq:
                qid = mq.group(1)
                gap = abs((start + mq.start()) - nm.start())
                _add(op, qid, "js_vicinity", gap)

        for m in pat_op_then_qid_any.finditer(text):
            op, qid = m.group(1), m.group(2)
            gap = len(m.group(0))
            if gap <= WIDE_ACCEPT_GAP:
                _add(op, qid, "js_wide", gap)
        for m in pat_qid_then_op_any.finditer(text):
            qid, op = m.group(1), m.group(2)
            gap = len(m.group(0))
            if gap <= WIDE_ACCEPT_GAP:
                _add(op, qid, "js_wide", gap)
        for m in pat_named_map_any.finditer(text):
            op, qid = m.group(1), m.group(2)
            _add(op, qid, "js_wide", 200)

    _log(f"[DEBUG] collected op/qid candidates: {len(pairs)}")

    # 並び替え：source優先 → op優先 → gap 昇順
    def _pref_source(src: str) -> int:
        return {"html_url":0, "js_url":1, "js_object":2, "js_vicinity":3, "js_wide":9}.get(src, 9)

    def _pref_op(op: str) -> int:
        flat = op.replace(".", "").replace("_","").lower()
        order = [
            "adaptivesearchtimeline", "searchtimeline",
            "adaptivesearchtimelinequery", "searchtimelinequery",
        ]
        return order.index(flat) if flat in order else (10 if ("search" in flat and "timeline" in flat) else 50)

    pairs.sort(key=lambda t: (_pref_source(t[2]), _pref_op(t[0]), t[3]))
    return pairs
import json, re

# 置き換え推奨
_FEATURES_NULL_RE = re.compile(r"The following features cannot be null:\s*(.+)$", re.DOTALL)

def _augment_features_from_error(features_dict: dict, error_text: str) -> dict:
    """
    400 のエラー文から不足 feature を抽出し True で補完。
    - スネークケースのみ抽出 (例: responsive_web_..., longform_notetweets_...)
    - ゴミ(extensions/name/tracing/...)は自然に弾かれる
    """
    m = _FEATURES_NULL_RE.search(error_text)
    if not m:
        return features_dict

    # 例外文全体から snake_case キーだけ拾う
    # 先頭とどこかに '_' を含む小文字英数+_ のみ
    keys = set(re.findall(r"\b[a-z][a-z0-9_]*_[a-z0-9_]+\b", m.group(1)))
    if not keys:
        return features_dict

    newf = dict(features_dict)
    added = []
    for k in sorted(keys):
        if k not in newf or newf[k] is None:
            newf[k] = True
            added.append(k)
    if added:
        _log(f"[STEP] features auto-add (clean): {added}")
    return newf

import re
from typing import List, Optional, Tuple, Set

def _get_op_qid_for_names(s, op_names: List[str]) -> Optional[Tuple[str, str]]:
    names = "|".join(map(re.escape, op_names))

    pat_plain = re.compile(rf"/i/api/graphql/([A-Za-z0-9_-]{{6,80}})/({names})\b", re.IGNORECASE)
    pat_u002f = re.compile(rf"\\u002Fi\\u002Fapi\\u002Fgraphql\\u002F([A-Za-z0-9_-]{{6,80}})\\u002F({names})\b", re.IGNORECASE)
    pat_x2f   = re.compile(rf"\\x2Fi\\x2Fapi\\x2Fgraphql\\x2F([A-Za-z0-9_-]{{6,80}})\\x2F({names})\b", re.IGNORECASE)

    def scan_text(txt: str) -> Optional[Tuple[str,str]]:
        for pat in (pat_plain, pat_u002f, pat_x2f):
            m = pat.search(txt)
            if m:
                return (m.group(2), m.group(1))
        return None

    # HTML から
    for url in [
        "https://x.com/home",
        "https://x.com/explore",
        "https://x.com/search?q=a&src=typed_query",
        "https://x.com/i/connect_people",
    ]:
        r = s.get(url, headers={"Accept":"text/html,*/*;q=0.8","Referer":"https://x.com/"}, timeout=15)
        if r.ok:
            got = scan_text(r.text)
            if got: return got

    # JS から
    js_urls: Set[str] = set(_fetch_main_js_urls_with_session(s))
    for u in js_urls:
        r = s.get(u, headers={"Accept":"*/*","Referer":"https://x.com/"}, timeout=15)
        if r.ok:
            got = scan_text(r.text)
            if got: return got

    return None

def fetch_user_tweet_ids(s, headers, user_id: str, count: int = 40) -> Tuple[bool, Optional[List[str]], Optional[str]]:
    """
    ユーザーの直近ポストIDを新しい順で返す（最大 count）
    """
    op_qid = _get_op_qid_for_names(s, ["UserTweets","UserTweetsAndReplies"])
    if not op_qid:
        return False, None, "queryId not found for UserTweets"
    op, qid = op_qid

    variables = {
        "userId": str(user_id),
        "count": count,
        "includePromotedContent": True,
        "withQuickPromoteEligibilityTweetFields": True,
        "withV2Timeline": True,
    }
    params = {
        "variables": json.dumps(variables, separators=(",", ":")),
        "features": json.dumps(_default_features(), separators=(",", ":")),
        "fieldToggles": json.dumps(_default_field_toggles(), separators=(",", ":")),
    }
    url = f"https://x.com/i/api/graphql/{qid}/{op}"
    r = s.get(url, headers=headers, params=params, timeout=20)
    if r.status_code == 400:
        # features 自動補完
        feat = _augment_features_from_error(_default_features(), r.text[:2000])
        params["features"] = json.dumps(feat, separators=(",", ":"))
        r = s.get(url, headers=headers, params=params, timeout=20)
    if r.status_code != 200:
        return False, None, r.text[:800]

    ids: List[str] = []
    data = r.json()
    # instructions → entries → content.itemContent.tweet_results.result.rest_id
    try:
        instr = (data.get("data", {})
                   .get("user", {})
                   .get("result", {})
                   .get("timeline_v2", {})
                   .get("timeline", {})
                   .get("instructions", []))
        for inst in instr:
            for e in inst.get("entries", []):
                content = (e.get("content") or {})
                ic = (content.get("itemContent") or {})
                tr = (ic.get("tweet_results") or ic.get("tweetResults") or {})
                res = tr.get("result") or {}
                rid = res.get("rest_id") or (res.get("legacy") or {}).get("id_str")
                if rid and rid not in ids:
                    ids.append(str(rid))
    except Exception:
        pass

    return (True, ids, None) if ids else (False, None, "no tweets found")

def _iter_result_nodes_from_timeline(data: dict):
    """SearchTimeline/TweetDetail っぽい JSON から result ノードを列挙"""
    def _add_from_content(content):
        ic = (content.get("itemContent") or {})
        tr = (ic.get("tweet_results") or ic.get("tweetResults") or {})
        res = tr.get("result")
        if isinstance(res, dict):
            yield res
        # module/items 型
        for it in content.get("items", []):
            ic2 = (it.get("item") or {}).get("itemContent") or {}
            tr2 = (ic2.get("tweet_results") or ic2.get("tweetResults") or {})
            res2 = tr2.get("result")
            if isinstance(res2, dict):
                yield res2

    instr = (data.get("data", {})
               .get("search_by_raw_query", {})
               .get("search_timeline", {})
               .get("timeline", {})
               .get("instructions", []))
    for inst in instr:
        for e in inst.get("entries", []):
            content = e.get("content") or {}
            yield from _add_from_content(content)
        if inst.get("type") == "TimelinePinEntry":
            e = inst.get("entry", {}) or {}
            content = e.get("content", {}) or {}
            yield from _add_from_content(content)

def _extract_direct_replies(json_obj: dict, parent_tweet_id: str):
    """
    会話(=conversation_id:<parent>)の中から、
    legacy.in_reply_to_status_id_str が parent と一致するものだけを返す
    """
    parent = str(parent_tweet_id)
    for res in _iter_result_nodes_from_timeline(json_obj):
        legacy = res.get("legacy") or {}
        tid = res.get("rest_id") or legacy.get("id_str")
        if not tid: 
            continue
        if str(legacy.get("in_reply_to_status_id_str") or "") != parent:
            continue  # 直下じゃない（孫返信など）は除外
        text = legacy.get("full_text") or legacy.get("text") or ""
        created = legacy.get("created_at")
        yield (str(tid), text, created)

def fetch_direct_replies_for_tweet(s, headers, tweet_id: str, per_tweet_limit: int = 50):
    """
    tweet_id の直下の返信を新しい順で返す
    """
    # 既存の SearchTimeline を使う（op/qid は再利用）
    op_qid = collect_searchtimeline_pairs_with_session(s)
    if not op_qid:
        return False, None, "no (op,qid) candidates"
    # 最上位候補だけ使う（あなたの多段試行があるならそれでもOK）
    op, qid, src, gap = op_qid[0]

    url = f"https://x.com/i/api/graphql/{qid}/{op}"
    variables = {
        "rawQuery": f"conversation_id:{tweet_id}",
        "count": max(per_tweet_limit, 50),
        "querySource": "typed_query",
        "product": "Latest",
    }
    params = {
        "variables": json.dumps(variables, separators=(",", ":")),
        "features": json.dumps(_default_features(), separators=(",", ":")),
        "fieldToggles": json.dumps(_default_field_toggles(), separators=(",", ":")),
    }

    r = s.get(url, headers=headers, params=params, timeout=20)
    if r.status_code == 400:
        feat = _augment_features_from_error(_default_features(), r.text[:2000])
        params["features"] = json.dumps(feat, separators=(",", ":"))
        r = s.get(url, headers=headers, params=params, timeout=20)
    if r.status_code != 200:
        return False, None, r.text[:800]

    data = r.json()
    created_map = _build_created_map_from_search_timeline(data)

    # 直下だけに絞る
    by_id = {}
    for rid, text, created in _extract_direct_replies(data, tweet_id):
        created = created or created_map.get(rid)
        utc, jst = _normalize_created_at(created)
        by_id[rid] = {
            "tweet_id": rid,
            "text": text,
            "created_at": created,
            "created_at_utc": utc,
            "created_at_jst": jst,
            "parent_tweet_id": str(tweet_id),
        }

    # ページネーション（必要なら）
    cursor = _find_bottom_cursor(data)
    pages = 1
    while cursor and len(by_id) < per_tweet_limit and pages < 5:
        variables["cursor"] = cursor
        params["variables"] = json.dumps(variables, separators=(",", ":"))
        r2 = s.get(url, headers=headers, params=params, timeout=20)
        if r2.status_code != 200:
            break
        data2 = r2.json()
        created_map2 = _build_created_map_from_search_timeline(data2)
        for rid, text, created in _extract_direct_replies(data2, tweet_id):
            created = created or created_map2.get(rid)
            utc, jst = _normalize_created_at(created)
            by_id.setdefault(rid, {
                "tweet_id": rid, "text": text, "created_at": created,
                "created_at_utc": utc, "created_at_jst": jst,
                "parent_tweet_id": str(tweet_id),
            })
        cursor = _find_bottom_cursor(data2)
        pages += 1

    results = sorted(by_id.values(), key=lambda x: (x["created_at_utc"] or ""), reverse=True)
    return True, results[:per_tweet_limit], None

def fetch_replies_to_my_tweets(s, headers, user_id: str, total_limit: int = 20, lookback_tweets: int = 30):
    """
    自分の直近 lookback_tweets 件のポストを対象に、
    直下返信を集約して新しい順 total_limit 件を返す
    """
    ok, ids, err = fetch_user_tweet_ids(s, headers, user_id, count=lookback_tweets)
    if not ok:
        return False, None, f"user tweets err: {err}"

    all_by_id = {}
    for tid in ids:
        ok2, rows, err2 = fetch_direct_replies_for_tweet(s, headers, tid, per_tweet_limit=total_limit)
        if not ok2:
            continue  # このツイートはスキップ（権限や0件など）
        for r in rows:
            all_by_id.setdefault(r["tweet_id"], r)
        if len(all_by_id) >= total_limit:
            break

    results = sorted(all_by_id.values(), key=lambda x: (x["created_at_utc"] or ""), reverse=True)
    return (True, results[:total_limit], None) if results else (False, None, "no direct replies found")


def fetch_replies_to_me_graphql(s, headers, screen_name, limit=5):
    if screen_name.startswith("@"):
        screen_name = screen_name[1:]

    pairs = collect_searchtimeline_pairs_with_session(s)
    if not pairs:
        return False, None, "no (op,qid) candidates"

    # 取りこぼしを減らすため 1ページの件数を多めに
    page_count = max(limit * 3, 50)

    tried = 0
    OP_ORDER_BASE = ["AdaptiveSearchTimeline", "SearchTimeline",
                     "AdaptiveSearchTimelineQuery", "SearchTimelineQuery"]

    for op, qid, src, gap in pairs[:12]:
        # 同じ qid で op を差し替えながら試す（404対策）
        for op_try in [op] + [x for x in OP_ORDER_BASE if x != op]:
            url = f"https://x.com/i/api/graphql/{qid}/{op_try}"

            base_features = _default_features()
            field_toggles = _default_field_toggles()

            variables = {
                "rawQuery": f"to:{screen_name}",
                "count": page_count,
                "querySource": "typed_query",
                "product": "Latest",
            }
            params = {
                "variables": json.dumps(variables, separators=(",", ":")),
                "features": json.dumps(base_features, separators=(",", ":")),
                "fieldToggles": json.dumps(field_toggles, separators=(",", ":")),
            }

            r = s.get(url, headers=headers, params=params, timeout=20)
            _log(f"[STEP] graphql({op_try} [{src}/gap={gap}] to:{screen_name}) -> {r.status_code} : url={url}")
            tried += 1

            # 400(features不足) は自動補完で再試行
            if r.status_code == 400:
                text = r.text[:2000]
                feat1 = _augment_features_from_error(base_features, text)
                if feat1 != base_features:
                    params["features"] = json.dumps(feat1, separators=(",", ":"))
                    r = s.get(url, headers=headers, params=params, timeout=20)
                    _log(f"[STEP] graphql({op_try} retry1 with augmented features) -> {r.status_code}")
                if r.status_code == 400:
                    text = r.text[:2000]
                    feat2 = _augment_features_from_error(feat1, text)
                    if feat2 != feat1:
                        params["features"] = json.dumps(feat2, separators=(",", ":"))
                        r = s.get(url, headers=headers, params=params, timeout=20)
                        _log(f"[STEP] graphql({op_try} retry2 with augmented features) -> {r.status_code}")

            if r.status_code == 404:
                continue
            if r.status_code != 200:
                return False, None, r.text[:800]

            # ---- 200: ページネーションで “取りこぼし” を回収 ----
            try:
                # 集約器：tweet_id 一意化しつつ created_at 補完
                by_id = {}  # id -> record

                def _ingest_page(json_obj: dict):
                    # created_at 補完マップ
                    created_map = _build_created_map_from_search_timeline(json_obj)

                    # すべての候補を吸い込む
                    for rid, text, created in _yield_tweet_candidates(json_obj):
                        rid_s = str(rid)
                        if rid_s in by_id:
                            continue
                        created = created or created_map.get(rid_s)

                        # 可能なら UTC/JST に正規化
                        utc, jst = _normalize_created_at(created)

                        by_id[rid_s] = {
                            "tweet_id": rid_s,
                            "text": text,
                            "created_at": created,
                            "created_at_utc": utc,
                            "created_at_jst": jst,
                        }

                data = r.json()
                _ingest_page(data)

                # カーソルを辿って追加ページも取得（最大 6 ページ）
                cursor = _find_bottom_cursor(data)
                pages = 1
                while (len(by_id) < limit) and cursor and pages < 6:
                    variables["cursor"] = cursor
                    params["variables"] = json.dumps(variables, separators=(",", ":"))
                    r2 = s.get(url, headers=headers, params=params, timeout=20)
                    _log(f"[STEP] graphql({op_try} page{pages+1}) -> {r2.status_code}")

                    if r2.status_code == 400:
                        # features は前段で補完済み想定。念のため一度だけ増補試行
                        text = r2.text[:2000]
                        featx = _augment_features_from_error(json.loads(params["features"]), text)
                        if featx:
                            params["features"] = json.dumps(featx, separators=(",", ":"))
                            r2 = s.get(url, headers=headers, params=params, timeout=20)
                            _log(f"[STEP] graphql({op_try} page{pages+1} retry with features) -> {r2.status_code}")

                    if r2.status_code != 200:
                        break

                    data2 = r2.json()
                    _ingest_page(data2)
                    cursor = _find_bottom_cursor(data2)
                    pages += 1

                # 新しい順（UTC降順）に並べて limit 件
                results_all = sorted(
                    by_id.values(),
                    key=lambda x: (x["created_at_utc"] or ""),
                    reverse=True
                )
                results = results_all[:limit]

                return (True, results, None) if results else (False, None, "no replies found")

            except Exception as ex:
                return False, None, f"parse error: {ex}"

    return False, None, f"all {tried} (op,qid) candidates exhausted"

from typing import Optional, Any

def _find_bottom_cursor(data: dict) -> Optional[str]:
    """
    SearchTimeline のレスポンスから Bottom/BOTTOMV2 カーソル値を探して返す
    """
    try:
        instr = (data.get("data", {})
                    .get("search_by_raw_query", {})
                    .get("search_timeline", {})
                    .get("timeline", {})
                    .get("instructions", []))
    except Exception:
        return None

    def walk(x: Any) -> Optional[str]:
        if isinstance(x, dict):
            # 新旧いずれの表記にも対応
            ct = (x.get("cursorType") or x.get("displayType") or "").lower()
            if ct in ("bottom", "bottomv2"):
                v = x.get("value")
                if v:
                    return v
            for v in x.values():
                got = walk(v)
                if got:
                    return got
        elif isinstance(x, list):
            for v in x:
                got = walk(v)
                if got:
                    return got
        return None

    for inst in instr:
        got = walk(inst)
        if got:
            return got
    return None

def _coerce_tweet_node(res: dict) -> dict:
    """
    result が TweetWithVisibilityResults の場合に中の tweet/result を取り出す
    """
    if not isinstance(res, dict):
        return res
    t = res.get("__typename")
    if t == "TweetWithVisibilityResults":
        tw = res.get("tweet")
        if isinstance(tw, dict):
            return tw.get("result") or tw
    return res


def fetch_replies_to_me_graphql_bk2(s, headers, screen_name, limit=5):
    if screen_name.startswith("@"):
        screen_name = screen_name[1:]

    pairs = collect_searchtimeline_pairs_with_session(s)
    if not pairs:
        return False, None, "no (op,qid) candidates"

    tried = 0
    for op, qid, src, gap in pairs[:12]:
        url = f"https://x.com/i/api/graphql/{qid}/{op}"

        variables = {
            "rawQuery": f"to:{screen_name}",
            "count": limit,
            "querySource": "typed_query",
            "product": "Latest",
        }
        base_features = _default_features()
        field_toggles = _default_field_toggles()

        # 1回目の試行
        params = {
            "variables": json.dumps(variables, separators=(",", ":")),
            "features": json.dumps(base_features, separators=(",", ":")),
            "fieldToggles": json.dumps(field_toggles, separators=(",", ":")),
        }
        r = s.get(url, headers=headers, params=params, timeout=20)
        _log(f"r={r}")
        _log(f"[STEP] graphql({op} [{src}/gap={gap}] to:{screen_name}) -> {r.status_code} : url={url}")
        tried += 1

        # 400（features null）の場合は最大2回まで不足分を自動追加してリトライ
        if r.status_code == 400:
            text = r.text[:2000]
            # 1回目の増補
            feat1 = _augment_features_from_error(base_features, text)
            if feat1 != base_features:
                params["features"] = json.dumps(feat1, separators=(",", ":"))
                r = s.get(url, headers=headers, params=params, timeout=20)
                _log(f"[STEP] graphql({op} retry1 with augmented features) -> {r.status_code}")

            # それでも 400 ならもう一度増補
            if r.status_code == 400:
                text = r.text[:2000]
                feat2 = _augment_features_from_error(feat1, text)
                if feat2 != feat1:
                    params["features"] = json.dumps(feat2, separators=(",", ":"))
                    r = s.get(url, headers=headers, params=params, timeout=20)
                    _log(f"[STEP] graphql({op} retry2 with augmented features) -> {r.status_code}")

        if r.status_code == 404:
            continue  # 別の (op,qid) を試す
        if r.status_code != 200:
            return False, None, r.text[:800]

        # ---- 200: 重複を除去し、作成日時で“新しい順”に並べて limit 件だけ返す ----
        try:
            data = r.json()

            # created_at が取れない場合のフォールバック用にマップを作る
            created_map = _build_created_map_from_search_timeline(data)

            # いったん全部集めて tweet_id で一意化（同じIDは最新created_atを採用）
            by_id = {}  # id -> record
            for rid, text, created in _yield_tweet_candidates(data):
                rid_s = str(rid)
                created = created or created_map.get(rid_s)

                # 正規化（UTC/JST 文字列 'YYYY-mm-dd HH:MM:SS' へ）
                utc, jst = _normalize_created_at(created)
                # 文字列比較でOKなように UTC をキーにする（Noneは空文字に）
                utc_key = utc or ""

                rec = {
                    "tweet_id": rid_s,
                    "text": text,
                    "created_at": created,          # 生の値（元の互換用）
                    "created_at_utc": utc,          # 追加: UTC
                    "created_at_jst": jst,          # 追加: JST
                }

                # 既にあるなら、新しい方（UTC文字列が大きい方）を残す
                old = by_id.get(rid_s)
                if (old is None) or ((utc_key) and (utc_key > (old.get("created_at_utc") or ""))):
                    by_id[rid_s] = rec

            # 新しい順（UTC降順）にソート
            results_all = sorted(
                by_id.values(),
                key=lambda x: (x["created_at_utc"] or ""),
                reverse=True
            )

            # 先頭 limit 件だけ返す
            results = results_all[:limit]

            return (True, results, None) if results else (False, None, "no replies found")
        except Exception as ex:
            return False, None, f"parse error: {ex}"


    return False, None, f"all {tried} (op,qid) candidates exhausted"

from typing import Any

def _build_created_map_from_search_timeline(data: dict) -> dict:
    """
    GraphQL SearchTimeline の JSON から {tweet_id: created_at} を収集
    """
    m = {}

    def _add(res: dict):
        if not isinstance(res, dict):
            return
        legacy = res.get("legacy") or {}
        tid = res.get("rest_id") or legacy.get("id_str")
        created = legacy.get("created_at")
        if tid and created and str(tid) not in m:
            m[str(tid)] = created

    try:
        instr = (
            data.get("data", {})
                .get("search_by_raw_query", {})
                .get("search_timeline", {})
                .get("timeline", {})
                .get("instructions", [])
        )
        for inst in instr:
            for entry in inst.get("entries", []):
                content = entry.get("content", {}) or {}
                item = content.get("itemContent") or {}

                # 普通の Tweet
                res = (item.get("tweet_results") or {}).get("result")
                if isinstance(res, dict):
                    _add(res)

                # items がネストしてる場合
                for it in content.get("items", []):
                    ic = (it.get("item") or {}).get("itemContent") or {}
                    res2 = (ic.get("tweet_results") or {}).get("result")
                    if isinstance(res2, dict):
                        _add(res2)

            # ピン留め対応
            if inst.get("type") == "TimelinePinEntry":
                entry = inst.get("entry", {}) or {}
                content = entry.get("content", {}) or {}
                item = content.get("itemContent") or {}
                res = (item.get("tweet_results") or {}).get("result")
                if isinstance(res, dict):
                    _add(res)
    except Exception:
        pass

    return m

def fetch_replies_to_me_graphql_bk1(s, headers, screen_name, limit=5):
    if screen_name.startswith("@"):
        screen_name = screen_name[1:]

    pairs = collect_searchtimeline_pairs_with_session(s)
    if not pairs:
        return False, None, "no (op,qid) candidates"

    tried = 0
    for op, qid, src, gap in pairs[:12]:
        url = f"https://x.com/i/api/graphql/{qid}/{op}"

        variables = {
            "rawQuery": f"to:{screen_name}",
            "count": limit,
            "querySource": "typed_query",
            "product": "Latest",
        }
        base_features = _default_features()
        field_toggles = _default_field_toggles()

        # 1回目の試行
        params = {
            "variables": json.dumps(variables, separators=(",", ":")),
            "features": json.dumps(base_features, separators=(",", ":")),
            "fieldToggles": json.dumps(field_toggles, separators=(",", ":")),
        }
        r = s.get(url, headers=headers, params=params, timeout=20)
        _log(f"[STEP] graphql({op} [{src}/gap={gap}] to:{screen_name}) -> {r.status_code} : url={url}")
        tried += 1

        # 400（features null）の場合は最大2回まで不足分を自動追加してリトライ
        if r.status_code == 400:
            text = r.text[:2000]
            # 1回目の増補
            feat1 = _augment_features_from_error(base_features, text)
            if feat1 != base_features:
                params["features"] = json.dumps(feat1, separators=(",", ":"))
                r = s.get(url, headers=headers, params=params, timeout=20)
                _log(f"[STEP] graphql({op} retry1 with augmented features) -> {r.status_code}")

            # それでも 400 ならもう一度増補
            if r.status_code == 400:
                text = r.text[:2000]
                feat2 = _augment_features_from_error(feat1, text)
                if feat2 != feat1:
                    params["features"] = json.dumps(feat2, separators=(",", ":"))
                    r = s.get(url, headers=headers, params=params, timeout=20)
                    _log(f"[STEP] graphql({op} retry2 with augmented features) -> {r.status_code}")

        if r.status_code == 404:
            continue  # 別の (op,qid) を試す
        if r.status_code != 200:
            return False, None, r.text[:800]

        # ---- 200: 重複ツイート（tweet_id）を除去して limit をユニーク基準で適用 ----
        try:
            data = r.json()
            results = []
            seen_ids = set()  # 追加: 一意化用セット
            for rid, text, created_at in _yield_tweet_candidates(data):
                print("created_at")
                print(created_at)
                if rid in seen_ids:
                    continue  # 重複はスキップ
                seen_ids.add(rid)
                results.append({
                    "tweet_id": rid,
                    "text": text,
                    "created_at": created_at
                })
                if len(results) >= limit:  # ユニーク件数でカウント
                    break

            return (True, results, None) if results else (False, None, "no replies found")
        except Exception as ex:
            return False, None, f"parse error: {ex}"

    return False, None, f"all {tried} (op,qid) candidates exhausted"


# --- GraphQL.py 追記（または既存 get_tweets の下あたりに） ---

def _session_and_headers_from_firefox_profile(profile):
    """
    Firefoxプロファイルからcookieを取り、認証済みセッションと共通ヘッダを返す。
    """
    _log("[START] _session_and_headers_from_firefox_profile")
    a, c, e = get_x_cookies_from_firefox(profile)
    if e:
        _log(f"[ERR] Cookie取得エラー: {e}")
        return None, None

    s = _new_session()
    _set_cookies(s, a, c)

    bearer   = fetch_web_bearer_token_with_session(s)
    query_id = fetch_usertweets_query_id_with_session(s)  # 取得しておく（tweetsで使う）
    _log(f"[STEP] bearer(head)={bearer[:20]}..., userTweetsQueryId={query_id}")

    headers = {
        "authorization": f"Bearer {bearer}",
        "x-csrf-token": c,
        "x-twitter-auth-type": "OAuth2Session",
        "x-twitter-active-user": "yes",
        "x-twitter-client-language": "ja",
        "accept-language": "ja,en-US;q=0.9",
        "referer": "https://x.com/",
        "origin": "https://x.com",
        "accept": "*/*",
    }
    auth = s.get("https://x.com/i/api/1.1/account/settings.json", headers=headers, timeout=12)
    if not auth.ok:
        _log(auth.text[:300]); _log("[ERR] X 認証が無効")
        return None, None
    return s, headers


def _normalize_result_rows(rows):
    """
    rows: [{"tweet_id","text","created_at","type","reply_to_tweet_id"}...]
    -> created_at_utc/jst を付加
    """
    print("_normalize_result_rows")

    out = []
    for tw in rows:
        print(tw.get("created_at"))
        utc_str, jst_str = _normalize_created_at(tw.get("created_at"))
        out.append({
            "tweet_id": tw["tweet_id"],
            "text": tw["text"],
            "created_at_raw": tw.get("created_at"),
            "created_at_utc": utc_str,
            "created_at_jst": jst_str,
            "type": tw.get("type"),
            "reply_to_tweet_id": tw.get("reply_to_tweet_id")
        })
    return out

