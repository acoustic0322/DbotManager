def main():
    with open('modules/mutual_follow/db_manager.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        if 'def update_' in line:
            clean = line.strip().encode('ascii', errors='replace').decode('ascii')
            print(f"Line {idx+1}: {clean}")

if __name__ == '__main__':
    main()
