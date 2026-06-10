import os
import sys

def main():
    target = 'app.py'
    if not os.path.exists(target):
        print(f"File {target} not found")
        return
        
    print("=== Searching app.py for perform_delete_account calls ===")
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if 'perform_delete_account' in line:
                safe_line = line.strip().encode('utf-8', errors='replace').decode('utf-8')
                sys.stdout.buffer.write(f"Line {idx+1}: {safe_line}\n".encode('utf-8', errors='replace'))

if __name__ == '__main__':
    main()
