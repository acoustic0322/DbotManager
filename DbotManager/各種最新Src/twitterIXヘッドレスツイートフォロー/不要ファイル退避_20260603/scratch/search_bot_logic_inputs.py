import os
import sys

def main():
    target = 'modules/ixbrowser/bot_logic_dp.py'
    if not os.path.exists(target):
        print("File not found")
        return
        
    terms = [".input("]
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            for term in terms:
                if term in line:
                    safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                    print(f"Line {idx+1}: {safe_line}")
                    break

if __name__ == '__main__':
    main()
