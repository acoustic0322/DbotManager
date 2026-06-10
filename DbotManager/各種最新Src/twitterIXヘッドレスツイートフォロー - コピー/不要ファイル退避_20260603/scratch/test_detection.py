import psutil
import sys
import os

# We import the function from worker_service
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from worker_service import is_engagement_running

def main():
    print("Checking if engagement_handler is running right now:")
    running = is_engagement_running()
    print(f"Result: {running}")
    
    print("\nSimulating a completed cmd window that is still open:")
    # We find if there's any cmd.exe process in the system with engagement_handler in its cmdline
    cmd_found = False
    for proc in psutil.process_iter():
        try:
            name = proc.name().lower()
            if 'cmd' in name:
                cmdline = proc.cmdline()
                if cmdline and 'engagement_handler.py' in ' '.join(cmdline):
                    print(f"Found residual cmd process: PID {proc.pid}, Cmdline: {cmdline}")
                    cmd_found = True
        except:
            pass
            
    if not cmd_found:
        print("No residual cmd windows found in system.")
        
    print("\nVerifying that our detection ignores cmd.exe:")
    # Double check if any cmd.exe is erroneously flagged as running
    flagged = False
    for proc in psutil.process_iter():
        try:
            cmdline = proc.cmdline()
            if cmdline and 'engagement_handler.py' in ' '.join(cmdline):
                name = proc.name().lower()
                is_python = 'python' in name or 'py' in name
                print(f"Process PID {proc.pid} ({name}) contains engagement_handler.py in cmdline. Is Python? {is_python}")
                if not is_python:
                    print("--> Correctly ignored by python-only check.")
                else:
                    print("--> Flagged as active (True).")
                    flagged = True
        except:
            pass

if __name__ == "__main__":
    main()
