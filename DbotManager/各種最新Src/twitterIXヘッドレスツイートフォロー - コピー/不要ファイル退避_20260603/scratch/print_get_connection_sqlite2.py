def main():
    with open('modules/mutual_follow/db_manager.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for j in range(120, 160):
        if j < len(lines):
            # Encode and decode back to ignore bad chars or print only ascii
            line = lines[j].rstrip()
            print(f"{j+1}: {line.encode('ascii', errors='replace').decode('ascii')}")

if __name__ == '__main__':
    main()
