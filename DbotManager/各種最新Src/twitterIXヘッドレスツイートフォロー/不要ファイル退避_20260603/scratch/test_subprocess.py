import subprocess
import sys
import time
import os

def main():
    test_file = "scratch/test_out.txt"
    if os.path.exists(test_file):
        os.remove(test_file)
        
    # Command list
    args = [sys.executable, '-c', f"import time; open('{test_file}', 'w').write('executed')" ]
    
    # Spawn using the exact worker_service method
    cmd = ['cmd', '/k'] + args
    print(f"Spawning: {cmd}")
    p = subprocess.Popen(cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    
    time.sleep(3)
    
    # Check if file was written
    if os.path.exists(test_file):
        print("Success: File was written!")
        with open(test_file, 'r') as f:
            print(f"Content: {f.read()}")
    else:
        print("Failure: File was NOT written!")
        
    # Clean up
    try:
        p.terminate()
    except: pass

if __name__ == "__main__":
    main()
