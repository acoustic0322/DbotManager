import os
import sys

def main():
    target = 'logs/engagement.log'
    if not os.path.exists(target):
        print("Log not found")
        return
        
    start_time = "2026-05-19 18:03:20"
    end_time = "2026-05-19 18:04:15"
    
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if len(line) >= 19:
                ts = line[:19]
                if ts >= start_time and ts <= end_time:
                    safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                    print(safe_line)

if __name__ == '__main__':
    main()
