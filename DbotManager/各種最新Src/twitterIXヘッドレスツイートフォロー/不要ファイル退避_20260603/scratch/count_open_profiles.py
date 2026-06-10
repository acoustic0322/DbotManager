import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)).replace('\\scratch', ''))
from modules.ixbrowser.ixbrowser_local_api import IXBrowserClient

def check():
    client = IXBrowserClient()
    open_list = client.get_open_profiles()
    print(f"--- IXBROWSER OPEN PROFILES CHECK ---")
    print(f"Count: {len(open_list)}")
    for p in open_list:
        pid = p.get('profile_id', p.get('id'))
        name = p.get('name')
        print(f" - ID: {pid}, Name: {name}")

if __name__ == "__main__":
    check()
