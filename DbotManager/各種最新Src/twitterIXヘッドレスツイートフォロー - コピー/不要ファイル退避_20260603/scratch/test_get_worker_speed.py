import time
import os
import sys

# Add root directory to sys.path
root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(root_dir)

# Mock Streamlit to import app.py without streamlit errors
class StreamlitMock:
    def __getattr__(self, name):
        if name in ('cache_data', 'cache_resource'):
            def decorator(*args, **kwargs):
                def wrapper(func):
                    return func
                return wrapper
            return decorator
        return StreamlitMock()
    def __enter__(self):
        return self
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass
    def __call__(self, *args, **kwargs):
        return StreamlitMock()
    def __contains__(self, item):
        return False
    def __getitem__(self, item):
        return None
    def __setitem__(self, key, value):
        pass

sys.modules['streamlit'] = StreamlitMock()

import app

def main():
    print("=== Testing get_worker_process speed ===")
    
    # 1. Clean run without PID file (should use fallback scan)
    if os.path.exists(app.WORKER_PID_FILE):
        try: os.remove(app.WORKER_PID_FILE)
        except: pass
        print("Removed existing PID file.")
        
    start_t = time.time()
    pid = app.get_worker_process()
    duration_scan = time.time() - start_t
    print(f"Fallback scan - Found PID: {pid} | Duration: {duration_scan*1000:.3f} ms")
    
    # 2. Subsequent run with PID file (should use fast path)
    if not os.path.exists(app.WORKER_PID_FILE):
        print("Error: PID file was not created by fallback scan!")
        return
        
    start_t = time.time()
    pid2 = app.get_worker_process()
    duration_fast = time.time() - start_t
    print(f"Fast path - Found PID: {pid2} | Duration: {duration_fast*1000:.3f} ms")
    
    if pid == pid2:
        print("Success: PIDs match and fast path is active.")
    else:
        print("Error: PIDs do not match.")

if __name__ == '__main__':
    main()
