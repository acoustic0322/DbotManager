import time
import subprocess
import sys
import os
import socket
from loguru import logger
import psutil

# VERSION: 2.1.3 (Foolproof Singleton & Execution Lock)
VERSION = "2.1.4"

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from modules.mutual_follow.db_manager import DBManager

def is_engagement_running():
    """実行中（engagement_handler.py）のプロセスがあるか確実な方法で確認"""
    try:
        for proc in psutil.process_iter():
            try:
                name = proc.name().lower()
                if 'python' in name or 'py' in name:
                    cmdline = proc.cmdline()
                    if cmdline and 'engagement_handler.py' in ' '.join(cmdline):
                        return True
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception as e:
        logger.error(f"process_iter error: {e}")
    return False

def main():
    hostname = socket.gethostname()
    pc_id = hostname
    try:
        if os.path.exists('config.json'):
            import json
            with open('config.json', 'r', encoding='utf-8') as f:
                pc_map = json.load(f).get('PC_MAP', {})
                if hostname in pc_map:
                    pc_id = pc_map[hostname]
    except: pass

    # 1. 物理ファイルロックによる完全な二重起動防止（Windows権限バグ回避）
    # Google Drive上の同期ロック競合を避けるため、ローカルのC:\tempを使用
    local_temp = "C:\\temp"
    if not os.path.exists(local_temp):
        try: os.makedirs(local_temp)
        except: pass
    
    lock_file_path = os.path.join(local_temp, f"worker_{pc_id}.lock")
    lock_file = open(lock_file_path, "w")
    try:
        import msvcrt
        # LK_NBLCK (非ブロッキングロック): すでにロックされていれば即座に IOError を投げる
        msvcrt.locking(lock_file.fileno(), msvcrt.LK_NBLCK, 1)
    except IOError:
        logger.warning(f"[{pc_id}] Worker is strictly locked by another local process (C:\\temp). Exiting.")
        return

    # Write PID file for app.py to read directly (fast path)
    pid_file_path = f"worker_{pc_id}.pid"
    try:
        with open(pid_file_path, "w", encoding="utf-8") as f:
            f.write(str(os.getpid()))
    except Exception as pid_err:
        logger.warning(f"Failed to write PID file {pid_file_path}: {pid_err}")

    logger.info(f"Worker Service (v{VERSION}) started on {pc_id}")
    
    last_id_file = os.path.join(local_temp, f"worker_{pc_id}_last_id.txt")
    last_processed_id = 0
    if os.path.exists(last_id_file):
        try:
            with open(last_id_file, 'r', encoding='utf-8') as f:
                last_processed_id = int(f.read().strip())
            logger.info(f"Loaded last processed command ID from local storage: {last_processed_id}")
        except Exception as e:
            logger.warning(f"Failed to read last processed ID file: {e}")
            last_processed_id = 0

    if last_processed_id == 0:
        try:
            init_db = DBManager()
            init_cmd = init_db.get_global_command()
            if init_cmd:
                latest_id = init_cmd.get('id', 0)
                created_at = init_cmd.get('created_at')
                
                is_fresh = False
                if created_at:
                    from datetime import datetime, UTC
                    if hasattr(created_at, 'tzinfo') and created_at.tzinfo is not None:
                        created_at_naive = created_at.astimezone(UTC).replace(tzinfo=None)
                    elif isinstance(created_at, str):
                        try:
                            created_at_naive = datetime.strptime(created_at.split('.')[0], "%Y-%m-%d %H:%M:%S")
                        except:
                            created_at_naive = None
                    else:
                        created_at_naive = created_at
                    
                    if created_at_naive:
                        now_utc = datetime.now(UTC).replace(tzinfo=None)
                        age_seconds = (now_utc - created_at_naive).total_seconds()
                        if age_seconds < 300:
                            is_fresh = True
                            logger.info(f"Detected fresh command ID {latest_id} created {age_seconds:.1f}s ago.")
                
                if is_fresh:
                    last_processed_id = latest_id - 1
                else:
                    last_processed_id = latest_id
                
                logger.info(f"Worker initialized. Monitoring commands strictly newer than ID: {last_processed_id}")
            else:
                logger.info("No commands found in database on startup.")
                last_processed_id = 0
        except Exception as e:
            logger.warning(f"Failed to fetch initial command state: {e}")
            last_processed_id = 0

    while True:
        try:
            db = DBManager()
            db.report_heartbeat()
            
            cmd_info = db.get_global_command()
            if cmd_info:
                current_id = cmd_info.get('id')
                command = cmd_info.get('command')
                params_str = cmd_info.get('params', '{}')
                
                if current_id > last_processed_id:
                    logger.info(f"!!! NEW COMMAND DETECTED !!! ID: {current_id} ({command})")
                    last_processed_id = current_id
                    
                    # Save last processed ID to local storage
                    try:
                        with open(last_id_file, 'w', encoding='utf-8') as f:
                            f.write(str(current_id))
                    except Exception as e:
                        logger.warning(f"Failed to save last processed ID to local storage: {e}")
                    
                    if command == "START_ENGAGEMENT":
                        # 2. すでに実行中なら重複して起動しない（連打バグ回避）
                        if is_engagement_running():
                            logger.warning("engagement_handler.py is already running. Ignoring duplicate command.")
                        else:
                            import json
                            params = json.loads(params_str)
                            args = [sys.executable, 'engagement_handler.py']
                            if params.get('url'): args += ['--url', params['url']]
                            if params.get('count'): args += ['--count', str(params['count'])]
                            if params.get('rt_count'): args += ['--rt-count', str(params['rt_count'])]
                            if params.get('follow_count'): args += ['--follow-count', str(params['follow_count'])]
                            if params.get('tweet_count'): args += ['--tweet-count', str(params['tweet_count'])]
                            if params.get('tweet_image'): args += ['--tweet-image']
                            if params.get('visible'): args += ['--visible']
                            
                            logger.info(f"Launching engagement_handler: {args}")
                            subprocess.Popen(['cmd', '/k'] + args, creationflags=subprocess.CREATE_NEW_CONSOLE)
                        
                    elif command == "STOP_ALL":
                        if sys.platform == 'win32':
                            os.system('taskkill /F /IM python.exe /FI "WINDOWTITLE ne worker_service.py*"')
                            os.system('taskkill /F /IM ixbrowser.exe')
                        logger.info("STOP_ALL executed.")
                        
                    elif command == "CLEAN_IXBROWSER":
                        logger.info("Executing IXBrowser ghost profile cleanup...")
                        from modules.ixbrowser.ixbrowser_local_api import IXBrowserClient
                        cli = IXBrowserClient()
                        open_list = cli.get_open_profiles()
                        if open_list:
                            pids = [p.get('profile_id', p.get('id')) for p in open_list]
                            pids = [pid for pid in pids if pid]
                            if pids:
                                cli.close_profiles_batch(pids)
                                time.sleep(3)
                            for p in cli.get_open_profiles() or []:
                                pid = p.get('profile_id', p.get('id'))
                                if pid: cli.reset_open_state(pid)
                        
                        # [NEW] Targeted OS-level zombie chrome process kill
                        try:
                            import psutil
                            killed = 0
                            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                                try:
                                    name = proc.info['name']
                                    if name and "chrome" in name.lower():
                                        cmdline = proc.info['cmdline']
                                        if cmdline:
                                            cmdline_str = " ".join(cmdline).lower()
                                            if "ixbrowser-resources" in cmdline_str:
                                                proc.kill()
                                                killed += 1
                                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                                    pass
                            if killed > 0:
                                logger.success(f"Force killed {killed} zombie IXBrowser Chrome processes.")
                        except Exception as ex:
                            logger.warning(f"Failed to run OS-level targeted Chrome kill: {ex}")
                            
                        logger.success("IXBrowser cleanup finished.")
            
            time.sleep(5) 
            
        except Exception as e:
            logger.error(f"Worker Error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()
