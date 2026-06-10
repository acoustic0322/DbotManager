import os
import sys

def main():
    target = 'app.py'
    if not os.path.exists(target):
        return
    with open(target, 'r', encoding='utf-8', errors='ignore') as f:
        for idx, line in enumerate(f):
            if 'st.sidebar' in line or 'page =' in line or 'selectbox(' in line:
                if 'st.sidebar.markdown' not in line:
                    safe_line = line.strip().encode(sys.stdout.encoding or 'utf-8', errors='replace').decode(sys.stdout.encoding or 'utf-8')
                    print(f"Line {idx+1}: {safe_line}")

if __name__ == "__main__":
    main()
