import os

def main():
    target = 'app.py'
    if not os.path.exists(target):
        print(f"File {target} not found")
        return
        
    print("=== Searching app.py for delete/削除 keywords ===")
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if 'delete' in line.lower() or '削除' in line:
                print(f"Line {idx+1}: {line.strip()}")

if __name__ == '__main__':
    main()
