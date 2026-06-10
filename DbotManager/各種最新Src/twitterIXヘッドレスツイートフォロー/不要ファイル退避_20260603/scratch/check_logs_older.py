import os
import sys

def main():
    target = 'logs/engagement.log'
    print(f"\n=== Lines from {target} ===")
    if not os.path.exists(target):
        print("File not found")
        return
        
    with open(target, 'r', encoding='utf-8', errors='replace') as f:
        lines = f.readlines()
        # Print lines from -250 to -50
        for l in lines[-250:-50]:
            safe_l = l.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
            print(safe_l)

if __name__ == "__main__":
    main()
