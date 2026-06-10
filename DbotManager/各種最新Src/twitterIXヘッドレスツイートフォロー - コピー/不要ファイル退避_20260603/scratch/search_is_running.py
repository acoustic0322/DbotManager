import os

def search_files(directory):
    for root, dirs, files in os.walk(directory):
        if 'node_modules' in dirs:
            dirs.remove('node_modules')
        if '.gemini' in dirs:
            dirs.remove('.gemini')
        if '.git' in dirs:
            dirs.remove('.git')
        for file in files:
            if file.endswith('.py'):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8', errors='ignore') as f:
                        for idx, line in enumerate(f):
                            if 'is_engagement_running' in line:
                                print(f"{path} Line {idx+1}: {line.strip()}")
                except Exception as e:
                    print(f"Error reading {path}: {e}")

def main():
    search_files('.')

if __name__ == "__main__":
    main()
