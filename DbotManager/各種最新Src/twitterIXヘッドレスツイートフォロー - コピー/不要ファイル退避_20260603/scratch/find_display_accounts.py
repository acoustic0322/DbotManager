def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        if 'display_accounts' in line:
            print(f"Line {idx+1}: {line.strip()}")

if __name__ == '__main__':
    main()
