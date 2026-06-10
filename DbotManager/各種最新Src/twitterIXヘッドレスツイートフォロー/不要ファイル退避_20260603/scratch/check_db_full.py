import json
import psycopg2

try:
    with open('db_config.json', 'r', encoding='utf-8') as f:
        conf = json.load(f)['postgres']
    
    conn = psycopg2.connect(conf['uri'])
    cursor = conn.cursor()
    
    cursor.execute("SELECT username, selected, is_alive, sync_status FROM accounts WHERE selected=1")
    accounts = cursor.fetchall()
    print(f"Selected Accounts ({len(accounts)}):")
    for acc in accounts[:10]:
        print(acc)
    
    cursor.execute("SELECT id, command, params FROM system_commands ORDER BY id DESC LIMIT 1")
    cmd = cursor.fetchone()
    print("Latest Command:", cmd)
    
    conn.close()
except Exception as e:
    print("Error:", e)
