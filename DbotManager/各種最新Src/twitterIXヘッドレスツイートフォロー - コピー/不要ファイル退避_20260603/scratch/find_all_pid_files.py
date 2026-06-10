import os

def main():
    print("=== Searching for worker_*.pid files ===")
    for root, dirs, files in os.walk('.'):
        # Limit search depth to avoid crawling Google Drive deeply
        depth = root.count(os.sep)
        if depth > 1:
            continue
        for file in files:
            if file.startswith("worker_") and file.endswith(".pid"):
                path = os.path.join(root, file)
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        content = f.read().strip()
                    print(f"Path: {path} | Content: {content}")
                except Exception as e:
                    print(f"Path: {path} | Error: {e}")

if __name__ == '__main__':
    main()
