import os
import sys

def main():
    target = r"C:\Users\boxin\.gemini\antigravity\brain\47534015-4abb-4f0f-a549-ca227b036de7\.system_generated\logs\overview.txt"
    if not os.path.exists(target):
        print("overview.txt not found")
        return
        
    terms = ["speed_min", "speed_max", "typing", "タイピング", "秒"]
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            for term in terms:
                if term in line:
                    safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                    print(f"Line {idx+1} ({term}): {safe_line[:120]}...")
                    break

if __name__ == '__main__':
    main()
