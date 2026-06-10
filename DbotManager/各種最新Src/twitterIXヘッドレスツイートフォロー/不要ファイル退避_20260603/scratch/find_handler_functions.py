def main():
    with open('engagement_handler.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        if 'def ' in line:
            clean = line.strip().encode('ascii', errors='replace').decode('ascii')
            print(f"Line {idx+1}: {clean}")

if __name__ == '__main__':
    main()
