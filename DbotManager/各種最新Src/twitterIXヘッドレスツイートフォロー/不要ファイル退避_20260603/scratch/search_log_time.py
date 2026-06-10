import os
import sys

def main():
    target = 'logs/engagement.log'
    if not os.path.exists(target):
        print("Log not found")
        return
        
    start_time = "2026-05-19 18:00"
    end_time = "2026-05-19 18:02"
    printing = False
    
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for line in f:
            if start_time in line:
                printing = True
            if end_time in line:
                printing = False
            if printing:
                safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                print(safe_line)

if __name__ == '__main__':
    main()
