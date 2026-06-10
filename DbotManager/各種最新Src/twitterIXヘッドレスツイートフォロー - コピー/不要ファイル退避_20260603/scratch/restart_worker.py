import subprocess
import psutil
import os
import time

def main():
    target_pid = 17568
    print(f"Targeting worker PID: {target_pid}")
    
    # 1. Kill the target worker process
    try:
        proc = psutil.Process(target_pid)
        print(f"Killing process: {proc.name()} ({target_pid})")
        proc.kill()
        proc.wait(timeout=5)
        print("Process killed successfully.")
    except Exception as e:
        print(f"Error killing process or process already dead: {e}")
        
    time.sleep(2)
    
    # 2. Spawn a new worker service in a visible console window
    print("Spawning new worker_service.py in a new console...")
    try:
        # We spawn cmd /k python worker_service.py in a new console
        subprocess.Popen(
            ['cmd', '/k', 'python', 'worker_service.py'],
            creationflags=subprocess.CREATE_NEW_CONSOLE
        )
        print("New worker spawned successfully.")
    except Exception as e:
        print(f"Failed to spawn new worker: {e}")

if __name__ == '__main__':
    main()
