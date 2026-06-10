import os

def main():
    target = 'modules/mutual_follow/db_manager.py'
    if not os.path.exists(target):
        print("File does not exist")
        return
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if 'system_commands' in line:
                print(f"Line {idx+1}: {line.strip()}")

if __name__ == "__main__":
    main()
