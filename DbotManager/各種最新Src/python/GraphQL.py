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
        created = (legacy or {}).get("created_at")
        if text:
            return rest_id, text, created
    # パターン2: TweetWithVisibilityResults
    tw = node.get("tweet")
    if isinstance(tw, dict):
        leg2 = tw.get("legacy")
        rest_id = tw.get("rest_id") or (leg2 or {}).get("id_str")
        if rest_id:
            text = (leg2 or {}).get("full_text") or (tw.get("note_tweet_results", {}).get("result", {}) or {}).get("text") or tw.get("text")
            created = (leg2 or {}).get("created_at")
            if text:
                return rest_id, text, created
    return None

def _yield_tweet_candidates(obj: Any):
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

def fetch_searchtimeline_query_id_with_session(s: requests.Session) -> Optional[str]:
    """
    abs.twimg.com の client-web チャンク(main/vendor含む)を総当たりし、
    SearchTimeline 系の queryId を robust に抽出して最初の1件を返す。
    見つからなければ None。
    """
    js_urls = _fetch_main_js_urls_with_session(s)

    # ① operationName 候補（大小混在対策）
    name_candidates = [
        "SearchTimeline",
        "searchTimeline",
        "AdaptiveSearchTimeline",
        "SearchTimelineQuery",
        "AdaptiveSearchTimelineQuery",
    ]

    # ② 代表的な2順序（operationName → queryId / queryId → operationName）
    #   a) ..."operationName":"SearchTimeline"... "queryId":"XXXX"...
    pat_op_then_qid = re.compile(
        r'"operationName"\s*:\s*"(?:' + "|".join(name_candidates) + r')".{0,1500}?"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"',
        re.IGNORECASE | re.DOTALL
    )
    #   b) ..."queryId":"XXXX"... "operationName":"SearchTimeline"...
    pat_qid_then_op = re.compile(
        r'"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})".{0,1500}?"operationName"\s*:\s*"(?:' + "|".join(name_candidates) + r')"',
        re.IGNORECASE | re.DOTALL
    )

    # ③ 旧来のマップ形式 ..."SearchTimeline": {"queryId":"XXXX", ...}
    pat_named_map = re.compile(
        r'"(?:' + "|".join(name_candidates) + r')"\s*:\s*\{\s*"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"',
        re.IGNORECASE | re.DOTALL
    )

    # ④ URL 直書き検出 /i/api/graphql/<qid>/SearchTimeline
    pat_url_embed = re.compile(
        r'/i/api/graphql/([A-Za-z0-9_-]{10,})/(?:' + "|".join(name_candidates) + r')\b',
        re.IGNORECASE
    )

    # ⑤ fallback: 名前だけ先に見つけ、近傍±4000文字を再スキャン
    pat_name_only = re.compile(
        r'"operationName"\s*:\s*"(?:' + "|".join(name_candidates) + r')"',
        re.IGNORECASE
    )
    pat_qid_generic = re.compile(r'"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"', re.IGNORECASE)

    seen = set()
    for js_url in js_urls:
        r = s.get(js_url, headers={"Accept": "*/*", "Referer": "https://x.com/"}, timeout=15)
        if not r.ok:
            continue
        text = r.text

        # a) op → qid
        m = pat_op_then_qid.search(text)
        if m:
            qid = m.group(1)
            if qid not in seen:
                _log(f"[STEP] Found (op→qid) in {js_url}: {qid}")
                return qid
        # b) qid → op
        m = pat_qid_then_op.search(text)
        if m:
            qid = m.group(1)
            if qid not in seen:
                _log(f"[STEP] Found (qid→op) in {js_url}: {qid}")
                return qid
        # c) named map
        m = pat_named_map.search(text)
        if m:
            qid = m.group(1)
            if qid not in seen:
                _log(f"[STEP] Found (named map) in {js_url}: {qid}")
                return qid
        # d) URL 埋め込み
        m = pat_url_embed.search(text)
        if m:
            qid = m.group(1)
            if qid not in seen:
                _log(f"[STEP] Found (url embed) in {js_url}: {qid}")
                return qid

        # e) 近傍スキャン：まず名前の位置を全部拾って、その周辺に queryId が無いか再検索
        for nm in pat_name_only.finditer(text):
            start = max(0, nm.start() - 4000)
            end   = min(len(text), nm.end() + 4000)
            window = text[start:end]
            mq = pat_qid_generic.search(window)
            if mq:
                qid = mq.group(1)
                if qid not in seen:
                    _log(f"[STEP] Found (vicinity scan) in {js_url}: {qid}")
                    return qid

    return None


def fetch_searchtimeline_query_id_with_session_bk1(s: requests.Session) -> str:
    """
    js_urls 全部を走査して GraphQL SearchTimeline 系の queryId を取得
    """
    js_urls = _fetch_main_js_urls_with_session(s)

    name_patterns = [
        "SearchTimeline",
        "searchTimeline",
        "AdaptiveSearchTimeline"
    ]
    combined_pattern = re.compile(
        r'"(?:' + "|".join(name_patterns) + r')[^"]*"\s*:\s*\{\s*"queryId"\s*:\s*"([A-Za-z0-9_-]{10,})"',
        re.IGNORECASE | re.DOTALL
    )

    for js_url in js_urls:
        print(js_url)
        r = s.get(js_url, headers={"Accept": "*/*", "Referer": "https://x.com/"}, timeout=15)
        if not r.ok:
            continue

        m = combined_pattern.search(r.text)
        if m:
            qid = m.group(1)
            _log(f"[STEP] Found SearchTimeline queryId in {js_url}: {qid}")
            return qid

    return None


def fetch_replies_to_me_graphql(s, headers, screen_name, limit=5):
    """
    GraphQL SearchTimeline を使って自分宛のリプライを取得
    - screen_name: @なし or @付き どちらでもOK
    - limit: 最大取得件数
    戻り値: (ok, [dict...], err)
    """
    if screen_name.startswith("@"):
        screen_name = screen_name[1:]

    query_id = fetch_searchtimeline_query_id_with_session(s)
    if not query_id:
        return False, None, "queryId not found for SearchTimeline"

    url = f"https://x.com/i/api/graphql/{query_id}/SearchTimeline"

    variables = {
        "rawQuery": f"to:{screen_name}",
        "count": limit,
        "querySource": "typed_query",
        "product": "Latest"  # 最新順に取得
    }
    params = {
        "variables": json.dumps(variables, separators=(",", ":")),
        "features": json.dumps(_default_features(), separators=(",", ":")),
        "fieldToggles": json.dumps(_default_field_toggles(), separators=(",", ":")),
    }

    r = s.get(url, headers=headers, params=params, timeout=15)
    _log(f"[STEP] graphql(SearchTimeline to:{screen_name}) -> {r.status_code}")
    if r.status_code != 200:
        return False, None, r.text[:800]

    try:
        data = r.json()
        results = []
        # 既存のツイート抽出ロジックを流用
        for rid, text, created in _yield_tweet_candidates(data):
            results.append({
                "tweet_id": rid,
                "text": text,
                "created_at": created
            })
            if len(results) >= limit:
                break

        if results:
            return True, results, None
        else:
            return False, None, "no replies found"
    except Exception as ex:
        return False, None, f"parse error: {ex}"
