import streamlit as st

from styles.style import load_css
from components.sidebar import render_sidebar

from views.dashboard import render_dashboard
from views.account_manage import render_account_manage
from views.analytics import render_analytics
from views.settings import render_settings

# =========================================================
# CONFIG
# =========================================================

st.set_page_config(
    page_title="D-BOT",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# STYLE
# =========================================================

load_css()

# =========================================================
# SIDEBAR
# =========================================================

page = render_sidebar()

# =========================================================
# ROUTING
# =========================================================

if page == "カテゴリ１":
#    render_dashboard()
    render_account_manage("daisuke")

elif page == "カテゴリ２":
    render_account_manage("tomoya1")

elif page == "カテゴリ３":
#    render_analytics()
    render_account_manage("dd")

elif page == "カテゴリ４":
#    render_settings()
    render_account_manage("next")
