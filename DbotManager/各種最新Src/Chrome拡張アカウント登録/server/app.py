from __future__ import annotations

import json
import logging
import os
from contextlib import contextmanager
from typing import Iterator

import pymysql
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ==========================================================
# 初期設定
# ==========================================================

load_dotenv()

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s %(levelname)s %(message)s",
)

logger = logging.getLogger("x-account-sync")

API_TOKEN = os.getenv("API_TOKEN", "")

DB_HOST = os.getenv("DB_HOST", "127.0.0.1")
DB_PORT = int(os.getenv("DB_PORT", "3306"))
DB_USER = os.getenv("DB_USER", "")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_NAME = os.getenv("DB_NAME", "")

DEFAULT_VPS_ID = int(os.getenv("DEFAULT_VPS_ID", "2"))

# ==========================================================
# リクエストモデル
# ==========================================================


class XAccountData(BaseModel):

    twitter_id: str = ""
    screen_name: str = Field(min_length=1, max_length=100)

    display_name: str = ""

    twitter_user_id: str = Field(
        min_length=1,
        max_length=45,
    )

    auth_token: str = Field(
        min_length=1,
        max_length=100,
    )

    ct0: str = Field(min_length=1)

    twid: str = ""

    cookies: dict[str, str] = Field(default_factory=dict)

    cookie_string: str = ""

    user_agent: str = ""
    sec_ch_ua: str = ""

    impersonate: str = "chrome"

    exported_at: str | None = None
    source_url: str | None = None


class AccountRequest(BaseModel):

    username: str = Field(min_length=1, max_length=45)
    password: str = Field(min_length=1, max_length=45)

    account: XAccountData


# ==========================================================
# FastAPI
# ==========================================================

app = FastAPI(
    title="X Account Sync API",
    version="2.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type"],
)

# ==========================================================
# 共通処理
# ==========================================================


def require_api_token(
    authorization: str | None = Header(default=None),
) -> None:

    if not API_TOKEN:
        raise HTTPException(
            500,
            "サーバーのAPI_TOKENが未設定です。",
        )

    if authorization != f"Bearer {API_TOKEN}":
        raise HTTPException(
            401,
            "APIトークンが正しくありません。",
        )


@contextmanager
def db_connection() -> Iterator[pymysql.connections.Connection]:

    connection = pymysql.connect(
        host=DB_HOST,
        port=DB_PORT,
        user=DB_USER,
        password=DB_PASSWORD,
        database=DB_NAME,
        charset="utf8mb4",
        cursorclass=pymysql.cursors.DictCursor,
        autocommit=False,
        connect_timeout=10,
        read_timeout=20,
        write_timeout=20,
    )

    try:
        yield connection

    finally:
        connection.close()


def get_user(connection, username, password):

    with connection.cursor() as cursor:

        cursor.execute(
            """
            SELECT
                id,
                username,
                enable
            FROM
                user_master
            WHERE
                username = %s
                AND password = %s
            LIMIT 1
            """,
            (username, password),
        )

        user = cursor.fetchone()

    if not user:
        raise HTTPException(
            401,
            "ユーザーIDまたはパスワードが正しくありません。",
        )

    if int(user.get("enable") or 0) != 1:
        raise HTTPException(
            403,
            "このユーザーは無効です。",
        )

    return user


def norm_name(value):
    return value.strip().lstrip("@")


def cookie_json(account):
    return json.dumps(
        account.cookies,
        ensure_ascii=False,
        separators=(",", ":"),
    )


# ==========================================================
# API
# ==========================================================


@app.get("/health")
def health():
    return {"status": "ok"}

# ==========================================================
# アカウント追加
# ==========================================================

