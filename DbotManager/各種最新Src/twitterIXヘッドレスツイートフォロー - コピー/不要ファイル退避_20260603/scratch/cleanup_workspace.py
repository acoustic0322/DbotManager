import os
import shutil

ROOT_DIR = r"h:\マイドライブ\twitterIXヘッドレスツイートフォロー"

# 1. Exact root files to delete (temporary logs, CSVs, and text dumps)
JUNK_ROOT_FILES = [
    "direct_test.log",
    "direct_test_2.log",
    "direct_test_3.log",
    "direct_test_4.log",
    "direct_test_5.log",
    "worker_debug.log",
    "db_content.txt",
    "process_dump.txt",
    "process_dump_utf8.txt",
    "tasklist.csv",
    "tasklist_ps.csv",
    "full_res.json",
    "category_stats.txt",
    "checkprofiles.py",
    "test_check.py",
    "test_groq.py"
]

# 2. Temporary python files starting with 'tmp_' at root
def get_tmp_scripts():
    files = []
    if os.path.exists(ROOT_DIR):
        for name in os.listdir(ROOT_DIR):
            if name.startswith("tmp_") and name.endswith(".py"):
                files.append(name)
    return files

# 3. Timestamped/redundant log files inside logs/
def get_old_logs():
    logs = []
    logs_dir = os.path.join(ROOT_DIR, "logs")
    if os.path.exists(logs_dir):
        for name in os.listdir(logs_dir):
            if (name.startswith("engagement.2026") or name == "auth_session.log" or name == "account_mgmt.log" or name == "bulk_login.log") and name.endswith(".log"):
                logs.append(os.path.join("logs", name))
    return logs

def main():
    print("=" * 60)
    print(" [CLEAN] GOOGLE DRIVE WORKSPACE SAFE CLEANUP ")
    print("=" * 60)
    
    deleted_files = 0
    deleted_bytes = 0
    
    # Collect all targets
    targets = []
    
    # Add root junk files
    for f in JUNK_ROOT_FILES:
        path = os.path.join(ROOT_DIR, f)
        if os.path.exists(path) and os.path.isfile(path):
            targets.append(path)
            
    # Add tmp_ scripts
    for f in get_tmp_scripts():
        path = os.path.join(ROOT_DIR, f)
        if os.path.exists(path) and os.path.isfile(path):
            targets.append(path)
            
    # Add old log files
    for f in get_old_logs():
        path = os.path.join(ROOT_DIR, f)
        if os.path.exists(path) and os.path.isfile(path):
            targets.append(path)
            
    # Perform deletion of files
    if not targets:
        print("No junk or temporary files found to delete.")
    else:
        print(f"Found {len(targets)} unnecessary files to delete:")
        for path in targets:
            size = os.path.getsize(path)
            deleted_bytes += size
            try:
                os.remove(path)
                print(f"  - Deleted: {os.path.basename(path)} ({size / 1024:.1f} KB)")
                deleted_files += 1
            except Exception as e:
                print(f"  - Failed to delete {os.path.basename(path)}: {e}")

    # Remove __pycache__ folders recursively
    pycache_folders = []
    for root, dirs, files in os.walk(ROOT_DIR):
        if "__pycache__" in dirs:
            pycache_folders.append(os.path.join(root, "__pycache__"))
            
    if pycache_folders:
        print(f"\nFound {len(pycache_folders)} __pycache__ cache directories to delete:")
        for folder in pycache_folders:
            try:
                shutil.rmtree(folder)
                print(f"  - Deleted cache folder: {os.path.relpath(folder, ROOT_DIR)}")
            except Exception as e:
                print(f"  - Failed to delete cache folder {folder}: {e}")
                
    print("-" * 60)
    print(f"Cleanup Completed! Deleted {deleted_files} files saving {deleted_bytes / (1024 * 1024):.2f} MB.")
    print("Core scripts, DB, credentials, batch scripts, and modules are 100% untouched and safe.")
    print("=" * 60)

if __name__ == "__main__":
    main()
