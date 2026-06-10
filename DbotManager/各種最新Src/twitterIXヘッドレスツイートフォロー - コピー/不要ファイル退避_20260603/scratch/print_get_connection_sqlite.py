def main():
    with open('modules/mutual_follow/db_manager.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for j in range(94, 124):
        if j < len(lines):
            print(f"{j+1}: {lines[j].rstrip()}")

if __name__ == '__main__':
    main()
