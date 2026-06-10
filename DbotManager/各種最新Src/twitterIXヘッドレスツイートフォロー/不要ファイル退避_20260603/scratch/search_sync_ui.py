import os
import sys

def main():
    target = 'app.py'
    if not os.path.exists(target):
        print(f"File {target} not found")
        return
        
    print("=== Searching app.py for sync-related UI keywords ===")
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if any(term in line.lower() for term in ['sync', '同期', 'インポート', 'import']):
                # Filter out obvious logging or comment-only lines if too many, but let's see
                safe_line = line.strip().encode('utf-8', errors='replace').decode('utf-8')
                sys.stdout.buffer.write(f"Line {idx+1}: {safe_line}\n".encode('utf-8', errors='replace'))

if __name__ == '__main__':
    main()
