from modules.mutual_follow.db_manager import DBManager
import json
import os

db = DBManager()
cmd = db.get_global_command()
if cmd:
    print("Latest Global Command:")
    print(json.dumps(cmd, indent=2, default=str))
else:
    print("No global command found in system_commands table.")

# Check if worker is running
pid_file = "worker.pid"
if os.path.exists(pid_file):
    with open(pid_file, 'r') as f:
        pid = f.read().strip()
    print(f"Worker PID file exists: {pid}")
    import psutil
    try:
        if psutil.pid_exists(int(pid)):
            print(f"Worker process (PID {pid}) is RUNNING.")
        else:
            print(f"Worker process (PID {pid}) is NOT running (stale PID file).")
    except:
        print("Could not check process status.")
else:
    print("Worker PID file does not exist.")
