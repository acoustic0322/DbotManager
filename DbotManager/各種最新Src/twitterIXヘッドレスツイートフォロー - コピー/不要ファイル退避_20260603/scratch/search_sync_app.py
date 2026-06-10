import os
import sys

def main():
    target = 'app.py'
    if not os.path.exists(target):
        print(f"File {target} not found")
        return
        
    print("=== Searching app.py for sync/group/import keywords ===")
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if 'import_accounts_from_group' in line or 'group_sync' in line.lower() or 'sync_groups' in line.lower():
                safe_line = line.strip().encode('utf-8', errors='replace').decode('utf-8')
                sys.stdout.buffer.write(f"Line {idx+1}: {safe_line}\n".encode('utf-8', errors='replace'))

if __name__ == '__main__':
    main()
