import json
import psycopg2

try:
    with open('db_config.json', 'r', encoding='utf-8') as f:
        conf = json.load(f)['postgres']
    
    conn = psycopg2.connect(conf['uri'])
    cursor = conn.cursor()
    
    cursor.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='public'")
    tables = cursor.fetchall()
    print("Tables:", tables)
    
    cursor.execute("SELECT * FROM system_commands ORDER BY id DESC LIMIT 5")
    commands = cursor.fetchall()
    print("Latest Commands:", commands)
    
    conn.close()
except Exception as e:
    print("Error:", e)
