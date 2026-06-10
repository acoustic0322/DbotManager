import time
import os
import sys
import socket
import json

WORKER_PID_FILE = "worker_PC_02.pid" # Mock file name matching Sub PC format

def get_worker_process_optimized():
    # 1. Fast Path: Check PID file validation first (extremely fast!)
    if os.path.exists(WORKER_PID_FILE):
        try:
            with open(WORKER_PID_FILE, 'r', encoding='utf-8') as f:
                pid = int(f.read().strip())
            try:
                import psutil
                proc = psutil.Process(pid)
                # Verify that the process cmdline matches worker_service.py
                cmdline = proc.cmdline()
                if cmdline and 'worker_service.py' in ' '.join(cmdline):
                    return pid
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                # Clean up stale PID file
                if os.path.exists(WORKER_PID_FILE):
                    try: os.remove(WORKER_PID_FILE)
                    except: pass
        except Exception:
            pass

    # 2. Slow Path Fallback: Scan process list dynamically and write PID file
    # Uses fast batching parameters in process_iter to minimize performance penalty
    try:
        import psutil
        for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
            try:
                name = proc.info['name'].lower()
                if 'python' in name or 'py' in name:
                    cmdline = proc.info['cmdline']
                    if cmdline and 'worker_service.py' in ' '.join(cmdline):
                        pid = proc.info['pid']
                        # Self-heal by writing the PID file for future fast paths
                        try:
                            with open(WORKER_PID_FILE, 'w', encoding='utf-8') as f:
                                f.write(str(pid))
                        except:
                            pass
                        return pid
            except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                pass
    except Exception:
        pass

    return None

def main():
    print("=== Benchmarking Process Detection Logic ===")
    
    # 1. Clean run without PID file (should use fallback scan)
    if os.path.exists(WORKER_PID_FILE):
        try: os.remove(WORKER_PID_FILE)
        except: pass
        
    start_t = time.time()
    pid = get_worker_process_optimized()
    duration_scan = time.time() - start_t
    print(f"Fallback scan - Found PID: {pid} | Duration: {duration_scan*1000:.3f} ms")
    
    # Check if PID file was created
    if not os.path.exists(WORKER_PID_FILE):
        print("Error: PID file was not created by fallback scan!")
        return
        
    # 2. Subsequent run with PID file (should use fast path)
    start_t = time.time()
    pid2 = get_worker_process_optimized()
    duration_fast = time.time() - start_t
    print(f"Fast path - Found PID: {pid2} | Duration: {duration_fast*1000:.3f} ms")
    
    if pid == pid2:
        print("Success: PIDs match and fast path is working.")
        print(f"Speedup ratio: {duration_scan / duration_fast:.1f}x faster!")
    else:
        print("Error: PIDs do not match.")

if __name__ == '__main__':
    main()
