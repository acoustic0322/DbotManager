def main():
    with open('modules/ixbrowser/bot_logic_dp.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        if 'tweet' in line.lower() or 'post' in line.lower() or 'send' in line.lower():
            # Filter to relevant lines to avoid log overload
            if any(k in line.lower() for k in ['def ', 'click', 'text', 'button', 'status', 'error', 'fail']):
                clean = line.strip().encode('ascii', errors='replace').decode('ascii')
                print(f"Line {idx+1}: {clean}")

if __name__ == '__main__':
    main()
