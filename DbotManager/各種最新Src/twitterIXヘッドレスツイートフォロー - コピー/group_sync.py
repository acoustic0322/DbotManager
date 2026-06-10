import os
import sys
import pandas as pd
from loguru import logger

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.ixbrowser.ixbrowser_controller import IXBrowserController
from modules.mutual_follow.db_manager import DBManager

def import_accounts_from_group(selected_group=None):
    logger.info("Connecting to IXBrowser...")
    ix = IXBrowserController()
    
    if not selected_group:
        # 1. Fetch Groups
        try:
            all_groups = ix.get_all_groups()
            if not all_groups:
                logger.error("No groups found or failed to connect to IXBrowser.")
                return
            
            # 除外するグループIDのリスト
            target_excluded_ids = [
                283682, 274711, 261161, 274048, 260964, 
                255449, 253113, 277506, 248214
            ]
            groups = [
                g for g in all_groups 
                if "販売サイト用" not in str(g.get('title', '')) 
                and g['id'] not in target_excluded_ids
            ]
        except Exception as e:
            logger.error(f"Failed to fetch groups: {e}")
            return

        print("\n--- IXBrowser Groups ---")
        for i, g in enumerate(groups):
            print(f"{i}: {g['title']} (ID: {g['id']})")
        
        try:
            choice = int(input("\nImportしたいグループの番号を入力してください: "))
            if choice < 0 or choice >= len(groups):
                print("無効な選択です。")
                return
            selected_group = groups[choice]
        except (ValueError, IndexError):
            print("無効な入力です。")
            return

    # 2. Fetch Profiles from Group
    logger.info(f"Fetching profiles from group: {selected_group['title']}...")
    profiles = ix.get_all_accounts(group_id=selected_group['id'])
    
    if not profiles:
        logger.warning(f"Group '{selected_group['title']}' にはプロファイルがありません。")
        return

    logger.success(f"{len(profiles)} 件のプロファイルを取得しました。")

    # 3. Load DB
    db = DBManager()
    try:
        df_existing = db.get_all_accounts_df()
        logger.info(f"既存のアカウントをDBから読み込みました ({len(df_existing)} 件)")
    except Exception as e:
        logger.error(f"DBの読み込みに失敗しました: {e}")
        df_existing = pd.DataFrame()

    # Define Columns (Matches app.py logic)
    needed_cols = [
        'screen_name', 'password', 'email', 'auth_token', 'ct0', 'totp_secret',
        'assigned_name', 'assigned_bio', 'assigned_icon', 'assigned_header',
        'is_japanese', 'profile_updated', 'initial_follow_done', 
        'last_tweet_time', 'last_tweet_content', 'is_suspended', 'Select'
    ]

    # 4. Filter, Merge and Prune
    new_accounts = []
    to_delete = []
    current_ix_names = set(p.get('screen_name') for p in profiles if p.get('screen_name'))
    existing_names = set(df_existing['screen_name'].astype(str).tolist()) if not df_existing.empty and 'screen_name' in df_existing.columns else set()

    # --- Pruning Step (Delete from DB if not in IX) ---
    if selected_group and not df_existing.empty:
        group_title = selected_group.get('title', '')
        # このグループに属しているはずのDBアカウントを抽出
        db_group_accounts = df_existing[df_existing['category'] == group_title]['screen_name'].tolist()
        
        to_delete = [name for name in db_group_accounts if name not in current_ix_names]
        if to_delete:
            logger.warning(f"Removing {len(to_delete)} accounts from DB that no longer exist in IXBrowser group '{group_title}': {to_delete}")
            # DBから直接削除
            for name in to_delete:
                db.delete_account(name)
            # 既存DFからも削除して後続の処理に合わせる
            df_existing = df_existing[~df_existing['screen_name'].isin(to_delete)]
            existing_names = set(df_existing['screen_name'].astype(str).tolist())

    for p in profiles:
        name = p.get('screen_name')
        if not name:
            continue
        
        if name in existing_names:
            # 既存垢の情報更新（必要であればここでトークンなどの上書きロジックを入れる）
            logger.debug(f"Skip: {name} (Already exists)")
            continue
            
        # Create row with defaults
        row = {col: "" for col in needed_cols}
        row.update(p) # Map IXBrowser fields
        
        # Ensure boolean defaults
        row['is_suspended'] = False
        row['profile_updated'] = False
        row['is_japanese'] = False
        row['initial_follow_done'] = False
        row['Select'] = True # Default to selected for new imports
        
        # Set category and group_name from group name
        if selected_group:
            row['category'] = selected_group.get('title', '')
            row['group_name'] = selected_group.get('title', '')
        
        new_accounts.append(row)

    if not new_accounts and not to_delete:
        logger.info("変更（追加・削除）はありませんでした。")
    else:
        if new_accounts:
            df_new = pd.DataFrame(new_accounts)
            # Ensure all needed columns are present
            for col in needed_cols:
                if col not in df_new.columns:
                    df_new[col] = ""

            df_final = pd.concat([df_existing, df_new], ignore_index=True)
            
            # Save to DB
            try:
                db.save_accounts_df(df_final)
                logger.success(f"✅ {len(new_accounts)} 件のアカウントをDBに追加保存しました。")
            except Exception as e:
                logger.error(f"DB保存に失敗しました: {e}")
        else:
            logger.info("削除のみ完了し、新規追加はありません。")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Import accounts from IXBrowser Group")
    parser.add_argument("name_or_id", nargs="?", help="Group Name or Group ID")
    parser.add_argument("--id", help="Explicit Group ID")
    args = parser.parse_args()

    try:
        selected_group = None
        ix = IXBrowserController()

        if args.id or args.name_or_id:
            search_val = args.id if args.id else args.name_or_id
            
            # --- Robust Search Logic ---
            try:
                groups = ix.get_all_groups()
                # 1. Try to find in the list first (for name or ID validation)
                selected_group = next((g for g in groups if str(g['id']) == str(search_val)), None)
                if not selected_group and not args.id:
                    selected_group = next((g for g in groups if g['title'] == search_val), None)
            except Exception:
                # If get_all_groups fails, we just ignore and continue to direct ID attempt
                pass
            
            # 2. If ID is provided but not found in list, we TRUST the ID and try directly
            if not selected_group and str(search_val).isdigit():
                logger.info(f"Group '{search_val}' was not found in listing, but attempting direct fetch by ID...")
                selected_group = {'id': search_val, 'title': f"ID:{search_val}"}

            if not selected_group:
                logger.error(f"Group with ID/Name '{search_val}' not found and does not appear to be a numeric ID.")
                sys.exit(1)

        import_accounts_from_group(selected_group=selected_group)
    except KeyboardInterrupt:
        print("\nCanceled.")
    except Exception as e:
        logger.exception(f"Fatal error: {e}")
    
    # Only wait for input if no arguments were provided (interactive mode)
    if len(sys.argv) == 1:
        input("\n終了するにはEnterを押してください...")
