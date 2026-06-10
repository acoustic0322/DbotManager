import ctypes

# Constants
ES_CONTINUOUS = 0x80000000
ES_SYSTEM_REQUIRED = 0x00000001
ES_DISPLAY_REQUIRED = 0x00000002

def prevent_sleep():
    """Prevents the system from entering sleep mode."""
    try:
        # ES_SYSTEM_REQUIRED: Prevents idle to sleep
        # ES_DISPLAY_REQUIRED: Prevents display sleep (optional, maybe user wants screen off but PC on? 
        # usually for bots users want to see what happens, or at least PC must run. 
        # Let's keep display on too to be safe/visible or just SYSTEM is enough? 
        # Let's do SYSTEM | DISPLAY to be safe.)
        ctypes.windll.kernel32.SetThreadExecutionState(
            ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED
        )
        print("[System] Sleep mode disabled (High Performance).")
    except Exception as e:
        print(f"[System] Failed to set execution state: {e}")

def allow_sleep():
    """Allows the system to sleep again."""
    try:
        ctypes.windll.kernel32.SetThreadExecutionState(ES_CONTINUOUS)
        print("[System] Sleep mode re-enabled.")
    except Exception as e:
        print(f"[System] Failed to reset execution state: {e}")
