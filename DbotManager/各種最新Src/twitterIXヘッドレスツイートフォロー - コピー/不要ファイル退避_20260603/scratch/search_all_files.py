import os
import sys

def main():
    search_term = 'PC操作'
    print(f"Searching for: {search_term}")
    for root, dirs, files in os.walk('.'):
        for file in files:
            if file.endswith('.py') or file.endswith('.bat') or file.endswith('.json'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()
                        if search_term in content:
                            print(f"Found in {path}")
                            # Print matching lines
                            f.seek(0)
                            for idx, line in enumerate(f):
                                if search_term in line:
                                    print(f"  Line {idx+1}: {line.strip()}")
                except Exception as e:
                    pass

if __name__ == "__main__":
    main()
