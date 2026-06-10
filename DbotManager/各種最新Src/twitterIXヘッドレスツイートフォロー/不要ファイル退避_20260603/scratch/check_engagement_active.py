import psutil

print("Searching for active engagement_handler.py processes...")
found = False
for p in psutil.process_iter():
    try:
        cmd = p.cmdline()
        if cmd and any('engagement_handler.py' in str(arg) for arg in cmd):
            print(f"Found active process: PID {p.pid} | Name: {p.name()} | Cmdline: {cmd}")
            found = True
    except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
        pass

if not found:
    print("No active engagement_handler.py processes found.")
