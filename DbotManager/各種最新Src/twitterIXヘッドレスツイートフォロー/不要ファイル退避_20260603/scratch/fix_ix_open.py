import sys
import os
sys.path.append(os.getcwd())
from modules.ixbrowser.ixbrowser_controller import IXBrowserController
ctrl = IXBrowserController()
profiles = ctrl.client.get_profile_list(limit=200)
if not profiles:
    print("No profiles found.")
    sys.exit(0)

open_pids = []
for p in profiles:
    status = p.get("status")
    name = p.get("name")
    pid = p.get("profile_id")
    print(f"{name} (ID: {pid}): Status={status}")
    if status == 1: # 1 means Open in IXBrowser
        open_pids.append(pid)

if open_pids:
    print(f"\nFound {len(open_pids)} open profiles on IX side. Closing them now...")
    for pid in open_pids:
        print(f"Closing {pid}...")
        ctrl.close_browser(pid)
    print("All targeted profiles sent close command.")
else:
    print("\nNo profiles were marked as status=1 (Open) in the API.")
