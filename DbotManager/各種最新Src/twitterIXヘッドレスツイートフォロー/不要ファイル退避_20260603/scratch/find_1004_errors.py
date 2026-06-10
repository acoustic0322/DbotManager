import os
import sys

def main():
    target = 'logs/engagement.log'
    if not os.path.exists(target):
        print("Log file not found")
        return
        
    print("=== Analyzing 1004 errors in engagement.log ===")
    errors = []
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if "1004" in line or "Profile open failed" in line:
                errors.append((idx + 1, line.strip()))
                
    print(f"Total 1004/Profile open failures found: {len(errors)}")
    for line_num, err in errors[-20:]:  # Show the last 20 errors
        safe_err = err.encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
        print(f"Line {line_num}: {safe_err}")

if __name__ == '__main__':
    main()
