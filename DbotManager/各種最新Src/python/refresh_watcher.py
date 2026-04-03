import time
import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from twitter_api_v2 import proc_refresh_queue
from config import outputLog

while True:
    try:
        proc_refresh_queue()
    except Exception as e:
        outputLog(f"エラー: {e}")
    time.sleep(5)