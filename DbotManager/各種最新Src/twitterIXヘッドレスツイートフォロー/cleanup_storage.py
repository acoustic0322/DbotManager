import os
import shutil
import time
from datetime import datetime, timedelta

# --- 設定 ---
TARGET_DRIVE = "E:"
TARGET_DIR = r"E:\Browser Data"
FREE_PERCENT_THRESHOLD = 50.0  # 維持したい空き容量（％）
SAFE_WINDOW_HOURS = 1         # 1時間以内に使ったものは保護（それ以外は削除対象）

def get_free_percent(path):
    total, used, free = shutil.disk_usage(path)
    return (free / total) * 100

def cleanup():
    now_ts = time.time()
    safe_threshold_ts = now_ts - (SAFE_WINDOW_HOURS * 3600)
    
    print(f"[{datetime.now()}] Storage cleanup check started...")
    
    try:
        free_pct = get_free_percent(TARGET_DRIVE)
        print(f"Current free space: {free_pct:.2f}% (Target: {FREE_PERCENT_THRESHOLD}%)")
        
        if free_pct < FREE_PERCENT_THRESHOLD:
            print(f"Free space is low. Starting deletion of old caches...")
            
            # フォルダ一覧を取得
            folders = []
            for entry in os.scandir(TARGET_DIR):
                if entry.is_dir():
                    mtime = entry.stat().st_mtime
                    # 安全期間を過ぎているものだけをリストアップ
                    if mtime < safe_threshold_ts:
                        folders.append({
                            'path': entry.path,
                            'mtime': mtime
                        })
            
            # 古い順にソート
            folders.sort(key=lambda x: x['mtime'])
            
            if not folders:
                print("No old profiles found (all used within 1 hour).")
                return

            deleted_count = 0
            for folder in folders:
                try:
                    # 削除実行
                    shutil.rmtree(folder['path'])
                    deleted_count += 1
                    
                    # 進行状況を表示
                    if deleted_count % 10 == 0:
                        current_free = get_free_percent(TARGET_DRIVE)
                        print(f"  ...Deleting ({deleted_count} done), Current free: {current_free:.2f}%")
                    
                    # 削除ごとに容量チェック（目標達成したら停止）
                    if get_free_percent(TARGET_DRIVE) >= FREE_PERCENT_THRESHOLD:
                        print(f"Success: Target free space {FREE_PERCENT_THRESHOLD}% achieved.")
                        break
                except Exception as e:
                    # 実行中のものは削除できないためスキップ
                    continue
            
            print(f"Final Result: Deleted {deleted_count} profile caches.")
        else:
            print("Free space is sufficient.")
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    cleanup()
