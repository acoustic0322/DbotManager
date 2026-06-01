import streamlit as st
import pandas as pd
import subprocess
import os
import time
import random
import signal
import sys
import json
import asyncio
from datetime import datetime, timedelta
from modules.ai_generator import AIGenerator
from modules.profile_manager import ProfileManager
from modules.ixbrowser.ixbrowser_controller import IXBrowserController
from modules.mutual_follow.db_manager import DBManager
from androidIP自動変更.androidIP_autochange import reset_mobile_data

# Page config
st.set_page_config(
    page_title="D-BOT",
    page_icon="🤖",
    layout="wide"
)

# --- Stellar Stealth Design System ---
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');
    
    html, body, [data-testid="stapp"] {
        font-family: 'Outfit', sans-serif;
    }

    /* Main Container */
    .main {
        background: #0e1117;
    }

    /* Sidebar Styling */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #141721 0%, #0e1117 100%) !important;
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    /* Sidebar Labels & Radio Text */
    [data-testid="stSidebar"] .stMarkdown p,
    [data-testid="stSidebar"] .stMarkdown h1,
    [data-testid="stSidebar"] .stMarkdown h2,
    [data-testid="stSidebar"] .stMarkdown h3,
    [data-testid="stSidebar"] label,
    [data-testid="stSidebar"] .st-ae,
    [data-testid="stSidebar"] span {
        color: #ffffff !important;
        font-weight: 500;
    }
    
    /* Radio Button labels specifically */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p,
    [data-testid="stSidebar"] div[role="radiogroup"] label div {
        color: #ffffff !important;
        font-size: 1.05rem !important;
        font-weight: 500 !important;
    }

    /* Selectbox Text to Black for readability in fields */
    div[data-baseweb="select"] div {
        color: #000000 !important;
    }

    /* Card Layout (Borderless) */
    .stellar-card {
        background: transparent;
        padding: 0.5rem 0;
        border-radius: 0;
        border: none;
        margin-bottom: 20px;
        box-shadow: none;
    }

    /* Gold Line Divider (Minimalist & Elegant) */
    .gold-line {
        height: 1px;
        width: 500px; /* Extended to 500px */
        background: #D4AF37; /* Sophisticated Champagne Gold */
        margin: 0.3rem 0 1.5rem 0;
        box-shadow: 0 1px 4px rgba(212, 175, 55, 0.3);
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: #ffffff !important;
        border: none;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(168, 85, 247, 0.4);
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 20px;
    }
    .stTabs [data-baseweb="tab"] {
        background-color: transparent !important;
        font-weight: 600;
        color: #888;
    }
    .stTabs [data-baseweb="tab"][aria-selected="true"] {
        color: #fff;
        border-bottom-color: #a855f7 !important;
    }

    /* Glowing Icons or Titles */
    .glow-text {
        color: #fff;
        text-shadow: 0 0 10px rgba(168, 85, 247, 0.5);
        white-space: nowrap !important;
    }

    /* Account Visual Card */
    .account-visual-card {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(212, 175, 55, 0.2);
        border-radius: 12px;
        padding: 1rem;
        text-align: center;
        transition: all 0.3s ease;
        position: relative;
        margin-bottom: 15px;
    }
    .account-visual-card:hover {
        transform: translateY(-5px);
        border-color: rgba(212, 175, 55, 0.8);
        box-shadow: 0 5px 15px rgba(212, 175, 55, 0.2);
    }
    .status-dot {
        height: 10px;
        width: 10px;
        border-radius: 50%;
        display: inline-block;
        margin-right: 5px;
    }
    .status-active { background-color: #00ff00; box-shadow: 0 0 5px #00ff00; }
    .status-suspended { background-color: #ff0000; box-shadow: 0 0 5px #ff0000; }

    /* --- Universal Sizing Up --- */
    h1 { font-size: 3.5rem !important; }
    h2 { font-size: 2.8rem !important; }
    h3 { font-size: 2.2rem !important; }
    
    /* Input Fields */
    .stTextInput input, .stNumberInput input, .stSelectbox div[data-baseweb="select"] {
        font-size: 1.25rem !important;
        height: 3.5rem !important;
    }
    
    /* Sidebar Menu */
    [data-testid="stSidebar"] [data-testid="stWidgetLabel"] p {
        font-size: 1.4rem !important;
        white-space: nowrap !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        white-space: nowrap !important;
        flex-wrap: nowrap !important;
    }
    [data-testid="stSidebar"] div[role="radiogroup"] label div {
        font-size: 1.3rem !important;
        padding: 5px 0 !important;
        white-space: nowrap !important;
    }

    /* Buttons */
    .stButton > button {
        font-size: 1.2rem !important;
        padding: 0.8rem 2rem !important;
        border-radius: 12px !important;
    }

    /* Checkbox Label sizing */
    .stCheckbox label p {
        font-size: 1.1rem !important;
    }

    /* Sidebar Menu - Clean alignment */
    [data-testid="stSidebar"] div[role="radiogroup"] label {
        display: flex !important;
        flex-wrap: nowrap !important;
        align-items: center !important;
        padding: 10px 15px !important;
        margin: 4px 0 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        white-space: nowrap !important;
    }

    /* Super Gold Menu Styling for Selected Item */
    [data-testid="stSidebar"] [data-testid="stRadio"] div[role="radiogroup"] label[aria-checked="true"] {
        background: rgba(212, 175, 55, 0.15) !important;
        border: 1px solid rgba(212, 175, 55, 0.3) !important;
        color: #D4AF37 !important;
        box-shadow: 0 0 10px rgba(212, 175, 55, 0.1);
    }
    
    [data-testid="stSidebar"] div[role="radiogroup"] label p {
        white-space: nowrap !important;
        overflow: visible !important;
        font-size: 1.1rem !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] p {
        color: #D4AF37 !important;
        font-weight: 600 !important;
        font-size: 1.15rem !important; /* Slightly larger for emphasis but still no-wrap */
        white-space: nowrap !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] div[role="presentation"] div {
        border-color: #D4AF37 !important;
        background-color: #D4AF37 !important;
    }
    
    [data-testid="stSidebar"] div[role="radiogroup"] label[aria-checked="true"] div[role="presentation"] div > div {
        background-color: #fff !important;
    }

    [data-testid="stSidebar"] div[role="radiogroup"] label:hover {
        background: rgba(212, 175, 55, 0.1) !important;
    }
    
    [data-testid="stSidebar"] div[role="radiogroup"] label div[data-testid="stMarkdownContainer"] {
        padding-left: 10px !important;
        white-space: nowrap !important;
    }
    </style>
""", unsafe_allow_html=True)

# Constants
HISTORY_FILE = 'data/profile_history.csv'
LOG_FILE = 'bot.log'
PID_FILE = 'bot.pid'
import socket
def get_worker_pid_file():
    hostname = socket.gethostname()
    pc_id = hostname
    try:
        if os.path.exists('config.json'):
            import json
            with open('config.json', 'r', encoding='utf-8') as f:
                pc_map = json.load(f).get('PC_MAP', {})
                if hostname in pc_map:
                    pc_id = pc_map[hostname]
    except: pass
    return f"worker_{pc_id}.pid"

WORKER_PID_FILE = get_worker_pid_file()
SETTINGS_FILE = 'data/settings.json'
LOGIN_INFO_CSV = 'data/account_registry.csv'

# --- Utils ---
@st.cache_resource
def get_db():
    from modules.mutual_follow.db_manager import DBManager
    return DBManager()

@st.cache_data(ttl=60)
def load_accounts(group_id=None):
    db = get_db()
    return db.get_all_accounts_df()

def clear_account_cache():
    if 'cached_df_all' in st.session_state:
        del st.session_state.cached_df_all
    st.cache_data.clear()

def save_accounts(df):
    db = get_db()
    db.save_accounts_df(df)
    st.cache_data.clear() # Clear cache on save

def perform_delete_account(username):
    db = get_db()
    db.delete_account(username)
    clear_account_cache()
    return True

def perform_profile_reset(profile_id, username):
    from modules.ixbrowser.ixbrowser_controller import IXBrowserController
    controller = IXBrowserController()
    db = get_db()
    
    new_pid = controller.full_profile_reset(profile_id, username)
    if new_pid:
        db.update_profile_id(username, new_pid)
        clear_account_cache()
        return True
    return False

def load_settings():
    import json
    if os.path.exists(SETTINGS_FILE):
        with open(SETTINGS_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_settings(settings):
    import json
    with open(SETTINGS_FILE, 'w', encoding='utf-8') as f:
        json.dump(settings, f, ensure_ascii=False, indent=4)

@st.cache_data(ttl=3600)
def get_base64_image(image_path):
    import base64
    if os.path.exists(image_path):
        try:
            with open(image_path, "rb") as f:
                return base64.b64encode(f.read()).decode()
        except:
            pass
    return None

def trigger_single_icon_download(screen_name):
    import subprocess
    cmd = [sys.executable, 'asset_sync.py', '--single', screen_name]
    subprocess.Popen(cmd, creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0)

def trigger_account_check(usernames):
    if not usernames: return
    import subprocess
    if isinstance(usernames, str): usernames = [usernames]
    user_str = ",".join(usernames)
    cmd = [sys.executable, 'check_full_status.py', '--usernames', user_str]
    # Run in background console for visibility if possible, or hidden
    subprocess.Popen(['cmd', '/c', 'start'] + cmd if sys.platform == 'win32' else cmd, shell=True)

def render_editing_overlay(accounts):
    # --- [NEW] Individual Card Edit Form Overlay ---
    if "editing_account" in st.session_state and st.session_state.editing_account:
        editing_name = st.session_state.editing_account
        editing_data = accounts[accounts['screen_name'] == editing_name]
        
        if not editing_data.empty:
            acc_data = editing_data.iloc[0].to_dict()
            with st.container(border=True):
                st.markdown(f"#### 📝 アカウント情報の編集: @{editing_name}")
                
                # [NEW] ID & Display Name Editing
                col_n1, col_n2 = st.columns(2)
                new_screen_name = col_n1.text_input("ユーザーID (@handle)", value=str(acc_data.get('screen_name', '')), key=f"edit_handle_{editing_name}")
                new_display_name = col_n2.text_input("表示名", value=str(acc_data.get('assigned_name', '')), key=f"edit_name_{editing_name}")

                col_e1, col_e2, col_e3 = st.columns(3)
                new_pw = col_e1.text_input("パスワード", value=str(acc_data.get('password', '')), key=f"edit_pw_{editing_name}")
                new_totp = col_e2.text_input("2FA (TOTP) Key", value=str(acc_data.get('totp_secret', '')), key=f"edit_totp_{editing_name}")
                new_email = col_e3.text_input("メールアドレス", value=str(acc_data.get('email', '')), key=f"edit_email_{editing_name}")
                
                col_e4, col_e5, col_e6 = st.columns(3)
                new_auth = col_e4.text_input("auth_token", value=str(acc_data.get('auth_token', '')), key=f"edit_auth_{editing_name}")
                new_ct0 = col_e5.text_input("ct0", value=str(acc_data.get('ct0', '')), key=f"edit_ct0_{editing_name}")
                
                # Category Dropdown
                # Category Dropdown
                # Fetch current IX groups to add them to category options
                try:
                    ix_tmp = IXBrowserController()
                    ix_all_groups = ix_tmp.get_all_groups()
                    ix_group_names = [g['title'] for g in ix_all_groups if g['id'] is not None and g['title'] != 'すべて']
                except:
                    ix_group_names = []

                base_categories = ["日常生活", "ゲーム", "投資", "美容", "子育て", "アイドル", "エンジニア", "アニメ", "料理", "web2", "web用", "非公式用", "その他"]
                category_list = sorted(list(set(base_categories + ix_group_names)))
                
                current_cat = acc_data.get('category', '日常生活')
                if current_cat and current_cat not in category_list: category_list.append(current_cat)
                new_category = col_e6.selectbox("カテゴリー (AI判定のベース)", category_list, index=category_list.index(current_cat) if current_cat in category_list else 0, key=f"edit_cat_{editing_name}")
                
                # IX Group Selection
                ix_group_options = ["指定なし"] + [g['title'] for g in ix_all_groups if g['id'] is not None and g['title'] != 'すべて']
                ix_group_map = {g['title']: g['id'] for g in ix_all_groups if g['id'] is not None}
                
                current_group_id = str(acc_data.get('group_id', ''))
                current_group_name = "指定なし"
                for g in ix_all_groups:
                    if str(g['id']) == current_group_id:
                        current_group_name = g['title']
                        break
                
                if current_group_name not in ix_group_options:
                    ix_group_options.append(current_group_name)
                    
                col_g1, col_g2 = st.columns(2)
                new_group_name = col_g1.selectbox("IXBrowserグループ", ix_group_options, index=ix_group_options.index(current_group_name), key=f"edit_group_{editing_name}")
                new_group_id = ix_group_map.get(new_group_name) if new_group_name != "指定なし" else ""

                col_eb1, col_eb2 = st.columns([1, 4])
                if col_eb1.button("💾 変更を保存", type="primary", use_container_width=True):
                    idx = accounts[accounts['screen_name'] == editing_name].index[0]
                    clean_new_name = new_screen_name.replace('@', '').strip()
                    
                    # Update IXBrowser Profile Group if changed
                    if str(new_group_id) != str(current_group_id):
                        try:
                            from modules.ixbrowser.ixbrowser_local_api import Profile
                            p_id = acc_data.get('profile_id')
                            if p_id:
                                ix_client = IXBrowserController().client
                                p_obj = Profile(profile_id=p_id, name=clean_new_name, group_id=new_group_id)
                                ix_client.update_profile(p_obj)
                        except Exception as ix_err:
                            st.warning(f"IXBrowser同期失敗: {ix_err}")

                    # DBに直接保存
                    db = DBManager()
                    conn = db.get_connection()
                    cursor = conn.cursor()
                    p = db._placeholder()
                    try:
                        cursor.execute(f'''
                            UPDATE accounts 
                            SET username={p}, auth_token={p}, ct0={p}, password={p}, totp_secret={p}, email={p}, display_name={p}, category={p}, group_id={p}, group_name={p}
                            WHERE username={p}
                        ''', (clean_new_name, new_auth, new_ct0, new_pw, new_totp, new_email, new_display_name, new_category, str(new_group_id or ""), str(new_group_name if new_group_name != "指定なし" else ""), editing_name))
                        if db.db_type not in ["mysql", "postgres"]: conn.commit()
                        st.success(f"@{clean_new_name} の情報を更新しました。")
                    except Exception as e:
                        st.error(f"保存エラー: {e}")
                    finally:
                        pass
                    
                    # 重要: キャッシュをクリアして即時反映させる
                    st.cache_data.clear()
                    st.session_state.editing_account = None
                    time.sleep(1)
                    st.rerun()
                
                if col_eb2.button("キャンセル", key="cancel_edit_top"):
                    st.session_state.editing_account = None
                    st.rerun()
                st.markdown("---")

def get_bot_process():
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                return pid
            except OSError:
                os.remove(PID_FILE)
                return None
        except ValueError:
            return None
    return None

def start_bot():
    if get_bot_process():
        st.warning("ボットは既に稼働しています！")
        return
    process = subprocess.Popen(
        [sys.executable, 'account_manager.py'],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )
    with open(PID_FILE, 'w') as f:
        f.write(str(process.pid))
    st.success(f"ボットを起動しました。PID: {process.pid}")
    time.sleep(1)
    st.rerun()

def stop_bot():
    pid = get_bot_process()
    if pid:
        try:
            if sys.platform == 'win32':
                # Forced kill for Windows console processes
                subprocess.run(['taskkill', '/F', '/PID', str(pid), '/T'], capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
            st.success("停止シグナルを送信しました。")
        except Exception as e:
            st.error(f"停止中にエラーが発生しました: {e}")
        if os.path.exists(PID_FILE):
            os.remove(PID_FILE)
        time.sleep(1)
        st.rerun()

def get_worker_process():
    if os.path.exists(WORKER_PID_FILE):
        try:
            with open(WORKER_PID_FILE, 'r') as f:
                pid = int(f.read().strip())
            try:
                os.kill(pid, 0)
                return pid
            except OSError:
                if os.path.exists(WORKER_PID_FILE): os.remove(WORKER_PID_FILE)
                return None
        except:
            return None
    return None

def start_worker():
    if get_worker_process(): return
    process = subprocess.Popen(
        [sys.executable, 'worker_service.py'],
        creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
    )
    with open(WORKER_PID_FILE, 'w') as f:
        f.write(str(process.pid))

def stop_worker():
    pid = get_worker_process()
    if pid:
        try:
            if sys.platform == 'win32':
                subprocess.run(['taskkill', '/F', '/PID', str(pid), '/T'], capture_output=True)
            else:
                os.kill(pid, signal.SIGTERM)
        except: pass
        if os.path.exists(WORKER_PID_FILE): os.remove(WORKER_PID_FILE)

def read_logs():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            return f.readlines()
    return []

# --- Sidebar & Navigation ---
with st.sidebar:
    st.markdown("<h1 class='glow-text' style='text-align: center; font-size: 2.2rem; letter-spacing: 2px;'>D-BOT</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; color: #888; font-size: 0.8rem; margin-top: -15px;'>System v2.1.1 Stable</p>", unsafe_allow_html=True)
    
    if 'page' not in st.session_state:
        st.session_state.page = "選手権"

    # Custom CSS for Navigation Buttons
    st.markdown("""
        <style>
        .nav-button {
            display: flex;
            align-items: center;
            padding: 10px 15px;
            margin: 5px 0;
            border-radius: 10px;
            cursor: pointer;
            transition: all 0.3s;
            border: 1px solid transparent;
            font-weight: 500;
        }
        .nav-active {
            background: rgba(212, 175, 55, 0.15) !important;
            border-color: #D4AF37 !important;
            color: #D4AF37 !important;
        }
        </style>
    """, unsafe_allow_html=True)

    if 'page' not in st.session_state:
        st.session_state.page = "選手権"

    def nav_item(label, icon, key_suffix):
        is_active = st.session_state.page == label
        # Use columns to simulate button style if needed, but simple button is safer for rerun
        if st.button(f"{icon} {label}", key=f"nav_{key_suffix}", use_container_width=True, type="secondary" if not is_active else "primary"):
            st.session_state.page = label
            st.rerun()

    nav_item("選手権", "🏆", "cup")
    
    # Account Management Item
    nav_item("アカウント管理", "👥", "mgmt")
    
    if st.session_state.page == "アカウント管理":
        # Initialize with default to prevent blank display
        group_options = ["すべて"]
        
        try:
            # Use st.cache_data for IX group fetching
            @st.cache_data(ttl=600)
            def fetch_ix_groups():
                return IXBrowserController().get_all_groups()

            all_groups = fetch_ix_groups()
            if all_groups:
                target_excluded_ids = [283682, 274711, 261161, 274048, 260964, 255449, 253113, 277506, 248214]
                fetched_groups = [
                    g['title'] for g in all_groups 
                    if g['id'] is not None 
                    and "販売" not in str(g.get('title', ''))
                    and "サイト用" not in str(g.get('title', ''))
                    and "リンク渡す" not in str(g.get('title', ''))
                    and g['id'] not in target_excluded_ids
                    and str(g.get('title', '')).strip() != ""
                ]
                group_options = ["すべて"] + fetched_groups
            
            # Safe index determination
            current_sel = st.session_state.get('selected_group_filter', "すべて")
            try:
                sel_idx = group_options.index(current_sel)
            except (ValueError, IndexError):
                sel_idx = 0
            
            selected_group_sidebar = st.sidebar.selectbox(
                "📁 グループ選択", 
                options=group_options, 
                index=sel_idx,
                key="sidebar_group_selector",
                help="表示するアカウントのグループを選択してください"
            )
            st.session_state.selected_group_filter = selected_group_sidebar
        except Exception as e:
            # Fallback to "すべて" if everything fails
            st.session_state.selected_group_filter = "すべて"
            st.sidebar.selectbox("📁 グループ選択", options=["すべて"], index=0, disabled=True)
            st.sidebar.caption(f"⚠️ グループ情報を取得できませんでした")
    else:
        st.session_state.selected_group_filter = "すべて"
    
    nav_item("アカウント追加", "➕", "add")
    nav_item("ログイン失敗", "⚠️", "fail")
    nav_item("実行失敗", "❌", "exec_fail")
    nav_item("ロック", "🔒", "lock")
    nav_item("凍結", "❄️", "frozen")
    nav_item("凍結チェック用", "🔍", "frozen_check")
    nav_item("システム設定", "⚙️", "settings")

    page = st.session_state.page

    # --- Auto-start Worker Service ---
    # DISABLED: Auto-starting was causing infinite worker spawning due to Windows PID check failures.
    # Workers should be started manually via FORCE_RESET.bat or worker_service.py directly.
    if get_worker_process():
        st.sidebar.success("🟢 Worker Online")
    else:
        st.sidebar.warning("🟡 Worker Offline (Run FORCE_RESET.bat)")

    # --- Real-time Task Monitor in Sidebar ---
    PROGRESS_FILE = 'data/task_progress.json'
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, 'r', encoding='utf-8') as f:
                p_data = json.load(f)
            
            # 5分以内の更新があれば表示
            if time.time() - p_data.get('timestamp', 0) < 300:
                st.sidebar.markdown("---")
                st.sidebar.subheader("📊 実行モニター")
                total = p_data.get('total', 1)
                success = p_data.get('success', 0)
                fail = p_data.get('fail', 0)
                processed = success + fail
                
                percent = min(100, int((processed / total) * 100))
                st.sidebar.progress(percent / 100)
                st.sidebar.write(f"進捗: {percent}% ({processed}/{total})")
                st.sidebar.write(f"✅ 成功: {success} | ❌ 失敗: {fail}")
                
                if p_data.get('status'):
                    st.sidebar.info(f"状態: {p_data['status']}")
        except: pass

    # Internally ensure base path is loaded but hide UI
    version_paths = {
        "Main Account Registry": "data/account_registry.csv",
        "IXBrowser API Direct": "ixbrowser_api"
    }
    current_settings = load_settings()
    # Force primary if not set
    if 'active_csv_path' not in current_settings:
        current_settings['active_csv_path'] = version_paths["Main Account Registry"]
        save_settings(current_settings)
    
    selected_group_id = None

# --- Progress Monitor Component ---
def render_progress_monitor():
    if os.path.exists('data/task_progress.json'):
        try:
            with open('data/task_progress.json', 'r', encoding='utf-8') as f:
                progress = json.load(f)
            
            total = progress.get('total', 0)
            success = progress.get('success', 0)
            fail = progress.get('fail', 0)
            status_text = progress.get('status', '実行中')
            
            percent = int((success + fail) / total * 100) if total > 0 else 0
            
            # Neon Dashboard UI (iframe version for maximum stability)
            import streamlit.components.v1 as components
            dashboard_html = f"""
            <div style="background: #0e1117; color: #fff; font-family: sans-serif; border: 1px solid rgba(212, 175, 55, 0.3); border-radius: 15px; padding: 20px; box-shadow: 0 4px 15px rgba(0,0,0,0.5);">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
                    <div style="color: #D4AF37; font-size: 0.9rem; font-weight: 600; letter-spacing: 1px;">⚡ BOT MONITOR: <span style="color: #fff;">{status_text}</span></div>
                    <div style="color: #888; font-size: 0.8rem;">{percent}% DONE</div>
                </div>
                <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-bottom: 20px;">
                    <div style="background: rgba(255,255,255,0.03); border-radius: 10px; padding: 15px; text-align: center; border: 1px solid rgba(255,255,255,0.05);">
                        <div style="color: #D4AF37; font-size: 0.75rem; margin-bottom: 3px;">📊 実行予定</div>
                        <div style="font-size: 1.5rem; font-weight: 800;">{total}</div>
                    </div>
                    <div style="background: rgba(74, 222, 128, 0.05); border-radius: 10px; padding: 15px; text-align: center; border: 1px solid rgba(74, 222, 128, 0.1);">
                        <div style="color: #4ade80; font-size: 0.75rem; margin-bottom: 3px;">✅ 成功</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #4ade80;">{success}</div>
                    </div>
                    <div style="background: rgba(248, 113, 113, 0.05); border-radius: 10px; padding: 15px; text-align: center; border: 1px solid rgba(248, 113, 113, 0.1);">
                        <div style="color: #f87171; font-size: 0.75rem; margin-bottom: 3px;">❌ 失敗</div>
                        <div style="font-size: 1.5rem; font-weight: 800; color: #f87171;">{fail}</div>
                    </div>
                </div>
                <div style="width: 100%; height: 6px; background: rgba(255,255,255,0.05); border-radius: 10px; overflow: hidden;">
                    <div style="width: {percent}%; height: 100%; background: linear-gradient(90deg, #D4AF37, #f3cf65);"></div>
                </div>
            </div>
            """
            components.html(dashboard_html, height=220)
            
            if st.button("🗑️ モニターを閉じる / 履歴クリア", use_container_width=True):
                if os.path.exists('data/task_progress.json'):
                    os.remove('data/task_progress.json')
                st.rerun()
        except Exception as e:
            st.sidebar.error(f"モニター描画エラー: {e}")



def render_global_control_center(ext_params=None):
    st.markdown("---")
    st.subheader("🌐 全PC一括制御 (Global Control Center)")
    col_g1, col_g2, col_g3, col_g4 = st.columns(4)
    from modules.mutual_follow.db_manager import DBManager
    db = DBManager()
    
    with col_g1:
        if st.button("🚀 全PCに同期指示 (START)", use_container_width=True, type="primary", key="global_start_comp"):
            try:
                if ext_params:
                    params = ext_params
                else:
                    params = {
                        "tweet_count": st.session_state.get('tweet_count', 0),
                        "follow_count": st.session_state.get('follow_count', 0),
                        "rt_count": st.session_state.get('rt_count', 0),
                        "reply_count": st.session_state.get('reply_count', 0),
                        "tweet_image": st.session_state.get('use_tweet_image', False),
                        "visible": st.session_state.get('use_visible', False),
                        "sync_sheets": False
                    }
                db.reset_all_in_use()
                db.set_global_command("START_ENGAGEMENT", params)
                st.success("全PCへ開始指示を送信し、ロックを初期化しました。")
                
                st.rerun()
            except Exception as e:
                st.error(f"送信失敗: {e}")
    
    with col_g2:
        if st.button("🛑 全PC強制停止 (STOP ALL)", use_container_width=True, key="global_stop_comp"):
            try:
                db.set_global_command("STOP_ALL")
                st.warning("全PCへ停止指示を送信しました。")
            except Exception as e:
                st.error(f"送信失敗: {e}")

    with col_g3:
        if st.button("♻️ 使用中フラグをリセット", use_container_width=True, key="global_reset_inuse_comp", help="他PCで実行中と認識されてしまっているアカウントのロックを強制解除します"):
            try:
                db.reset_all_in_use()
                st.success("全アカウントの使用中フラグをリセットしました。")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                st.error(f"リセット失敗: {e}")

    with col_g4:
        if st.button("🧹 IXBrowser一括クリーンアップ", use_container_width=True, help="全PCのIXBrowser上で「Open」のまま固まっているプロファイルを強制的に解除します"):
            try:
                db.set_global_command("CLEAN_IXBROWSER")
                st.success("全PCへIXBrowserクリーンアップ指示を送信しました。")
            except Exception as e:
                st.error(f"送信失敗: {e}")

# --- Account Selector Component ---
def render_account_selector(key_prefix, accounts_df=None):
    global selected_group_id
    def toggle_selection(username, current_val, key):
        from modules.mutual_follow.db_manager import DBManager
        db = DBManager()
        db.update_account_selection(username, not current_val)
        clear_account_cache()
    if accounts_df is not None:
        accounts = accounts_df
    else:
        accounts = load_accounts(group_id=selected_group_id if selected_group_id else None)
    
    if accounts.empty:
        st.warning("アカウントがありません。")
        return pd.DataFrame()

    # Fetch today's stats for display
    @st.cache_data(ttl=60)
    def fetch_daily_stats():
        db = DBManager()
        return db.get_daily_stats()
    
    stats_list = fetch_daily_stats()
    stats_dict = {}
    for s in stats_list:
        uname = s['username']
        if uname not in stats_dict: stats_dict[uname] = {}
        stats_dict[uname][s['action_type']] = s['count']

    # Layout for selector buttons & Search
    col_btn1, col_btn2, col_btn3, col_search = st.columns([1, 1, 1, 3])
    
    def update_all_selection(new_status):
        from modules.mutual_follow.db_manager import DBManager
        db = DBManager()
        # Use high-performance bulk update
        db.update_all_selection_status(new_status, screen_names=accounts['screen_name'].tolist())
        clear_account_cache()
        
        # Batch update session state to avoid multiple reruns
        for idx, row in accounts.iterrows():
            name = row['screen_name']
            key = f"sel_{key_prefix}_{name}_{idx}"
            if key in st.session_state:
                st.session_state[key] = new_status
        st.rerun()

    if col_btn1.button("✅ 全て選択", key=f"{key_prefix}_btn_all", use_container_width=True):
        update_all_selection(True)
    if col_btn2.button("🚫 全て解除", key=f"{key_prefix}_btn_none", use_container_width=True):
        update_all_selection(False)
    if col_btn3.button("⏳ 未完了のみ", key=f"{key_prefix}_btn_incomplete", use_container_width=True):
        # Special logic for incomplete (profile_updated is false/null)
        target_indices = accounts[~accounts['profile_updated'].fillna(False).astype(bool)].index
        accounts['Select'] = False
        accounts.loc[target_indices, 'Select'] = True
        save_accounts(accounts)
        st.rerun()
    
    search_term = col_search.text_input("🔍 アカウント検索", placeholder="IDで絞り込み...", key=f"{key_prefix}_search_input")

    # Visual Grid Selector
    st.markdown("### アカウント一覧")
    
    # Filter by search term
    if search_term:
        display_accounts = accounts[accounts['screen_name'].str.contains(search_term, case=False, na=False)]
    else:
        display_accounts = accounts
    
    # Sort by ID (screen_name) alphabetically
    if not display_accounts.empty:
        display_accounts = display_accounts.sort_values(by='screen_name', key=lambda x: x.str.lower())

    selected_count = len(accounts[accounts['Select'] == True])
    st.markdown(f"<div style='background: rgba(212, 175, 55, 0.1); padding: 5px 15px; border-radius: 20px; display: inline-block; border: 1px solid rgba(212, 175, 55, 0.3); margin-bottom: 15px;'>🚩 現在の選抜数: <b>{selected_count}</b> / {len(accounts)}</div>", unsafe_allow_html=True)

    # Use centralized overlay
    render_editing_overlay(accounts)

    # Pagination settings
    PAGE_SIZE = 24
    total_accounts = len(display_accounts)
    num_pages = (total_accounts + PAGE_SIZE - 1) // PAGE_SIZE
    
    if num_pages > 1:
        st.markdown("---")
        col_p1, col_p2, col_p3 = st.columns([1, 2, 1])
        page_num = col_p2.number_input("ページ選択", min_value=1, max_value=num_pages, value=1, key=f"{key_prefix}_page_nav")
        st.markdown(f"<p style='text-align: center; color: #888;'>Page {page_num} of {num_pages}</p>", unsafe_allow_html=True)
        
        start_idx = (page_num - 1) * PAGE_SIZE
        end_idx = start_idx + PAGE_SIZE
        paged_accounts = display_accounts.iloc[start_idx:end_idx]
    else:
        paged_accounts = display_accounts

    cols_per_row = 4 # Reduced from 6 to make items bigger
    account_list = paged_accounts.to_dict('records')
    for i in range(0, len(account_list), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            if i + j < len(account_list):
                acc = account_list[i + j]
                name = acc.get('screen_name', 'Unknown')
                
                # Stats display
                us = stats_dict.get(name, {})
                l_cnt = us.get('like', 0)
                b_cnt = us.get('bookmark', 0)
                r_cnt = us.get('rt', 0)
                p_cnt = us.get('reply', 0)
                f_cnt = us.get('follow', 0)
                t_cnt = us.get('tweet', 0)
                
                # Check for local icon
                icon_path = os.path.join('data/icons', f"{name}.jpg")
                b64_icon = get_base64_image(icon_path)
                icon_html = f'<img src="data:image/jpeg;base64,{b64_icon}" style="width: 75px; height: 75px; border-radius: 50%; border: 2px solid #D4AF37; object-fit: cover;">' if b64_icon else '<div style="font-size: 3rem;">👤</div>'
                
                # [UPDATED] Show sync status with distinct colors for Running, Finished, and Failed
                sync_status = str(acc.get('sync_status', '')).strip()
                status_color = "#D4AF37" # Default Gold
                display_status = sync_status
                
                if not sync_status:
                    status_html = ""
                else:
                    if "実行中" in sync_status:
                        status_color = "#3498db" # Blue
                    elif "失敗" in sync_status or "エラー" in sync_status:
                        status_color = "#e74c3c" # Red
                    elif "完了" in sync_status or "終了" in sync_status or "Success" in sync_status:
                        status_color = "#2ecc71" # Green
                    
                    status_html = f'<div style="font-size: 0.85rem; color: {status_color}; font-weight: 700; margin-bottom: 2px; text-shadow: 0 0 5px {status_color}44;">● {sync_status}</div>'
                
                # Category Badge
                cat_val = acc.get('category', '日常生活')
                cat_html = f'<div style="display: inline-block; background: rgba(168, 85, 247, 0.15); border: 1px solid rgba(168, 85, 247, 0.3); color: #a855f7; font-size: 0.75rem; padding: 1px 8px; border-radius: 10px; margin-bottom: 5px;">{cat_val}</div>'

                with cols[j]:
                    # Improved Card Layout: Name (Gold) -> @ID (Gold)
                    display_name = acc.get("assigned_name", "") or name
                    card_html = (
                        f'<div style="text-align: center; margin-bottom: 8px;">'
                        f'<a href="https://x.com/{name}" target="_blank">{icon_html}</a>'
                        f'<div style="font-size: 1.1rem; color: #D4AF37; font-weight: 900; margin-top: 8px; overflow: hidden; text-overflow: ellipsis; white-space: nowrap;">'
                        f'{display_name}'
                        f'</div>'
                        f'<div style="font-size: 0.9rem; margin-bottom: 6px;">'
                        f'<a href="https://x.com/{name}" target="_blank" style="color: #000000; text-decoration: none; font-weight: 600;">@{name}</a>'
                        f'</div>'
                        f'{cat_html}'
                        f'{status_html}'
                        f'<div style="font-size: 0.75rem; color: #888; margin-bottom: 3px;">🕐 {acc.get("last_tweet_at", "未投稿")}</div>'
                        f'<div style="display: flex; flex-wrap: wrap; justify-content: center; gap: 5px 10px; font-size: 0.8rem; color: #fff; background: rgba(0,0,0,0.3); padding: 5px 10px; border-radius: 12px; border: 1px solid rgba(212, 175, 55, 0.3); margin-top: 5px;">'
                        f'<span title="いいね">❤️{l_cnt}</span><span title="ブックマーク">📚{b_cnt}</span><span title="リツイート">🔄{r_cnt}</span><span title="リプライ">💬{p_cnt}</span><span title="フォロー">➕{f_cnt}</span><span title="ツイート">🐦{t_cnt}</span>'
                        f'</div></div>'
                    )
                    st.markdown(card_html, unsafe_allow_html=True)
                    idx_in_full = display_accounts.index[i + j] # Use original DF index
                    acc_key = f"sel_{key_prefix}_{name}_{idx_in_full}"
                    new_val = st.checkbox("✔ 選択", value=acc.get('Select', False), key=acc_key)
                        
                    if new_val != acc.get('Select', False):
                        accounts.at[idx_in_full, 'Select'] = new_val
                        db = DBManager()
                        db.update_account_selection(name, new_val)

    if num_pages > 1:
        st.markdown(f"<p style='text-align: center; color: #888;'>Page {page_num} of {num_pages}</p>", unsafe_allow_html=True)

    return accounts[accounts['Select'] == True]


# =============================================================================
# Pages
# =============================================================================

# [GLOBAL] Show progress monitor on all pages at the very top of the main area
render_progress_monitor()

if page == "選手権":
    st.markdown("<h2 class='glow-text' style='margin-bottom: 0;'>選手権</h2><div class='gold-line' style='margin-top: 0;'></div>", unsafe_allow_html=True)

    st.markdown('<div class="stellar-card" style="padding-top: 0;">', unsafe_allow_html=True)
    
    # 1. Main Action Panel
    st.markdown("### 設定")
    col_t1, col_t2 = st.columns(2)
    target_handle = col_t1.text_input("応援対象のユーザーID (@ID)", placeholder="jack", help="@を除いたスクリーンネームを入れると、その人のプロフィールへ向かいます")
    tweet_keyword = col_t2.text_input("検索キーワード / ツイート冒頭", placeholder="最新ツイートの特定キーワード...", help="プロフィール内でどのツイートに応援（いいね/リプ）するかを特定します")

    # [Prominent IP Toggle]
    use_ip_rotation = st.checkbox("🔄 **IP変更（アンドロイド）を有効にする**", value=True, help="処理開始前に機内モードのON/OFFを行いIPを変更します")

    with st.expander("🛠️ 詳細パラメータ設定", expanded=True):
        col_pa1, col_pa2, col_pa3 = st.columns(3)
        like_count = col_pa1.number_input("いいね・ブクマ数", min_value=0, value=0)
        rt_count = col_pa2.number_input("リツイート数", min_value=0, value=0)
        reply_count = col_pa3.number_input("AIリプライ数", min_value=0, value=0)
        
        col_pa4, col_pa5 = st.columns(2)
        follow_count = col_pa4.number_input("新規フォロー数", min_value=0, value=0)
        tweet_count = col_pa5.number_input("新規ツイート数", min_value=0, value=0)
        
        fixed_text = st.text_input("固定ツイート/リプライ文 (空白ならAIが生成)", placeholder="応援してます！", help="入力すると、リプライや新規ツイートでこの文章が優先的に使われます")
        
        col_opt1, col_opt2, col_opt3 = st.columns(3)
        use_recreate = col_opt1.checkbox("プロファイルを強制的に再作成する", value=False, key="use_recreate", help="既存のIXBrowserプロファイルを削除して作り直します。")
        use_tweet_image = col_opt2.checkbox("ツイートにAI画像を添付する", value=False, key="use_tweet_image", help="ツイート時にAIで画像を生成して自動で添付します。")
        use_visible = col_opt3.checkbox("ブラウザを表示する (Visible)", value=False, key="use_visible", help="ヘッドレスを無効にし、ブラウザの動作を目視できるようにします。")

    # Placeholder for the button so it appears here
    button_placeholder = st.container()
    
    st.markdown('<div style="margin-bottom: 25px;"></div>', unsafe_allow_html=True)

    # 2. Member Selection (Visual Grid)
    selected_rows = render_account_selector("p6_bulk_like")

    # 3. Execution Action (Rendered into the placeholder above)
    # [MODIFIED] Execution check: If ONLY tweeting, target_handle and keyword are optional.
    # Otherwise, they are required.
    can_run = not selected_rows.empty
    if (like_count > 0 or rt_count > 0 or reply_count > 0 or follow_count > 0):
        if not target_handle: can_run = False
        if (like_count > 0 or rt_count > 0 or reply_count > 0) and not tweet_keyword: can_run = False

    with button_placeholder:
        col_exec1, col_exec2 = st.columns(2)
        if col_exec1.button("🚀 ローカルで実行", type="primary", use_container_width=True, disabled=not can_run):
            current_accounts = load_accounts()
            current_accounts['Select'] = False
            selected_screen_names = selected_rows['screen_name'].tolist()
            current_accounts.loc[current_accounts['screen_name'].isin(selected_screen_names), 'Select'] = True
            save_accounts(current_accounts)

            st.success("ローカルで自動応援プロセスを開始します..")

            cmd = [sys.executable, 'engagement_handler.py', 
                   '--count', str(int(like_count)),
                   '--rt-count', str(int(rt_count)),
                   '--reply-count', str(int(reply_count)),
                   '--follow-count', str(int(follow_count)),
                   '--tweet-count', str(int(tweet_count))]
            
            if target_handle:
                cmd += ['--target-id', target_handle]
            if tweet_keyword:
                cmd += ['--keyword', tweet_keyword]
            if fixed_text:
                cmd += ['--reply-text', fixed_text]
            if not use_ip_rotation:
                cmd.append('--skip-ip')
            if use_recreate:
                cmd.append('--recreate')
            if use_tweet_image:
                cmd.append('--tweet-image')
            if use_visible:
                cmd.append('--visible')

            try:
                if sys.platform == 'win32':
                    full_cmd = ['cmd', '/k'] + cmd
                    process = subprocess.Popen(full_cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
                else:
                    process = subprocess.Popen(cmd)
                st.info(f"コンソールウィンドウを起動しました (PID: {process.pid})。")
                time.sleep(1)
            except Exception as e:
                st.error(f"起動エラー: {e}")

        # [NEW] Global Control Center right here, right below local execution
        t_params = {
            'target_id': target_handle,
            'keyword': tweet_keyword,
            'count': int(like_count),
            'rt_count': int(rt_count),
            'reply_count': int(reply_count),
            'follow_count': int(follow_count),
            'tweet_count': int(tweet_count),
            'reply_text': fixed_text,
            'visible': use_visible,
            'tweet_image': use_tweet_image
        }
        render_global_control_center(ext_params=t_params)

    st.markdown('</div>', unsafe_allow_html=True)

elif page == "アカウント追加":
    st.markdown("<h2 class='glow-text' style='margin-bottom: 0;'>ログイン情報修復・追加</h2><div class='gold-line' style='margin-top: 0;'></div>", unsafe_allow_html=True)
    st.markdown('<div class="stellar-card" style="padding-top: 0;">', unsafe_allow_html=True)

    with st.expander("📝 手動登録・修正"):
        col_a, col_b, col_c = st.columns(3)
        manual_username = col_a.text_input("1. ユーザー名 / @ID", placeholder="example_user", key="manual_uname")
        manual_password = col_b.text_input("2. パスワード", type="password", key="manual_pw")
        totp_secret = col_c.text_input("3. 2段階認証キー（TOTP）", placeholder="JBSWY3DPEHPK3PXP", key="manual_totp")

        col_d, col_e, col_f = st.columns(3)
        auth_token_manual = col_d.text_input("4. Cookie（auth_token）", placeholder="1234abcd...", key="manual_auth")
        ct0_manual = col_e.text_input("5. Cookie（ct0）", placeholder="abcd1234...", key="manual_ct0")
        email_manual = col_f.text_input("6. メールアドレス（任意）", placeholder="email@example.com", key="manual_email")

        col_cat1, col_cat2 = st.columns(2)
        # Dynamic category options including IX groups
        try:
            ix_tmp = IXBrowserController()
            ix_all_groups = ix_tmp.get_all_groups()
            ix_group_names = [g['title'] for g in ix_all_groups if g['id'] is not None and g['title'] != 'すべて']
        except:
            ix_group_names = []
            
        base_categories = ["日常生活", "ゲーム", "投資", "美容", "子育て", "アイドル", "エンジニア", "アニメ", "料理", "web2", "web用", "非公式用", "その他"]
        category_options = sorted(list(set(base_categories + ix_group_names)))
        
        manual_category = col_cat1.selectbox("7. カテゴリー", category_options, index=0, key="manual_category")
        
        # New Default Group selector for IXBrowser
        ix_group_options = ["指定なし"] + [g['title'] for g in ix_all_groups if g['id'] is not None and g['title'] != 'すべて']
        ix_group_map = {g['title']: g['id'] for g in ix_all_groups if g['id'] is not None}
        
        manual_ix_group = col_cat2.selectbox("8. IXBrowserグループ (プロファイル作成用)", ix_group_options, index=0, key="manual_ix_group")
        selected_ix_group_id = ix_group_map.get(manual_ix_group) if manual_ix_group != "指定なし" else None

        if st.button("📥 情報をCSVに直接保存（ブラウザ起動なし）", help="ID/パスワード/2FA/Cookie(auth+ct0)をとりあえず登録・更新します"):
            # csv_path = get_active_csv_path()
            if False: # csv_path == "ixbrowser_api":
                st.error("API直結モードでは保存できません。")
            else:
                db = DBManager()
                df = db.get_all_accounts_df()
                clean_name = manual_username.replace('@', '').strip()
                if not df.empty and clean_name in df['screen_name'].astype(str).tolist():
                    idx = df[df['screen_name'] == clean_name].index[0]
                    if manual_password: df.at[idx, 'password'] = manual_password
                    if email_manual: df.at[idx, 'email'] = email_manual
                    if totp_secret: df.at[idx, 'totp_secret'] = totp_secret
                    if auth_token_manual: df.at[idx, 'auth_token'] = auth_token_manual
                    if ct0_manual: df.at[idx, 'ct0'] = ct0_manual
                    df.at[idx, 'category'] = manual_category
                    msg = f"✅ {clean_name} のログイン情報を更新しました。"
                else:
                    new_row = {col: "" for col in df.columns} if not df.empty else {}
                    new_row.update({
                        'screen_name': clean_name,
                        'username': clean_name,
                        'password': manual_password,
                        'email': email_manual,
                        'totp_secret': totp_secret,
                        'auth_token': auth_token_manual,
                        'ct0': ct0_manual,
                        'category': manual_category,
                        'group_id': selected_ix_group_id,
                        'group_name': manual_ix_group if manual_ix_group != "指定なし" else "",
                        'Select': True
                    })
                    for c in ['auth_token', 'ct0', 'totp_secret']:
                        if c not in new_row:
                            new_row[c] = ""
                    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
                    msg = f"✅ {clean_name} を新規追加しました。"
                
                # [FIX] 確実にDBに保存し、キャッシュを破棄して画面を更新する
                save_accounts(df) 
                st.success(msg)
                trigger_single_icon_download(clean_name)
                trigger_account_check(clean_name)
                time.sleep(1)
                st.rerun()


        use_ip_rotation = st.checkbox("IP回転を実行する（Androidデバイスモード）", value=True, key="p_login_rotate_ip")
        use_headless = st.checkbox("ヘッドレスモードで実行（ブラウザを隠す）", value=True, key="p_login_headless")

        # Group Selector for Login
        login_ix_group = st.selectbox("作成先 IXBrowserグループ", ix_group_options, index=0, key="login_ix_group")
        login_group_id = ix_group_map.get(login_ix_group) if login_ix_group != "指定なし" else None

        # ログインフォーム
        login_username = st.text_input("ユーザー名（@なし）", key="login_uname")
        login_password = st.text_input("パスワード", type="password", key="login_pw")
        login_email = st.text_input("メールアドレス（任意）", key="login_email")

        if st.button("ログイン & トークン再取得・保存", type="primary", disabled=not (login_username and login_password), key="p_login_btn"):
            with st.status("ログイン処理を実行中...", expanded=True) as status:
                script_path = os.path.join(os.getcwd(), 'account_manager.py')
                if not os.path.exists(script_path):
                    status.update(label="エラー: 実行ファイルが見つかりません", state="error")
                    st.error(f"実行ファイルが見つかりません: {script_path}")
                else:
                    cmd = [sys.executable, script_path, login_username, login_password]
                    if login_email: cmd.append(f"--email={login_email}")
                    if use_ip_rotation: cmd.append('--rotate-ip')
                    if use_headless: cmd.append('--headless')
                    if login_group_id: cmd.append(f'--group-id={login_group_id}')

                    try:
                        # Use Popen to avoid blocking the UI
                        process = subprocess.Popen(
                            cmd, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            text=True, 
                            encoding='utf-8', 
                            errors='replace',
                            creationflags=subprocess.CREATE_NO_WINDOW if sys.platform == 'win32' else 0
                        )

                        import json
                        full_stdout = ""
                        full_stderr = ""
                        data = None
                        
                        # Real-time log display
                        log_placeholder = st.empty()
                        while True:
                            line = process.stdout.readline()
                            if not line and process.poll() is not None:
                                break
                            if line:
                                full_stdout += line
                                # Clean up formatting for UI
                                clean_line = line.strip()
                                if clean_line:
                                    log_placeholder.text(f"DEBUG: {clean_line}")
                                    # Try to catch JSON result
                                    if clean_line.startswith('{') and clean_line.endswith('}'):
                                        try:
                                            data = json.loads(clean_line)
                                        except: pass

                        _, stderr_left = process.communicate()
                        full_stderr += (stderr_left or "")

                        if process.returncode == 0 and data:
                            if data.get("status") == "success":
                                status.update(label=f"ログイン成功: {data.get('screen_name')}", state="complete")
                                trigger_single_icon_download(data.get('screen_name'))
                                time.sleep(0.5)
                                st.rerun()
                            else:
                                status.update(label=f"ログイン失敗: {data.get('message')}", state="error")
                                with st.expander("詳細ログ"):
                                    st.code(full_stdout)
                                    st.code(full_stderr)
                        else:
                            status.update(label="❌ 処理が正常に完了しませんでした", state="error")
                            with st.expander("詳細ログ"):
                                st.code(full_stdout)
                                st.code(full_stderr)

                    except Exception as e:
                        status.update(label=f"💥 実行エラー: {e}", state="error")
                        st.error(f"実行エラー: {e}")

    st.subheader("IXBrowserから一括インポート")

    try:
        ix_ctrl = IXBrowserController()
        all_ix_groups = ix_ctrl.get_all_groups()
        # 除外するグループIDのリスト
        target_excluded_ids = [
            283682, 274711, 261161, 274048, 260964, 
            255449, 253113, 277506, 248214
        ]
        
        # タイトルキーワードまたはIDで除外
        ix_groups = [
            g for g in all_ix_groups 
            if "販売" not in str(g.get('title', '')) 
            and "サイト用" not in str(g.get('title', ''))
            and "リンク渡す" not in str(g.get('title', ''))
            and g['id'] not in target_excluded_ids
        ]
        excluded_group_ids = [
            g['id'] for g in all_ix_groups 
            if "販売" in str(g.get('title', '')) 
            or "サイト用" in str(g.get('title', ''))
            or "リンク渡す" in str(g.get('title', ''))
            or g['id'] in target_excluded_ids
        ]
        
        group_options = []
        for g in ix_groups:
            if g['id'] is None:
                group_options.append("すべて (全グループから取得)")
            else:
                group_options.append(f"{g['title']} (ID: {g['id']})")

        col_imp1, col_imp2 = st.columns([2, 1])
        selected_option = col_imp1.selectbox("インポート対象グループを選択", group_options)

        target_group = None
        for g in ix_groups:
            opt_name = "すべて (全グループから取得)" if g['id'] is None else f"{g['title']} (ID: {g['id']})"
            if opt_name == selected_option:
                target_group = g
                break
        
        # Space to align button with selectbox field
        col_imp2.markdown("<div style='margin-top: 28px;'></div>", unsafe_allow_html=True)
        if col_imp2.button("📥 インポートを開始", use_container_width=True):
            if target_group:
                with st.status(f"グループ '{target_group['title']}' からインポート中...", expanded=True) as status:
                    profiles = ix_ctrl.get_all_accounts(group_id=target_group['id'])
                    status.write(f"✅ {len(profiles)} 件のプロファイルを取得しました。")

                    if not profiles:
                        status.update(label="インポート失敗: プロファイルが見つかりません", state="error")
                    else:
                        db = DBManager()
                        current_df = db.get_all_accounts_df()
                        existing_names = set(current_df['screen_name'].astype(str).tolist()) if not current_df.empty else set()
                        new_rows = []
                        results_for_preview = []
                        needed_cols = [
                            'screen_name', 'username', 'password', 'email', 'auth_token', 'ct0', 'totp_secret',
                            'is_suspended', 'Select'
                        ]

                        for p in profiles:
                            name = p.get('screen_name')
                            if not name: continue
                            
                            # 全グループ取得時は、除外対象グループのアカウントをスキップ
                            if target_group['id'] is None and p.get('group_id') in excluded_group_ids:
                                continue

                            if name in existing_names:
                                status.write(f"  🔄 更新中: {name}")
                                idx = current_df[current_df['screen_name'] == name].index[0]
                                for col in ['password', 'email', 'auth_token', 'ct0', 'totp_secret']:
                                    if p.get(col): current_df.at[idx, col] = p.get(col)
                                results_for_preview.append(p)
                            else:
                                status.write(f"  ➕ 追加中: {name}")
                                row = {col: "" for col in needed_cols}
                                row.update(p)
                                row['Select'] = True
                                row['is_suspended'] = False
                                if target_group and target_group['id'] is not None:
                                    row['category'] = target_group['title']
                                    row['group_id'] = str(target_group['id'])
                                    row['group_name'] = target_group['title']
                                elif p.get('group_id'):
                                    row['group_id'] = str(p.get('group_id'))
                                
                                new_rows.append(row)
                                results_for_preview.append(row)

                        if results_for_preview:
                            final_df = pd.concat([current_df, pd.DataFrame(new_rows)], ignore_index=True) if new_rows else current_df
                            db.save_accounts_df(final_df)
                            status.update(label=f"インポート成功 ({len(results_for_preview)} 件)", state="complete")
                            
                            st.success("処理されたアカウント情報の一覧です。")
                            preview_cols = ['screen_name', 'password', 'totp_secret', 'auth_token', 'ct0', 'email']
                            display_df = pd.DataFrame(results_for_preview)
                            st.dataframe(display_df[[c for c in preview_cols if c in display_df.columns]])

                            st.info("🔄 アイコン同期を開始します...")
                            subprocess.Popen([sys.executable, 'asset_sync.py', '--selected'], 
                                           creationflags=(subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0))

                            # [NEW] Trigger targeted status check for imported accounts
                            new_names = [r['screen_name'] for r in results_for_preview]
                            trigger_account_check(new_names)

                            time.sleep(3)
                            st.rerun()
                        else:
                            status.update(label="変更なし", state="complete")

    except Exception as e:
        st.error(f"IXBrowser連携エラー: {e}")

    st.markdown('</div>', unsafe_allow_html=True)


elif page == "凍結チェック用":
    st.markdown("<h2 class='glow-text'>チェック用アカウント管理</h2>", unsafe_allow_html=True)
    st.info("ここに登録されているアカウント（グループ名: 凍結チェック用）が、高速一括チェックのスキャナーとして使用されます。")
    db = DBManager()
    df_all = load_accounts()
    
    # 凍結チェック用グループのアカウントを抽出
    df_display = df_all[df_all['group_name'].fillna('').str.contains('凍結チェック', case=False, na=False)]
    
    # [NEW] もし件数が足りない場合、IXBrowserの最新情報をチェックして補完
    if len(df_display) < 11:
        try:
            from modules.ixbrowser.ixbrowser_controller import IXBrowserController
            ctrl = IXBrowserController()
            all_profiles = ctrl.get_all_profiles()
            # 「凍結チェック用」という名前を含むグループに属するプロファイルを抽出
            ix_targets = [p for p in all_profiles if '凍結チェック' in str(p.get('group_title', ''))]
            
            if len(ix_targets) > len(df_display):
                st.info(f"IXBrowserから最新の {len(ix_targets)} 件を同期中...")
                for p in ix_targets:
                    uname = p.get('username')
                    gname = p.get('group_title')
                    if uname:
                        # DBを最新グループ名で更新
                        conn = db.get_connection()
                        cursor = conn.cursor()
                        cursor.execute(f"UPDATE accounts SET group_name = ? WHERE username = ?", (gname, uname))
                        if db.db_type == "sqlite": conn.commit()
                # 更新後に再読み込み
                st.cache_data.clear()
                df_all = load_accounts()
                df_display = df_all[df_all['group_name'].fillna('').str.contains('凍結チェック', case=False, na=False)]
        except: pass

    st.markdown(f"**登録済みスキャナー: {len(df_display)} 件**")
    
    col_ref1, col_ref2 = st.columns([5, 1])
    if col_ref2.button("🔄 更新", key="fcheck_ref"):
        st.cache_data.clear(); st.rerun()

    if df_display.empty:
        st.warning("「凍結チェック用」グループのアカウントがありません。「アカウント管理」からグループを変更して追加してください。")
    else:
        columns_per_row = 4
        account_list = df_display.to_dict('records')
        for i in range(0, len(account_list), columns_per_row):
            cols = st.columns(columns_per_row)
            for j in range(columns_per_row):
                if i + j < len(account_list):
                    acc = account_list[i + j]
                    name = acc.get('screen_name', 'Unknown')
                    disp = acc.get("assigned_name", "") or name
                    with cols[j]:
                        icon_path = os.path.join('data/icons', f"{name}.jpg")
                        b64_icon = get_base64_image(icon_path)
                        icon_html = f'<img src="data:image/jpeg;base64,{b64_icon}" style="width: 60px; height: 60px; border-radius: 50%; border: 2px solid #a855f7; object-fit: cover; margin-bottom: 5px;">' if b64_icon else '<div style="font-size: 2rem; margin-bottom: 5px;">👤</div>'
                        st.markdown(f'<div style="text-align:center; background:rgba(168,85,247,0.05); padding:10px; border-radius:10px; border:1px solid rgba(168,85,247,0.2);">{icon_html}<div style="color:#a855f7;font-weight:900;font-size:0.8rem;">{disp}</div><div style="font-size:0.7rem;">@{name}</div></div>', unsafe_allow_html=True)
                        
                        bt1, bt2, bt3 = st.columns(3)
                        if bt1.button("✏️", key=f"fc_ed_{name}", help="編集"):
                            st.session_state.editing_account = name; st.rerun()
                        if bt2.button("🗑️", key=f"fc_del_{name}", help="削除"):
                            st.session_state[f"confirm_del_fc_{name}"] = True
                        if bt3.button("🔑", key=f"fc_login_{name}", help="ログイン確認"):
                            st.session_state.editing_account = name; st.session_state.page = "account_mgmt"; st.rerun()

                        if st.session_state.get(f"confirm_del_fc_{name}"):
                            st.error(f"削除？")
                            if st.button("削除実行", key=f"conf_y_fc_{name}"):
                                perform_delete_account(name)
                                st.cache_data.clear(); st.rerun()

elif page == "アカウント管理":
    st.markdown("<h2 class='glow-text' style='margin-bottom: 0;'>アカウント管理</h2><div class='gold-line' style='margin-top: 0;'></div>", unsafe_allow_html=True)
    
    # [NEW] 最優先：Cookie一括同期ボタンを一番上に配置
    st.info("💡 IXBrowserのサーバーから最新のクッキー（auth_token/ct0）を直接取得してDBに保存します。")
    if st.button("🔄 IXBrowserから全クッキーを同期実行", type="primary", use_container_width=True):
        from modules.ixbrowser.ixbrowser_controller import IXBrowserController
        ctrl = IXBrowserController()
        db = DBManager()
        # 最新のデータを読み直す
        df_sync = load_accounts()
        targets = df_sync.to_dict('records')
        
        with st.status("🍪 クッキー同期中...", expanded=True) as sync_status:
            db = DBManager()
            targets = df_sync.to_dict('records')
            total_sync = len(targets)
            p_bar = st.progress(0)
            
            success_sync = 0
            for idx, row in enumerate(targets):
                uname = row['screen_name']
                pid = row.get('profile_id')
                
                try:
                    # [修正] DBにIDがなくても、IXBrowser内に既存のものがあれば紐付ける (新規作成は禁止設定なので安全)
                    pid = ctrl.get_or_create_profile(uname)
                    
                    if not pid:
                        sync_status.write(f"⏭️ [{idx+1}/{total_sync}] @{uname} IXBrowser内にプロファイルが見つからないためスキップ")
                        continue
                    
                    if pid:
                        sync_status.write(f"⏳ [{idx+1}/{total_sync}] @{uname} クッキー取得中...")
                        c_list = ctrl.client.get_profile_cookies(pid)
                        if c_list:
                            auth_token = ""; ct0 = ""
                            for c in c_list:
                                if c.get('name') == 'auth_token': auth_token = c.get('value')
                                elif c.get('name') == 'ct0': ct0 = c.get('value')
                            
                            if auth_token and ct0:
                                db.update_cookies(uname, auth_token, ct0)
                                success_sync += 1
                                sync_status.write(f"✅ @{uname} 同期成功")
                            else:
                                sync_status.write(f"⚠️ @{uname} クッキー未設定")
                        else:
                            sync_status.write(f"❌ @{uname} 取得失敗 (APIエラー)")
                    
                    # サーバー負荷軽減のためわずかに待機
                    time.sleep(0.5)
                except Exception as e:
                    sync_status.write(f"⚠️ @{uname} 停止: {e}")
                
                p_bar.progress((idx + 1) / total_sync)
            
            st.cache_data.clear()
            if 'cached_df_all' in st.session_state: del st.session_state.cached_df_all
            sync_status.update(label=f"✅ {success_sync} 件のクッキー同期が完了しました！", state="complete")
            time.sleep(1)
            st.rerun()
    st.markdown("---")

    # --- [NEW] Status Check Buttons moved here ---
    with st.expander("🔍 アカウント状態の一括確認ツール", expanded=False):
        col_bulk1, col_bulk2 = st.columns(2)
        with col_bulk1:
            if st.button("🌐 公開プロフィール一括確認", type="secondary", use_container_width=True, help="ログインせずに公開ページを確認します（高速・安全）"):
                cmd = [sys.executable, 'safety_check.py']
                c_flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                subprocess.Popen(cmd, creationflags=c_flags)
                st.info("公開確認プロセスを開始しました。別ウィンドウで進行します。")
            
            if st.button("⚡ 高速ローテーション一括チェック", type="secondary", use_container_width=True, help="curl_cffiとクッキー回転を使用して高速に状態を確認します"):
                cmd = [sys.executable, 'check_full_status.py', '--db', '--force']
                c_flags = subprocess.CREATE_NEW_CONSOLE if sys.platform == 'win32' else 0
                subprocess.Popen(cmd, creationflags=c_flags)
                st.info("高速チェックプロセスを開始しました。別ウィンドウで進行します。")

            st.markdown("---")
            st.markdown("📦 **一括グループ移動**")
            try:
                ix_ctrl = IXBrowserController()
                ix_groups = ix_ctrl.get_all_groups()
                move_options = ["(選択してください)"] + [g['title'] for g in ix_groups if g['id'] is not None and g['title'] != 'すべて']
                move_map = {g['title']: g['id'] for g in ix_groups if g['id'] is not None}
                
                target_move_group = st.selectbox("移動先グループを選択", move_options, key="bulk_move_group_sel")
                if st.button("🚛 選択したアカウントを移動", type="secondary", use_container_width=True):
                    if target_move_group == "(選択してください)":
                        st.error("移動先を選択してください。")
                    else:
                        df_to_move = load_accounts()
                        selected_to_move = df_to_move[df_to_move['Select'] == True]
                        if selected_to_move.empty:
                            st.warning("移動対象のアカウントが選択されていません。")
                        else:
                            new_gid = move_map[target_move_group]
                            with st.status(f"{len(selected_to_move)} 件を '{target_move_group}' へ移動中...") as move_status:
                                from modules.ixbrowser.ixbrowser_local_api import Profile
                                ix_client = ix_ctrl.client
                                db = DBManager()
                                
                                success_move = 0
                                for _, row in selected_to_move.iterrows():
                                    uname = row['screen_name']
                                    pid = row.get('profile_id')
                                    # 1. IXBrowser API Update
                                    if pid:
                                        p_obj = Profile(profile_id=pid, name=uname, group_id=new_gid)
                                        ix_client.update_profile(p_obj)
                                    
                                    # 2. DB Update
                                    db = DBManager()
                                    conn = db.get_connection()
                                    cursor = conn.cursor()
                                    p = db._placeholder()
                                    cursor.execute(f'UPDATE accounts SET group_id={p}, group_name={p} WHERE username={p}', (str(new_gid), target_move_group, uname))
                                    if db.db_type not in ["mysql", "postgres"]: conn.commit()
                                    success_move += 1
                                
                                st.cache_data.clear()
                                move_status.update(label=f"✅ {success_move} 件の移動が完了しました！", state="complete")
                                time.sleep(1)
                                st.rerun()
            except Exception as e:
                st.error(f"グループ取得エラー: {e}")

        with col_bulk2:
            if st.button("🔒 精密ロック・凍結一括チェック", type="primary", use_container_width=True, help="各アカウントにログイン試行し、ロックや詳細な凍結状態を確認します（要IP回転）"):
                df_status = load_accounts()
                targets = df_status[df_status['Select'] == True]
                if targets.empty:
                    st.warning("チェック対象のアカウントが選択されていません。")
                else:
                    with st.status("🚀 精密一括チェック実行中...", expanded=True) as status:
                        from modules.ixbrowser.ixbrowser_controller import IXBrowserController
                        from modules.ixbrowser.bot_logic_dp import IXBrowserBotLogicDP
                        from modules.router.pixel_rotator import PixelIPRotator
                        from login_service import update_account_status
                        
                        ctrl = IXBrowserController()
                        
                        results = {"OK": 0, "SUSPENDED": 0, "LOCKED": 0, "ERROR": 0}
                        progress_bar = st.progress(0)
                        
                        for idx, (index, row) in enumerate(targets.iterrows()):
                            name = row['screen_name']
                            status.write(f"--- アカウント {idx+1}/{len(targets)}: {name} ---")
                            
                            try:
                                status.write(f"🌍 [{name}] IXBrowser起動中...")
                                # [修正] 自動作成を無効化 (allow_create=False)
                                p_id = ctrl.get_or_create_profile(name, allow_create=False)
                                page = ctrl.open_browser_dp(p_id, headless=False)
                                if not page:
                                    status.write(f"❌ [{name}] ブラウザ起動失敗")
                                    results["ERROR"] += 1
                                    continue
                                
                                status.write(f"📊 [{name}] 状態判定中...")
                                bot = IXBrowserBotLogicDP(page)
                                res_status, msg = bot.check_account_status()
                                
                                # [NEW] 詳細情報（名前、フォロー数、フォロワー数）を取得して保存
                                live_name = bot.get_display_name()
                                counts = bot.get_follow_counts_via_api() # API経由で高速取得
                                if not counts:
                                    # APIがダメならDOMから取得試行
                                    counts = bot.get_follow_counts_from_dom()
                                
                                db = DBManager()
                                if live_name:
                                    db.save_display_name(name, live_name)
                                
                                if counts:
                                    db.update_follow_counts(name, counts['following'], counts['followers'])
                                
                                update_account_status(name, res_status, msg)
                                results[res_status if res_status in results else "ERROR"] += 1
                                status.write(f"✅ [{name}] 完了: {res_status} ({live_name if live_name else ''})")
                                
                            except Exception as e:
                                status.write(f"⚠️ [{name}] エラー: {e}")
                                results["ERROR"] += 1
                            finally:
                                status.write(f"🧹 [{name}] ブラウザを終了中...")
                                try: page.quit()
                                except: pass
                                ctrl.close_browser(p_id, screen_name=name)
                                
                                progress_bar.progress((idx + 1) / len(targets))
                        
                        status.update(label=f"一括チェック成功 (正常: {results['OK']}, 凍結: {results['SUSPENDED']}, ロック: {results['LOCKED']}, 失敗: {results['ERROR']})", state="complete")
                        st.rerun()

    st.markdown('<div class="stellar-card" style="padding-top: 0;">', unsafe_allow_html=True)

    # Use a more robust loading pattern to avoid empty state
    if 'cached_df_all' not in st.session_state or st.session_state.cached_df_all is None:
        with st.spinner("📦 アカウントデータをロード中..."):
            st.session_state.cached_df_all = load_accounts()
    
    df_all = st.session_state.cached_df_all
    if df_all is None: df_all = pd.DataFrame()
    df_display = df_all.copy()
        
    if 'mgmt_init_done' not in st.session_state:
        if not df_all.empty and df_all['Select'].any():
            df_all['Select'] = False
            save_accounts(df_all)
        st.session_state.mgmt_init_done = True
        if 'tournament_init_done' in st.session_state:
            del st.session_state.tournament_init_done
        
    st.markdown(f"**アカウント総数: {len(df_all)} アカウント**")

    col_mgmt_s, col_mgmt_a, col_mgmt_n, col_mgmt_u = st.columns([6, 1, 1, 1])
    mgmt_search = col_mgmt_s.text_input("🔍 アカウント検索", placeholder="IDで絞り込み...", key="mgmt_search_bar")
    selected_group_filter = st.session_state.get('selected_group_filter', "すべて")
    st.info(f"📂 **表示中のグループ: {selected_group_filter}**")

    if mgmt_search:
        df_display = df_display[df_display['screen_name'].str.contains(mgmt_search, case=False, na=False)]
        
    if selected_group_filter != "すべて":
        target = selected_group_filter.strip()
        # Handle NaN and empty strings safely
        g_names = df_display['group_name'].fillna('').str.strip()
        c_names = df_display['category'].fillna('').str.strip()
        df_display = df_display[
            (g_names == target) | 
            ((g_names == '') & (c_names == target))
        ]

    st.markdown(f"**表示中: {len(df_display)} / 全体: {len(df_all)} アカウント**")

    use_ip_mgmt = st.checkbox("🔄 **操作前にIPを変更する (Androidデバイス)**", value=True, key="ip_mgmt_toggle")

    col_m1, col_m2, col_m3, col_m4 = st.columns([1, 1, 1, 1])
    
    if col_m4.button("📡 グループ情報を最新同期", help="IXBrowserから最新のグループ情報を取得して、既存のアカウントに紐付けます。"):
        with st.status("IXBrowserとグループ情報を同期中...", expanded=True) as status:
            try:
                ix = IXBrowserController()
                profiles = ix.client.get_profile_list(limit=1000)
                groups = ix.get_all_groups()
                group_map = {str(g['id']): g['title'] for g in groups if g['id'] is not None}
                db = DBManager()
                df_sync = db.get_all_accounts_df()
                count = 0
                for p in profiles:
                    name = p.get('name')
                    gid = str(p.get('group_id', ''))
                    gname = group_map.get(gid, '')
                    if name in df_sync['screen_name'].tolist():
                        idx = df_sync[df_sync['screen_name'] == name].index[0]
                        df_sync.at[idx, 'group_id'] = gid
                        df_sync.at[idx, 'group_name'] = gname
                        if not df_sync.at[idx, 'category']:
                            df_sync.at[idx, 'category'] = gname
                        count += 1
                db.save_accounts_df(df_sync)
                status.update(label=f"✅ {count} 件のアカウント情報を同期しました。", state="complete")
                time.sleep(1)
                st.rerun()
            except Exception as e:
                status.update(label=f"❌ 同期エラー: {e}", state="error")

    with st.expander("🚀 高度な一括操作 (数千アカウント対応)", expanded=False):
        st.markdown("#### AIカテゴリー自動一括設定")
        st.info("全てのアカウントまたは選択中のアカウントに対して、名前から「ゲーム」「投資」などのカテゴリーをAIで自動判定してDBに保存します。")
        col_bulk_a, col_bulk_s = st.columns(2)
        
        def run_bulk_categorization(targets):
            settings = load_settings()
            keys = settings.get("gemini_api_key", "") or settings.get("GEMINI_API_KEYS", [])
            ai = AIGenerator(api_keys=keys)
            db = DBManager()
            progress_bar = st.progress(0)
            status_text = st.empty()
            total = len(targets)
            for idx, row in enumerate(targets.to_dict('records')):
                name = str(row['screen_name'])
                bio = str(row.get('biography', '') or row.get('description', ''))
                
                # [修正] 画像パスや空の名前をスキップ
                if '/' in name or '.jpg' in name or not name.strip():
                    continue

                # デバッグ用ログ出力
                with open('debug_categorization.log', 'a', encoding='utf-8') as f:
                    f.write(f"Processing index {idx}: name='{name}', bio_len={len(bio)}\n")
                
                status_text.text(f"分析中 ({idx+1}/{total}): @{name}")
                theme = ai.determine_theme(name, bio=bio)
                db.update_category(name, theme)
                progress_bar.progress((idx+1)/total)
                
                # APIのレートリミット対策で1秒待機
                time.sleep(1)
            status_text.success(f"✅ {total} 件の精密判定が完了しました。")
            time.sleep(2)
            st.rerun()

        if col_bulk_a.button("🔥 全アカウントを自動判定実行", use_container_width=True):
            run_bulk_categorization(df_all)
        if col_bulk_s.button("🎯 選択中のみ自動判定実行", use_container_width=True):
            run_bulk_categorization(df_all[df_all['Select'] == True])
        st.markdown("---")

    selected_to_delete = df_all[df_all['Select'] == True]
    delete_count = len(selected_to_delete)

    if col_m1.button("🗑️ 選択したアカウントを削除", type="primary"):
        if delete_count > 0: st.session_state.confirm_delete = True
        else: st.warning("削除するアカウントが選択されていません。")

    if st.session_state.get('confirm_delete') and delete_count > 0:
        with st.status("⚠️ 削除の最終確認", expanded=True):
            st.error(f"⚠️ 現在チェックされている **{delete_count} 件** のアカウントを完全に削除しますか？")
            c1, c2 = st.columns(2)
            if c1.button("🔥 はい, 削除を実行する", type="primary", use_container_width=True):
                for _, row in selected_to_delete.iterrows():
                    perform_delete_account(row['screen_name'])
                st.session_state.confirm_delete = False
                st.success(f"正常に {delete_count} 件 削除しました。")
                time.sleep(1)
                st.rerun()
            if c2.button("いいえ、やめる", use_container_width=True):
                st.session_state.confirm_delete = False
                st.rerun()

    if col_m2.button("🔄 選択中のアイコンを同期", type="secondary"):
        st.info("チェックしたアカウントのアイコン同期を開始します。")
        cmd = [sys.executable, 'asset_sync.py', '--selected']
        if use_ip_mgmt: cmd.append('--rotate-ip')
        subprocess.Popen(['cmd', '/k'] + cmd if sys.platform == 'win32' else cmd)

    if col_m3.button("🖼️ 画像未設定のみ同期", type="secondary"):
        st.info("アイコン未設定のアカウントのみ同期を開始します。")
        cmd = [sys.executable, 'asset_sync.py', '--missing-only', '--rotate-ip']
        subprocess.Popen(['cmd', '/k'] + cmd if sys.platform == 'win32' else cmd)

    st.markdown('<div class="gold-line" style="width: 100%;"></div>', unsafe_allow_html=True)

    col_mgmt_a, col_mgmt_n, col_mgmt_u = st.columns([1, 1, 1])
    if col_mgmt_a.button("全て選択", use_container_width=True):
        if not df_display.empty:
            db = DBManager()
            db.update_all_selection_status(True, screen_names=df_display['screen_name'].tolist())
            clear_account_cache()
            # Session state sync
            for idx, row in df_display.iterrows():
                key = f"sel_m_{row['screen_name']}_{idx}"
                st.session_state[key] = True
            st.rerun()
    if col_mgmt_n.button("選択解除", use_container_width=True):
        if not df_display.empty:
            db = DBManager()
            db.update_all_selection_status(False, screen_names=df_display['screen_name'].tolist())
            clear_account_cache()
            # Session state sync
            for idx, row in df_display.iterrows():
                key = f"sel_m_{row['screen_name']}_{idx}"
                st.session_state[key] = False
            st.rerun()
    if col_mgmt_u.button("未分類のみ選択", use_container_width=True):
        def is_unclassified(val):
            v = str(val).strip()
            return v in ['日常生活', 'その他', '', 'None', 'nan'] or '未分類' in v
        target_names = df_display[df_display['category'].apply(is_unclassified)]['screen_name'].tolist()
        if target_names:
            df_all.loc[df_all['screen_name'].isin(target_names), 'Select'] = True
            save_accounts(df_all)
            st.rerun()

    render_editing_overlay(df_all)
    
    # Pagination for Management
    PAGE_SIZE_MGMT = 24
    total_mgmt = len(df_display)
    num_pages_mgmt = (total_mgmt + PAGE_SIZE_MGMT - 1) // PAGE_SIZE_MGMT
    
    if num_pages_mgmt > 1:
        st.markdown("---")
        col_pm1, col_pm2, col_pm3 = st.columns([1, 2, 1])
        page_num_mgmt = col_pm2.number_input("ページ選択", min_value=1, max_value=num_pages_mgmt, value=1, key="mgmt_page_nav")
        st.markdown(f"<p style='text-align: center; color: #888;'>Page {page_num_mgmt} of {num_pages_mgmt}</p>", unsafe_allow_html=True)
        
        start_idx = (page_num_mgmt - 1) * PAGE_SIZE_MGMT
        end_idx = start_idx + PAGE_SIZE_MGMT
        paged_mgmt = df_display.iloc[start_idx:end_idx]
    else:
        paged_mgmt = df_display

    def toggle_selection(username, current_val, key):
        new_val = st.session_state[key]
        if new_val != current_val:
            db = DBManager()
            db.update_account_selection(username, new_val)
            clear_account_cache()

    columns_per_row = 4
    account_list = paged_mgmt.to_dict('records')
    
    for i in range(0, len(account_list), columns_per_row):
        cols = st.columns(columns_per_row)
        for j in range(columns_per_row):
            if i + j < len(account_list):
                acc = account_list[i + j]
                name = acc['screen_name']
                
                with cols[j]:
                    icon_path = os.path.join('data/icons', f"{name}.jpg")
                    b64_icon = get_base64_image(icon_path)
                    icon_html = f'<img src="data:image/jpeg;base64,{b64_icon}" style="width: 50px; height: 50px; border-radius: 50%; border: 2px solid #D4AF37; object-fit: cover; margin-bottom: 5px;">' if b64_icon else '<div style="font-size: 1.5rem; margin-bottom: 5px;">👤</div>'
                    
                    sync_status = str(acc.get('sync_status', '')).strip()
                    status_c = "#2ecc71" if "成功" in sync_status or "完了" in sync_status else "#e74c3c" if "失敗" in sync_status else "#D4AF37"
                    
                    # 統計情報
                    following = acc.get('following_count', 0)
                    followers = acc.get('followers_count', 0)
                    last_tweet = acc.get('last_tweet_at', '未投稿')
                    display_name = acc.get("assigned_name", "") or name
                    profile_url = f"https://x.com/{name}"
                    cat_val = acc.get('category', '未分類')
                    reach = acc.get('reach_status', 'OK')
                    reach_color = "#2ecc71" if reach == "OK" else "#e74c3c"
                    
                    # Cookie状態の確認
                    has_auth = bool(str(acc.get('auth_token', '')).strip()) and str(acc.get('auth_token', '')) != 'nan'
                    has_ct0 = bool(str(acc.get('ct0', '')).strip()) and str(acc.get('ct0', '')) != 'nan'
                    cookie_status = "✅" if has_auth and has_ct0 else "⚠️" if has_auth or has_ct0 else "❌"
                    cookie_color = "#2ecc71" if cookie_status == "✅" else "#f1c40f" if cookie_status == "⚠️" else "#e74c3c"

                    st.markdown(f"""
                        <div style="background: rgba(255,255,255,0.03); border: 1px solid rgba(212,175,55,0.2); border-radius: 10px; padding: 10px; text-align: center; margin-bottom: 5px;">
                            <div style="display: flex; justify-content: space-between; margin-bottom: 5px;">
                                <span style="background: rgba(168, 85, 247, 0.1); color: #a855f7; font-size: 0.6rem; padding: 1px 4px; border-radius: 4px;">{cat_val}</span>
                                <div style="display: flex; gap: 4px;">
                                    <span style="background: {cookie_color}22; color: {cookie_color}; font-size: 0.6rem; padding: 1px 4px; border-radius: 4px;">Cookie: {cookie_status}</span>
                                    <span style="background: {reach_color}22; color: {reach_color}; font-size: 0.6rem; padding: 1px 4px; border-radius: 4px;">{reach}</span>
                                </div>
                            </div>
                            {icon_html}
                            <div style="font-size: 0.9rem; color: #D4AF37; font-weight: 900; overflow: hidden; white-space: nowrap;">{display_name}</div>
                            <div style="font-size: 0.75rem; margin-bottom: 2px;"><a href="{profile_url}" target="_blank" style="text-decoration: none; color: #ccc;">@{name}</a></div>
                            <div style="font-size: 0.75rem; color: #888; font-weight: 600; margin: 3px 0;">📊 {following} / {followers}</div>
                            <div style="font-size: 0.65rem; color: #666;">🕒 {last_tweet}</div>
                            <div style="font-size: 0.7rem; color: {status_c}; font-weight: 600; margin-top: 3px;">● {sync_status if sync_status else "待機中"}</div>
                        </div>
                    """, unsafe_allow_html=True)
                    
                    real_idx = paged_mgmt.index[i + j]
                    b_col1, b_col2, b_col3, b_col4 = st.columns([1, 1, 1, 1])
                    b_col1.checkbox("✔", value=bool(acc.get('Select', False)), key=f"sel_m_{name}_{real_idx}", on_change=toggle_selection, args=(name, bool(acc.get('Select', False)), f"sel_m_{name}_{real_idx}"))
                    if b_col2.button("✏️", key=f"ed_m_{name}_{real_idx}"): st.session_state.editing_account = name; st.rerun()
                    if b_col3.button("🔄", key=f"rs_m_{name}_{real_idx}", help="Cookie削除"): st.session_state[f"confirm_reset_mgmt_{name}"] = True
                    if b_col4.button("🗑️", key=f"dl_m_{name}_{real_idx}"): st.session_state[f"confirm_del_mgmt_{name}"] = True
                    
                    # 確認ダイアログ類
                    if st.session_state.get(f"confirm_reset_mgmt_{name}"):
                        st.warning(f"Cookie消去して再作成しますか？")
                        cr1, cr2 = st.columns(2)
                        if cr1.button("実行", key=f"conf_r_y_{name}"):
                            if perform_profile_reset(acc.get('profile_id'), name): 
                                st.success("再作成完了"); time.sleep(1); st.rerun()
                        if cr2.button("止める", key=f"conf_r_n_{name}"):
                            del st.session_state[f"confirm_reset_mgmt_{name}"]; st.rerun()

                    if st.session_state.get(f"confirm_del_mgmt_{name}"):
                        st.error(f"削除しますか？")
                        cd1, cd2 = st.columns(2)
                        if cd1.button("削除", key=f"conf_d_y_{name}"):
                            perform_delete_account(name); st.rerun()
                        if cd2.button("止める", key=f"conf_d_n_{name}"):
                            del st.session_state[f"confirm_del_mgmt_{name}"]; st.rerun()
elif page == "凍結":
    st.markdown("<h2 class='glow-text'>凍結一覧</h2>", unsafe_allow_html=True)
    db = DBManager()
    df_all = load_accounts()
    
    # Column safety check
    if 'is_suspended' not in df_all.columns:
        df_all['is_suspended'] = False
    if 'sync_status' not in df_all.columns:
        df_all['sync_status'] = ""
        
    # 凍結、Suspended、不在、Unavailable など、ログイン不可能なものに限定
    frozen_keywords = '凍結|Suspended|不在|Unavailable|UserUnavailable|ロック中'
    df_display = df_all[
        (df_all['is_suspended'] == True) | 
        (df_all['is_alive'] == False) | 
        (df_all['sync_status'].str.contains(frozen_keywords, case=False, na=False))
    ]
    st.markdown(f"**要注意・凍結アカウント: {len(df_display)} 件**")
    
    # 0件でも更新ボタンを常に表示
    col_ref1, col_ref2 = st.columns([5, 1])
    if col_ref2.button("🔄 更新", key="frozen_ref_always"):
        st.cache_data.clear(); st.rerun()

    if df_display.empty:
        st.success("該当するアカウントはありません。")
    else:
        col_act1, col_act2, col_act3 = st.columns(3)
        if col_act1.button("📊 出力", key="frozen_exp"): 
            subprocess.run([sys.executable, 'export_login_failures.py', '--type', 'frozen'])
            st.success("完了")
        if col_act2.button("🧹 一括解除", key="frozen_clr"):
            db.bulk_clear_sync_status('凍結')
            if os.path.exists('data/task_progress.json'):
                try:
                    with open('data/task_progress.json', 'r', encoding='utf-8') as f: p_data = json.load(f)
                    p_data['fail'] = 0; p_data['fail_list'] = []
                    with open('data/task_progress.json', 'w', encoding='utf-8') as f: json.dump(p_data, f, ensure_ascii=False)
                except: pass
            st.cache_data.clear(); st.rerun()
        if col_act3.button("🗑️ 一括削除", key="frozen_bulk_del"):
            st.session_state.confirm_frozen_bulk_del = True

        if st.session_state.get('confirm_frozen_bulk_del'):
            st.error(f"⚠️ 表示されている凍結アカウント {len(df_display)} 件をすべて削除しますか？")
            d1, d2 = st.columns(2)
            if d1.button("🔥 はい、すべて削除", key="conf_frozen_bulk_y"):
                for _, row in df_display.iterrows():
                    perform_delete_account(row['screen_name'])
                st.session_state.confirm_frozen_bulk_del = False
                st.cache_data.clear(); st.rerun()
            if d2.button("いいえ", key="conf_frozen_bulk_n"):
                st.session_state.confirm_frozen_bulk_del = False
                st.rerun()
        
        st.markdown("---")
        columns_per_row = 4
        account_list = df_display.to_dict('records')
        for i in range(0, len(account_list), columns_per_row):
            cols = st.columns(columns_per_row)
            for j in range(columns_per_row):
                if i + j < len(account_list):
                    acc = account_list[i + j]
                    name = acc.get('screen_name', 'Unknown')
                    disp = acc.get("assigned_name", "") or name
                    reason_html = ''
                    with cols[j]:
                        icon_path = os.path.join('data/icons', f"{name}.jpg")
                        b64_icon = get_base64_image(icon_path)
                        icon_html = f'<img src="data:image/jpeg;base64,{b64_icon}" style="width: 70px; height: 70px; border-radius: 50%; border: 2px solid #e74c3c; object-fit: cover; margin-bottom: 10px;">' if b64_icon else '<div style="font-size: 2.5rem; margin-bottom: 10px;">👤</div>'
                        st.markdown(f'<div style="text-align:center;">{icon_html}<div style="color:#e74c3c;font-weight:900;">{disp}</div><div>@{name}</div>{reason_html}</div>', unsafe_allow_html=True)
                        
                        bt1, bt2, bt3 = st.columns(3)
                        if bt1.button("✅", key=f"frozen_cl_{name}", help="解除"):
                            db.update_sync_status(name, "")
                            if os.path.exists('data/task_progress.json'):
                                try:
                                    with open('data/task_progress.json', 'r', encoding='utf-8') as f: p_data = json.load(f)
                                    p_data['fail_list'] = [i for i in p_data.get('fail_list', []) if i['name'] != name]
                                    with open('data/task_progress.json', 'w', encoding='utf-8') as f: json.dump(p_data, f, ensure_ascii=False)
                                except: pass
                            st.cache_data.clear(); st.rerun()
                        if bt2.button("✏️", key=f"frozen_ed_{name}", help="編集"):
                            st.session_state.editing_account = name; st.rerun()
                        if bt3.button("🗑️", key=f"frozen_del_{name}", help="削除"):
                            st.session_state[f"confirm_del_frozen_{name}"] = True
                        
                        if st.session_state.get(f"confirm_del_frozen_{name}"):
                            st.error(f"削除しますか？")
                            cd1, cd2 = st.columns(2)
                            if cd1.button("はい", key=f"conf_y_frozen_{name}"):
                                perform_delete_account(name)
                                del st.session_state[f"confirm_del_frozen_{name}"]
                                st.cache_data.clear(); st.rerun()
                            if cd2.button("いいえ", key=f"conf_n_frozen_{name}"):
                                del st.session_state[f"confirm_del_frozen_{name}"]
                                st.rerun()
    
elif page == "実行失敗":
    st.markdown("<h2 class='glow-text'>実行失敗一覧</h2>", unsafe_allow_html=True)
    db = DBManager()
    df_all = load_accounts()
    progress_data = {}; 
    if os.path.exists('data/task_progress.json'): 
        try: 
            with open('data/task_progress.json', 'r', encoding='utf-8') as f: progress_data = json.load(f) 
        except: pass 
    fail_list = progress_data.get('fail_list', []); 
    reason_map = {item['name']: item.get('reason', '原因不明') for item in fail_list}; 
    fail_names = list(reason_map.keys()); 
    df_display = df_all[df_all['screen_name'].isin(fail_names) | df_all['sync_status'].str.contains('失敗|エラー|Error', na=False)]
    st.markdown(f"**実行失敗アカウント: {len(df_display)} 件**")
    
    # 0件でも更新ボタンを常に表示
    col_ref1, col_ref2 = st.columns([5, 1])
    if col_ref2.button("🔄 更新", key="exec_fail_ref_always"):
        st.cache_data.clear(); st.rerun()

    if df_display.empty:
        st.success("該当するアカウントはありません。")
    else:
        col_act1, col_act2, col_act3 = st.columns(3)
        if col_act1.button("📊 出力", key="fail_exp"): 
            subprocess.run([sys.executable, 'export_login_failures.py', '--type', 'fail'])
            st.success("完了")
        if col_act2.button("🧹 一括解除", key="fail_clr"):
            db.bulk_clear_sync_status('失敗')
            if os.path.exists('data/task_progress.json'):
                try:
                    with open('data/task_progress.json', 'r', encoding='utf-8') as f: p_data = json.load(f)
                    p_data['fail'] = 0; p_data['fail_list'] = []
                    with open('data/task_progress.json', 'w', encoding='utf-8') as f: json.dump(p_data, f, ensure_ascii=False)
                except: pass
            st.cache_data.clear(); st.rerun()
        if col_act3.button("🗑️ 一括削除", key="exec_fail_bulk_del"):
            st.session_state.confirm_exec_fail_bulk_del = True

        if st.session_state.get('confirm_exec_fail_bulk_del'):
            st.error(f"⚠️ 実行失敗アカウント {len(df_display)} 件をすべて削除しますか？")
            d1, d2 = st.columns(2)
            if d1.button("🔥 はい、すべて削除", key="conf_exec_fail_bulk_y"):
                for _, row in df_display.iterrows():
                    perform_delete_account(row['screen_name'])
                st.session_state.confirm_exec_fail_bulk_del = False
                st.cache_data.clear(); st.rerun()
            if d2.button("いいえ", key="conf_exec_fail_bulk_n"):
                st.session_state.confirm_exec_fail_bulk_del = False
                st.rerun()
        
        st.markdown("---")
        columns_per_row = 4
        account_list = df_display.to_dict('records')
        for i in range(0, len(account_list), columns_per_row):
            cols = st.columns(columns_per_row)
            for j in range(columns_per_row):
                if i + j < len(account_list):
                    acc = account_list[i + j]
                    name = acc.get('screen_name', 'Unknown')
                    disp = acc.get("assigned_name", "") or name
                    reason_html = ''
                    with cols[j]:
                        icon_path = os.path.join('data/icons', f"{name}.jpg")
                        b64_icon = get_base64_image(icon_path)
                        icon_html = f'<img src="data:image/jpeg;base64,{b64_icon}" style="width: 70px; height: 70px; border-radius: 50%; border: 2px solid #e74c3c; object-fit: cover; margin-bottom: 10px;">' if b64_icon else '<div style="font-size: 2.5rem; margin-bottom: 10px;">👤</div>'
                        st.markdown(f'<div style="text-align:center;">{icon_html}<div style="color:#e74c3c;font-weight:900;">{disp}</div><div>@{name}</div>{reason_html}</div>', unsafe_allow_html=True)
                        
                        bt1, bt2, bt3 = st.columns(3)
                        if bt1.button("✅", key=f"fail_cl_{name}", help="解除"):
                            db.update_sync_status(name, "")
                            if os.path.exists('data/task_progress.json'):
                                try:
                                    with open('data/task_progress.json', 'r', encoding='utf-8') as f: p_data = json.load(f)
                                    p_data['fail_list'] = [i for i in p_data.get('fail_list', []) if i['name'] != name]
                                    with open('data/task_progress.json', 'w', encoding='utf-8') as f: json.dump(p_data, f, ensure_ascii=False)
                                except: pass
                            st.cache_data.clear(); st.rerun()
                        if bt2.button("✏️", key=f"fail_ed_{name}", help="編集"):
                            st.session_state.editing_account = name; st.rerun()
                        if bt3.button("🗑️", key=f"fail_del_{name}", help="削除"):
                            st.session_state[f"confirm_del_fail_{name}"] = True
                        
                        if st.session_state.get(f"confirm_del_fail_{name}"):
                            st.error(f"削除しますか？")
                            cd1, cd2 = st.columns(2)
                            if cd1.button("はい", key=f"conf_y_fail_{name}"):
                                perform_delete_account(name)
                                del st.session_state[f"confirm_del_fail_{name}"]
                                st.cache_data.clear(); st.rerun()
                            if cd2.button("いいえ", key=f"conf_n_fail_{name}"):
                                del st.session_state[f"confirm_del_fail_{name}"]
                                st.rerun()
    
elif page == "ログイン失敗":
    st.markdown("<h2 class='glow-text'>ログイン失敗一覧</h2>", unsafe_allow_html=True)
    db = DBManager()
    df_all = load_accounts()
    df_display = df_all[df_all['sync_status'] == 'ログイン失敗']
    st.markdown(f"**ログイン失敗アカウント: {len(df_display)} 件**")
    
    # 0件でも更新ボタンを常に表示
    col_ref1, col_ref2 = st.columns([5, 1])
    if col_ref2.button("🔄 更新", key="login_fail_ref_always"):
        st.cache_data.clear(); st.rerun()

    if df_display.empty:
        st.success("該当するアカウントはありません。")
    else:
        col_act1, col_act2, col_act3, col_act4 = st.columns(4)
        if col_act1.button("📊 出力", key="login_fail_exp"): 
            subprocess.run([sys.executable, 'export_login_failures.py', '--type', 'login_fail'])
            st.success("完了")
        if col_act2.button("🧹 一括解除", key="login_fail_clr"):
            db.bulk_clear_sync_status('ログイン失敗')
            if os.path.exists('data/task_progress.json'):
                try:
                    with open('data/task_progress.json', 'r', encoding='utf-8') as f: p_data = json.load(f)
                    p_data['fail'] = 0; p_data['fail_list'] = []
                    with open('data/task_progress.json', 'w', encoding='utf-8') as f: json.dump(p_data, f, ensure_ascii=False)
                except: pass
            st.cache_data.clear(); st.rerun()
        if col_act3.button("🚀 一括再ログイン実行", key="login_fail_bulk_retry", type="primary"):
            cmd = [sys.executable, 'bulk_login.py']
            subprocess.Popen(['cmd', '/k'] + cmd if sys.platform == 'win32' else cmd)
            st.info("一括再ログインを開始しました。別ウィンドウで進行します。")
        if col_act4.button("🗑️ 一括削除", key="login_fail_bulk_del"):
            st.session_state.confirm_login_fail_bulk_del = True

        if st.session_state.get('confirm_login_fail_bulk_del'):
            st.error(f"⚠️ ログイン失敗アカウント {len(df_display)} 件をすべて削除しますか？")
            d1, d2 = st.columns(2)
            if d1.button("🔥 はい、すべて削除", key="conf_login_fail_bulk_y"):
                for _, row in df_display.iterrows():
                    perform_delete_account(row['screen_name'])
                st.session_state.confirm_login_fail_bulk_del = False
                st.cache_data.clear(); st.rerun()
            if d2.button("いいえ", key="conf_login_fail_bulk_n"):
                st.session_state.confirm_login_fail_bulk_del = False
                st.rerun()
        
        st.markdown("---")
        columns_per_row = 4
        account_list = df_display.to_dict('records')
        for i in range(0, len(account_list), columns_per_row):
            cols = st.columns(columns_per_row)
            for j in range(columns_per_row):
                if i + j < len(account_list):
                    acc = account_list[i + j]
                    name = acc.get('screen_name', 'Unknown')
                    disp = acc.get("assigned_name", "") or name
                    reason_html = ''
                    with cols[j]:
                        icon_path = os.path.join('data/icons', f"{name}.jpg")
                        b64_icon = get_base64_image(icon_path)
                        icon_html = f'<img src="data:image/jpeg;base64,{b64_icon}" style="width: 70px; height: 70px; border-radius: 50%; border: 2px solid #f39c12; object-fit: cover; margin-bottom: 10px;">' if b64_icon else '<div style="font-size: 2.5rem; margin-bottom: 10px;">👤</div>'
                        st.markdown(f'<div style="text-align:center;">{icon_html}<div style="color:#f39c12;font-weight:900;">{disp}</div><div>@{name}</div>{reason_html}</div>', unsafe_allow_html=True)
                        
                        bt1, bt2, bt3, bt4 = st.columns(4)
                        if bt1.button("✅", key=f"login_fail_cl_{name}", help="解除"):
                            db.update_sync_status(name, "")
                            if os.path.exists('data/task_progress.json'):
                                try:
                                    with open('data/task_progress.json', 'r', encoding='utf-8') as f: p_data = json.load(f)
                                    p_data['fail_list'] = [i for i in p_data.get('fail_list', []) if i['name'] != name]
                                    with open('data/task_progress.json', 'w', encoding='utf-8') as f: json.dump(p_data, f, ensure_ascii=False)
                                except: pass
                            st.cache_data.clear(); st.rerun()
                        if bt2.button("🔑", key=f"login_fail_retry_{name}", help="個別ログイン試行"):
                            pw = acc.get('password', '')
                            email = acc.get('email', '')
                            if pw:
                                cmd = [sys.executable, 'account_manager.py', name, pw, '--rotate-ip']
                                if email: cmd += ['--email', email]
                                subprocess.Popen(['cmd', '/k'] + cmd if sys.platform == 'win32' else cmd)
                                st.info(f"@{name} のログイン試行（IP変更あり）を開始しました。")
                            else:
                                st.error("パスワードが設定されていません。")
                        if bt3.button("✏️", key=f"login_fail_ed_{name}", help="編集"):
                            st.session_state.editing_account = name; st.rerun()
                        if bt4.button("🗑️", key=f"login_fail_del_{name}", help="削除"):
                            st.session_state[f"confirm_del_login_fail_{name}"] = True
                        
                        if st.session_state.get(f"confirm_del_login_fail_{name}"):
                            st.error(f"削除しますか？")
                            cd1, cd2 = st.columns(2)
                            if cd1.button("はい", key=f"conf_y_login_fail_{name}"):
                                perform_delete_account(name)
                                del st.session_state[f"confirm_del_login_fail_{name}"]
                                st.cache_data.clear(); st.rerun()
                            if cd2.button("いいえ", key=f"conf_n_login_fail_{name}"):
                                del st.session_state[f"confirm_del_login_fail_{name}"]
                                st.rerun()
    
elif page == "ロック":
    st.markdown("<h2 class='glow-text'>ロック一覧</h2>", unsafe_allow_html=True)
    db = DBManager()
    df_all = load_accounts()
    df_display = df_all[df_all['sync_status'].str.contains('ロック', na=False)]
    st.markdown(f"**ロックアカウント: {len(df_display)} 件**")
    
    # 0件でも更新ボタンを常に表示
    col_ref1, col_ref2 = st.columns([5, 1])
    if col_ref2.button("🔄 更新", key="lock_ref_always"):
        st.cache_data.clear(); st.rerun()

    if df_display.empty:
        st.success("該当するアカウントはありません。")
    else:
        col_act1, col_act2, col_act3 = st.columns(3)
        if col_act1.button("📊 出力", key="lock_exp"): 
            subprocess.run([sys.executable, 'export_login_failures.py', '--type', 'lock'])
            st.success("完了")
        if col_act2.button("🧹 一括解除", key="lock_clr"):
            db.bulk_clear_sync_status('ロック')
            if os.path.exists('data/task_progress.json'):
                try:
                    with open('data/task_progress.json', 'r', encoding='utf-8') as f: p_data = json.load(f)
                    p_data['fail'] = 0; p_data['fail_list'] = []
                    with open('data/task_progress.json', 'w', encoding='utf-8') as f: json.dump(p_data, f, ensure_ascii=False)
                except: pass
            st.cache_data.clear(); st.rerun()
        if col_act3.button("🗑️ 一括削除", key="lock_bulk_del"):
            st.session_state.confirm_lock_bulk_del = True

        if st.session_state.get('confirm_lock_bulk_del'):
            st.error(f"⚠️ ロック中アカウント {len(df_display)} 件をすべて削除しますか？")
            d1, d2 = st.columns(2)
            if d1.button("🔥 はい、すべて削除", key="conf_lock_bulk_y"):
                for _, row in df_display.iterrows():
                    perform_delete_account(row['screen_name'])
                st.session_state.confirm_lock_bulk_del = False
                st.cache_data.clear(); st.rerun()
            if d2.button("いいえ", key="conf_lock_bulk_n"):
                st.session_state.confirm_lock_bulk_del = False
                st.rerun()
        
        st.markdown("---")
        columns_per_row = 4
        account_list = df_display.to_dict('records')
        for i in range(0, len(account_list), columns_per_row):
            cols = st.columns(columns_per_row)
            for j in range(columns_per_row):
                if i + j < len(account_list):
                    acc = account_list[i + j]
                    name = acc.get('screen_name', 'Unknown')
                    disp = acc.get("assigned_name", "") or name
                    reason_html = ''
                    with cols[j]:
                        icon_path = os.path.join('data/icons', f"{name}.jpg")
                        b64_icon = get_base64_image(icon_path)
                        icon_html = f'<img src="data:image/jpeg;base64,{b64_icon}" style="width: 70px; height: 70px; border-radius: 50%; border: 2px solid #f39c12; object-fit: cover; margin-bottom: 10px;">' if b64_icon else '<div style="font-size: 2.5rem; margin-bottom: 10px;">👤</div>'
                        st.markdown(f'<div style="text-align:center;">{icon_html}<div style="color:#f39c12;font-weight:900;">{disp}</div><div>@{name}</div>{reason_html}</div>', unsafe_allow_html=True)
                        
                        bt1, bt2, bt3 = st.columns(3)
                        if bt1.button("✅", key=f"lock_cl_{name}", help="解除"):
                            db.update_sync_status(name, "")
                            if os.path.exists('data/task_progress.json'):
                                try:
                                    with open('data/task_progress.json', 'r', encoding='utf-8') as f: p_data = json.load(f)
                                    p_data['fail_list'] = [i for i in p_data.get('fail_list', []) if i['name'] != name]
                                    with open('data/task_progress.json', 'w', encoding='utf-8') as f: json.dump(p_data, f, ensure_ascii=False)
                                except: pass
                            st.cache_data.clear(); st.rerun()
                        if bt2.button("✏️", key=f"lock_ed_{name}", help="編集"):
                            st.session_state.editing_account = name; st.rerun()
                        if bt3.button("🗑️", key=f"lock_del_{name}", help="削除"):
                            st.session_state[f"confirm_del_lock_{name}"] = True
                        
                        if st.session_state.get(f"confirm_del_lock_{name}"):
                            st.error(f"削除しますか？")
                            cd1, cd2 = st.columns(2)
                            if cd1.button("はい", key=f"conf_y_lock_{name}"):
                                perform_delete_account(name)
                                del st.session_state[f"confirm_del_lock_{name}"]
                                st.cache_data.clear(); st.rerun()
                            if cd2.button("いいえ", key=f"conf_n_lock_{name}"):
                                del st.session_state[f"confirm_del_lock_{name}"]
                                st.rerun()


