import os

path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\app.py'
if not os.path.exists(path):
    print("app.py not found")
    exit(1)

with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# Remove auto-start logic
old_logic = """    # --- Auto-start Worker Service ---
    if not get_worker_process():
        start_worker()
        st.sidebar.success("🟢 Worker Started")
    else:
        st.sidebar.success("🟢 Worker Online")"""

new_logic = """    # --- Auto-start Worker Service ---
    # DISABLED: Auto-starting was causing infinite worker spawning due to Windows PID check failures.
    # Workers should be started manually via FORCE_RESET.bat or worker_service.py directly.
    if get_worker_process():
        st.sidebar.success("🟢 Worker Online")
    else:
        st.sidebar.warning("🟡 Worker Offline (Run FORCE_RESET.bat)")"""

if old_logic in content:
    content = content.replace(old_logic, new_logic)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully removed auto-start logic from app.py.")
else:
    print("Auto-start logic not found or already removed.")
