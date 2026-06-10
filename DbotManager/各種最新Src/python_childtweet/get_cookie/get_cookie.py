import json
from . import ixBrowser_profile_manager
from . import x_login_manager
from DrissionPage import ChromiumPage

def get_cookie(credentials):

    username = credentials.get("login_id", "")
    password = credentials.get("password", "")
    tfa_key = credentials.get("tfa_key", "")
    auth_token = credentials.get("auth_token", "")

    try:

        # Chrome起動
        page = ChromiumPage()

        # Xログインページへ
        page.get("https://x.com/i/flow/login")

        time.sleep(3)

        # ユーザー名入力
        page.ele('tag:input').input(username)

        page.keyboard.enter()

        time.sleep(3)

        # パスワード入力
        inputs = page.eles('tag:input')

        if len(inputs) >= 2:
            inputs[1].input(password)
        else:
            return False, "password input not found"

        page.keyboard.enter()

        time.sleep(5)

        # TODO:
        # 2FA処理が必要ならここ追加

        # Cookie取得
        cookies = page.cookies(as_dict=True)

        # auth_token取得
        auth_token = cookies.get("auth_token", "")

        return True, {
            "auth_token": auth_token,
            "cookies": cookies,
            "user_agent": page.user_agent
        }

    except Exception as e:

        return False, str(e)

API_BASE = "http://127.0.0.1:53200/api/v2"

def get_cookie_bk(credentials):

    username = credentials.get("login_id", "")
    password = credentials.get("password", "")
    tfa_key = credentials.get("tfa_key", "")
    auth_token = credentials.get("auth_token", "")

    group_id = 250972

    profile_id = ixBrowser_profile_manager.get_or_create_profile(
        api_base=API_BASE,
        username=username,
        password=password,
        tfa_key=tfa_key,
        group_id=group_id
    )

    if not profile_id:
        return False, "profile create error"

    page, err_code = x_login_manager.open_ix_browser(
        API_BASE,
        profile_id
    )

    if not page:
        return False, f"browser open error {err_code}"

    success, new_cookies = x_login_manager.login_to_x(
        page=page,
        username=username,
        password=password,
        tfa_key=tfa_key,
        email="",
        auth_token=auth_token
    )

    x_login_manager.close_ix_browser(
        API_BASE,
        profile_id,
        page
    )

    if not success:
        return False, "login failed"

    return True, {
        "auth_token": new_cookies.get("auth_token", ""),
        "cookies": new_cookies,
        "user_agent": getattr(page, "user_agent", "")
    }