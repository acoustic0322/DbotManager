import os
import glob
import sys

def main():
    print("=== Searching for 1004 in logs/ ===")
    files = glob.glob("logs/*.log")
    for file in files:
        with open(file, 'r', encoding='utf-8', errors='ignore') as f:
            for idx, line in enumerate(f):
                if "1004" in line:
                    safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                    print(f"File: {file} | Line {idx+1}: {safe_line}")

if __name__ == '__main__':
    main()
