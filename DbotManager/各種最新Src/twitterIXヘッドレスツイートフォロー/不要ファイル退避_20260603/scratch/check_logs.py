import os
import sys

def main():
    targets = ['bot.log', 'logs/engagement.log']
    for target in targets:
        print(f"\n=== Last 50 lines of {target} ===")
        if not os.path.exists(target):
            print("File not found")
            continue
            
        with open(target, 'r', encoding='utf-8', errors='replace') as f:
            lines = f.readlines()
            for l in lines[-50:]:
                safe_l = l.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                print(safe_l)

if __name__ == "__main__":
    main()
