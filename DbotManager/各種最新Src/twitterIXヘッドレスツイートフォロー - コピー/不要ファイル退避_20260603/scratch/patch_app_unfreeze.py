import os

with open('app.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

new_lines = []
i = 0
while i < len(lines):
    line = lines[i]
    
    # 1. 凍結一覧 individual clear
    if 'key=f"frozen_cl_{name}"' in line:
        new_lines.append(line)
        # The next line should be db.update_sync_status(...)
        next_line = lines[i+1]
        if 'db.update_sync_status' in next_line:
            new_lines.append('                            db.update_sync_status(acc.get(\'username\'), "")\n')
            new_lines.append('                            db.update_account_status(acc.get(\'username\'), is_suspended=False)\n')
            i += 2
            continue
            
    # 2. 実行失敗一覧 individual clear
    elif 'key=f"fail_cl_{name}"' in line:
        new_lines.append(line)
        next_line = lines[i+1]
        if 'db.update_sync_status' in next_line:
            new_lines.append('                            db.update_sync_status(acc.get(\'username\'), "")\n')
            new_lines.append('                            db.update_account_status(acc.get(\'username\'), is_suspended=False)\n')
            i += 2
            continue
            
    # 3. ログイン失敗一覧 individual clear
    elif 'key=f"login_fail_cl_{name}"' in line:
        new_lines.append(line)
        next_line = lines[i+1]
        if 'db.update_sync_status' in next_line:
            new_lines.append('                            db.update_sync_status(acc.get(\'username\'), "")\n')
            new_lines.append('                            db.update_account_status(acc.get(\'username\'), is_suspended=False)\n')
            i += 2
            continue
            
    # 4. ロック一覧 individual clear
    elif 'key=f"lock_cl_{name}"' in line:
        new_lines.append(line)
        next_line = lines[i+1]
        if 'db.update_sync_status' in next_line:
            new_lines.append('                            db.update_sync_status(acc.get(\'username\'), "")\n')
            new_lines.append('                            db.update_account_status(acc.get(\'username\'), is_suspended=False)\n')
            i += 2
            continue

    # 5. 凍結一覧 bulk clear
    elif 'key="frozen_clr"' in line:
        new_lines.append(line)
        next_line = lines[i+1]
        if 'db.bulk_clear_sync_status' in next_line:
            new_lines.append('            for _, row in df_display.iterrows():\n')
            new_lines.append('                uname = row[\'username\']\n')
            new_lines.append('                db.update_sync_status(uname, "")\n')
            new_lines.append('                db.update_account_status(uname, is_suspended=False)\n')
            i += 2
            continue

    # 6. 実行失敗一覧 bulk clear
    elif 'key="fail_clr"' in line:
        new_lines.append(line)
        next_line = lines[i+1]
        if 'db.bulk_clear_sync_status' in next_line:
            new_lines.append('            for _, row in df_display.iterrows():\n')
            new_lines.append('                uname = row[\'username\']\n')
            new_lines.append('                db.update_sync_status(uname, "")\n')
            new_lines.append('                db.update_account_status(uname, is_suspended=False)\n')
            i += 2
            continue

    # 7. ログイン失敗一覧 bulk clear
    elif 'key="login_fail_clr"' in line:
        new_lines.append(line)
        next_line = lines[i+1]
        if 'db.bulk_clear_sync_status' in next_line:
            new_lines.append('            for _, row in df_display.iterrows():\n')
            new_lines.append('                uname = row[\'username\']\n')
            new_lines.append('                db.update_sync_status(uname, "")\n')
            new_lines.append('                db.update_account_status(uname, is_suspended=False)\n')
            i += 2
            continue

    # 8. ロック一覧 bulk clear
    elif 'key="lock_clr"' in line:
        new_lines.append(line)
        next_line = lines[i+1]
        if 'db.bulk_clear_sync_status' in next_line:
            new_lines.append('            for _, row in df_display.iterrows():\n')
            new_lines.append('                uname = row[\'username\']\n')
            new_lines.append('                db.update_sync_status(uname, "")\n')
            new_lines.append('                db.update_account_status(uname, is_suspended=False)\n')
            i += 2
            continue

    new_lines.append(line)
    i += 1

with open('app.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("Patch applied successfully in UTF-8!")
