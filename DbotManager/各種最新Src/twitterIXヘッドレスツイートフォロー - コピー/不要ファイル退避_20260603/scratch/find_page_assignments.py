def main():
    with open('app.py', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    for idx, line in enumerate(lines):
        if 'st.session_state.page = "選手権"' in line or "st.session_state.page = '選手権'" in line:
            print(f"Line {idx+1}: {line.strip()}")
            # Print 5 lines before and after
            for j in range(-5, 6):
                if 0 <= idx + j < len(lines):
                    print(f"  {idx+1+j}: {lines[idx+j].strip()}")

if __name__ == '__main__':
    main()
