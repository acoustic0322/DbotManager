from modules.mutual_follow.db_manager import DBManager
import json
import os
import psutil

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
        pid_str = f.read().strip()
    print(f"Worker PID file exists: {pid_str}")
    try:
        pid = int(pid_str)
        if psutil.pid_exists(pid):
            proc = psutil.Process(pid)
            print(f"Worker process (PID {pid}) is RUNNING. Name: {proc.name()}")
        else:
            print(f"Worker process (PID {pid}) is NOT running (stale PID file).")
    except Exception as e:
        print(f"Could not check process status: {e}")
else:
    print("Worker PID file does not exist.")
