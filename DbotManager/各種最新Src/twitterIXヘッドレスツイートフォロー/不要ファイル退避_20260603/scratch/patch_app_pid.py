import os
import re

path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\app.py'
if not os.path.exists(path):
    print("app.py not found")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Replace the static WORKER_PID_FILE with a dynamic one
old_pid_def = "WORKER_PID_FILE = 'worker.pid'"

new_pid_def = """import socket
def get_worker_pid_file():
    hostname = socket.gethostname()
    pc_id = hostname
    try:
        if os.path.exists('config.json'):
            import json
            with open('config.json', 'r', encoding='utf-8') as f:
                pc_map = json.load(f).get('PC_MAP', {})
                if hostname in pc_map:
                    pc_id = pc_map[hostname]
    except: pass
    return f"worker_{pc_id}.pid"

WORKER_PID_FILE = get_worker_pid_file()"""

if old_pid_def in content:
    content = content.replace(old_pid_def, new_pid_def)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("app.py successfully patched to stop infinite spawning.")
else:
    print("Could not find WORKER_PID_FILE definition. It may have already been updated.")
