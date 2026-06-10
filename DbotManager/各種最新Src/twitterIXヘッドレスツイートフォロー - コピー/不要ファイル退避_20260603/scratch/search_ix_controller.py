import os

def main():
    target = 'modules/ixbrowser/ixbrowser_controller.py'
    if not os.path.exists(target):
        print("File does not exist")
        return
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if 'def open_browser_dp' in line or '1004' in line or 'Profile open failed' in line:
                print(f"Line {idx+1}: {line.strip()}")

if __name__ == "__main__":
    main()
