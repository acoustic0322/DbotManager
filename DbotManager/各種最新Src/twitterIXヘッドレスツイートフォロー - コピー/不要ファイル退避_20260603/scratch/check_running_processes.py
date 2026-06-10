import psutil
import sys

def main():
    print("=== Active Python Processes ===")
    for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
        try:
            name = proc.info['name'].lower()
            if 'python' in name or 'py' in name or 'cmd' in name:
                cmdline = proc.info['cmdline']
                cmdline_str = ' '.join(cmdline) if cmdline else 'N/A'
                print(f"PID: {proc.info['pid']} | Name: {proc.info['name']} | Cmd: {cmdline_str}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

if __name__ == '__main__':
    main()