@app.post(
    "/api/account/add",
    dependencies=[Depends(require_api_token)],
)
def add_account(req: AccountRequest):

    account = req.account
    name = norm_name(account.screen_name or account.twitter_id)

    try:

        with db_connection() as connection:

            user = get_user(
                connection,
                req.username,
                req.password,
            )

            user_id = user["id"]

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id
                    FROM
                        account_master
                    WHERE
                        user_id = %s
                        AND twitter_user_id = %s
                    LIMIT 1
                    """,
                    (
                        str(user_id),
                        account.twitter_user_id,
                    ),
                )

                if cursor.fetchone():
                    raise HTTPException(
                        409,
                        "このXアカウントは既に登録されています。",
                    )

                cursor.execute(
                    """
                    SELECT
                        id
                    FROM
                        account_master
                    WHERE
                        name = %s
                    LIMIT 1
                    """,
                    (name,),
                )

                if cursor.fetchone():
                    raise HTTPException(
                        409,
                        "同じXユーザー名のアカウントが既に登録されています。",
                    )

                cursor.execute(
                    """
                    INSERT INTO account_master
                    (
                        vps_id,
                        user_id,
                        name,
                        twitter_user_id,
                        login_id,
                        account_name,
                        display_name,
                        auth_token,
                        cookies,
                        user_agent,
                        sec_ch_ua,
                        inpersonate,
                        ct0,
                        regist_type,
                        enable,
                        is_cookie_expired
                    )
                    VALUES
                    (
                        %s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,
                        1,0
                    )
                    """,
                    (
                        DEFAULT_VPS_ID,
                        str(user_id),
                        name,
                        account.twitter_user_id,
                        name,
                        account.display_name or name,
                        account.display_name,
                        account.auth_token,
                        cookie_json(account),
                        account.user_agent[:200],
                        account.sec_ch_ua[:100],
                        account.impersonate[:45],
                        account.ct0,
                        "react",
                    ),
                )

                account_id = cursor.lastrowid

            connection.commit()

        logger.info(
            "Account added account_id=%s user_id=%s twitter_user_id=%s",
            account_id,
            user_id,
            account.twitter_user_id,
        )

        return {
            "status": "ok",
            "action": "added",
            "account_id": account_id,
            "message": f"@{name} を追加しました。",
        }

    except HTTPException:
        raise

    except pymysql.err.IntegrityError as ex:

        logger.exception("Integrity error")

        raise HTTPException(
            409,
            f"重複データのため追加できませんでした。({ex.args[0]})",
        ) from ex

    except pymysql.MySQLError as ex:

        logger.exception("DB error")

        raise HTTPException(
            500,
            f"データベース処理に失敗しました。({ex.args[0]})",
        ) from ex


# ==========================================================
# アカウント更新
# ==========================================================

@app.post(
    "/api/account/update",
    dependencies=[Depends(require_api_token)],
)
def update_account(req: AccountRequest):

    account = req.account
    name = norm_name(account.screen_name or account.twitter_id)

    try:

        with db_connection() as connection:

            user = get_user(
                connection,
                req.username,
                req.password,
            )

            user_id = user["id"]

            with connection.cursor() as cursor:

                cursor.execute(
                    """
                    SELECT
                        id,
                        name
                    FROM
                        account_master
                    WHERE
                        user_id = %s
                        AND twitter_user_id = %s
                    LIMIT 1
                    """,
                    (
                        str(user_id),
                        account.twitter_user_id,
                    ),
                )

                target = cursor.fetchone()

                if not target:
                    raise HTTPException(
                        404,
                        "更新対象のXアカウントが見つかりません。先にアカウント追加を実行してください。",
                    )

                cursor.execute(
                    """
                    SELECT
                        id
                    FROM
                        account_master
                    WHERE
                        name = %s
                        AND id <> %s
                    LIMIT 1
                    """,
                    (
                        name,
                        target["id"],
                    ),
                )

                if cursor.fetchone():
                    raise HTTPException(
                        409,
                        "変更後のXユーザー名が別アカウントで使用されています。",
                    )

                cursor.execute(
                    """
                    UPDATE account_master
                    SET
                        name                = %s,
                        login_id            = %s,
                        account_name        = %s,
                        display_name        = %s,
                        auth_token          = %s,
                        cookies             = %s,
                        user_agent          = %s,
                        sec_ch_ua           = %s,
                        inpersonate         = %s,
                        ct0                 = %s,
                        is_cookie_expired   = 0
                    WHERE
                        id = %s
                        AND user_id = %s
                    """,
                    (
                        name,
                        name,
                        account.display_name or name,
                        account.display_name,
                        account.auth_token,
                        cookie_json(account),
                        account.user_agent[:200],
                        account.sec_ch_ua[:100],
                        account.impersonate[:45],
                        account.ct0,
                        target["id"],
                        str(user_id),
                    ),
                )

                connection.commit()

                if cursor.rowcount == 0:
                    logger.info(
                        "No changes. account_id=%s user_id=%s",
                        target["id"],
                        user_id,
                    )

                    return {
                        "status": "ok",
                        "action": "unchanged",
                        "account_id": target["id"],
                        "message": "変更はありません（最新です）。",
                    }

                logger.info(
                    "Account updated account_id=%s user_id=%s twitter_user_id=%s",
                    target["id"],
                    user_id,
                    account.twitter_user_id,
                )

                return {
                    "status": "ok",
                    "action": "updated",
                    "account_id": target["id"],
                    "message": f"@{name} を更新しました。",
                }

    except HTTPException:
        raise

    except pymysql.err.IntegrityError as ex:

        logger.exception("Integrity error")

        raise HTTPException(
            409,
            f"重複データのため更新できませんでした。({ex.args[0]})",
        ) from ex

    except pymysql.MySQLError as ex:

        logger.exception("DB error")

        raise HTTPException(
            500,
            f"データベース処理に失敗しました。({ex.args[0]})",
        ) from ex    