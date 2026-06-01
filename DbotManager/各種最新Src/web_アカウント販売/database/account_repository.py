import pandas as pd

from database.db import engine

def get_accounts(user_name):

    sql = """
    SELECT
        am.id ,
        name ,
        account_name ,
        follow_count ,
        followers_count ,
        reach_status ,
        check_full_status_enable ,
        price ,
        is_locked ,
        is_suspended ,
        is_unauthorized
    FROM account_master am
    LEFT JOIN user_master um 
        on um.id = am.user_id 
    WHERE um.username = %s
    ORDER BY am.id
    """

    df = pd.read_sql(
        sql,
        engine,
        params=(user_name,)
    )

    # ステータス生成
    def build_status(row):

        if row["is_suspended"] == 1:
            return "SUSPENDED"

        if row["is_locked"] == 1:
            return "LOCKED"

        if row["is_unauthorized"] == 1:
            return "UNAUTHORIZED"

        return "ACTIVE"

    df["status"] = df.apply(build_status, axis=1)

    # 表示用ID
    df["id_text"] = "@" + df["account_name"].fillna("")

    return df