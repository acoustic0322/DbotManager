from modules.ixbrowser.ixbrowser_controller import IXBrowserController
import json
import io
import sys

# Ensure UTF-8 output
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

ctrl = IXBrowserController()
groups = ctrl.get_all_groups()
excluded_ids = [283682, 274711, 261161, 274048, 260964, 255449, 253113, 277506, 248214]
excluded_kw = ['販売', 'サイト用', 'リンク渡す']

print("--- IXBrowser Group List ---")
for g in groups:
    gid = g.get('id')
    title = g.get('title', 'Unknown')
    if gid is None: continue
    
    is_excluded = (gid in excluded_ids) or any(k in title for k in excluded_kw)
    status = "[EXCLUDED]" if is_excluded else "[TARGET]"
    print(f"{status} | ID: {gid} | Name: {title}")
