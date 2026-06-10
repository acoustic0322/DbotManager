def main():
    with open('modules/mutual_follow/db_manager.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        if 'def get_connection' in line:
            for j in range(0, 30):
                if idx + j < len(lines):
                    print(f"{idx+1+j}: {lines[idx+j].rstrip()}")

if __name__ == '__main__':
    main()
