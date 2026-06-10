import os

path = r'h:\マイドライブ\twitterIXヘッドレスツイートフォロー\worker_service.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_func = """def is_engagement_running():
    \"\"\"実行中（engagement_handler.py）のプロセスがあるか確認\"\"\"
    try:
        for proc in psutil.process_iter(['cmdline']):
            cmdline = proc.info.get('cmdline')
            if cmdline and 'engagement_handler.py' in ' '.join(cmdline):
                return True
    except: pass
    return False"""

new_func = """def is_engagement_running():
    \"\"\"実行中（engagement_handler.py）のプロセスがあるか確実な方法で確認\"\"\"
    try:
        for proc in psutil.process_iter():
            try:
                cmdline = proc.cmdline()
                if cmdline and 'engagement_handler.py' in ' '.join(cmdline):
                    return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        logger.error(f"process_iter error: {e}")
    return False"""

if old_func in content:
    content = content.replace(old_func, new_func)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("Successfully patched is_engagement_running in worker_service.py")
else:
    print("Function not found, maybe already patched.")
