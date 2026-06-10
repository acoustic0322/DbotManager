def main():
    with open('engagement_handler.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        if 'def execute_actions' in line:
            print(f"Line {idx+1}: {line.strip()}")
            for j in range(1, 40):
                if idx + j < len(lines):
                    print(f"  {idx+1+j}: {lines[idx+j].rstrip()}")

if __name__ == '__main__':
    main()
