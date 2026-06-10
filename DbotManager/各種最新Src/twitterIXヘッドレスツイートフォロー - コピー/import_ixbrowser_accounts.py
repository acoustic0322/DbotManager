import sys
import subprocess
import os

if __name__ == "__main__":
    script_dir = os.path.dirname(os.path.abspath(__file__))
    target = os.path.join(script_dir, "data_import.py")
    cmd = [sys.executable, target] + sys.argv[1:]
    subprocess.run(cmd)
