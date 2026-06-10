import psutil
import os
import sys

def main():
    print("=== Current Python Process Status ===")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'].lower()
            if 'python' in name or 'py' in name or 'streamlit' in name:
                cmdline = proc.info['cmdline']
                cmd_str = ' '.join(cmdline) if cmdline else ''
                if any(x in cmd_str for x in ['app.py', 'worker_service.py', 'engagement_handler.py', 'streamlit']):
                    print(f"PID: {proc.info['pid']} | Name: {proc.info['name']} | Cmd: {cmd_str}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

if __name__ == '__main__':
    main()
