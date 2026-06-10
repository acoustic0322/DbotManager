import os
import sys

def main():
    target = 'engagement_handler.py'
    if not os.path.exists(target):
        print("File not found")
        return
        
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if 'Distributed' in line or 'my_pc_index' in line or 'all_pc_ids' in line:
                safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                print(f"Line {idx+1}: {safe_line}")

if __name__ == "__main__":
    main()
