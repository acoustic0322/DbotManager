import pymysql
import json
import re
import config

conn = pymysql.connect(
    host=config.db_host,
    user='root',
    password='abcd1234',
    database='d_bot',
    charset='utf8mb4',
    cursorclass=pymysql.cursors.DictCursor
)

with conn.cursor() as cursor:

    cursor.execute("""
        SELECT id, cookies
        FROM account_master
        WHERE cookies IS NOT NULL
    """)

    rows = cursor.fetchall()

    for row in rows:

        account_id = row['id']
        cookies = row['cookies']

        try:
            # 正常ならそのまま確認
            json.loads(cookies)
            print(f"[OK] {account_id}")
            continue

        except Exception:

            fixed = cookies

            # g_state 修正
            fixed = re.sub(
                r'"g_state": "({.*?})"',
                lambda m: '"g_state": ' + json.dumps(m.group(1)),
                fixed
            )

            # personalization_id 修正
            fixed = fixed.replace(
                '""v1_',
                '"v1_'
            ).replace(
                '==""',
                '=="'
            )

            try:
                json.loads(fixed)

                cursor.execute("""
                    UPDATE account_master
                    SET cookies = %s
                    WHERE id = %s
                """, (fixed, account_id))

                print(f"[FIXED] {account_id}")

            except Exception as e:
                print(f"[FAILED] {account_id} {e}")

conn.commit()
conn.close()