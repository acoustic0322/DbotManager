import os
import sys

def main():
    target = 'app.py'
    if not os.path.exists(target):
        print("File not found")
        return
        
    with open(target, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx in range(1720, min(1820, len(lines))):
        line = lines[idx]
        safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
        print(f"Line {idx+1}: {safe_line}")

if __name__ == "__main__":
    main()
