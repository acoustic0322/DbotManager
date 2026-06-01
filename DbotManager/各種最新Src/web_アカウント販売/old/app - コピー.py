import streamlit as st
import pandas as pd
import random

# =====================================================
# PAGE CONFIG
# =====================================================

st.set_page_config(
    page_title="Nebula Dashboard",
    page_icon="🚀",
    layout="wide"
)

# =====================================================
# DESIGN SYSTEM
# =====================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

html, body, [data-testid="stApp"] {
    background: #0e1117;
    color: white;
    font-family: 'Outfit', sans-serif;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141721 0%, #0e1117 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Titles */
.glow-text {
    color: white;
    text-shadow: 0 0 12px rgba(168, 85, 247, 0.6);
}

/* Gold line */
.gold-line {
    height: 1px;
    width: 100%;
    background: #D4AF37;
    margin-top: -10px;
    margin-bottom: 25px;
    box-shadow: 0 0 10px rgba(212,175,55,0.3);
}

/* Cards */
.metric-card {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(212,175,55,0.15);
    border-radius: 18px;
    padding: 25px;
    transition: 0.3s;
}

.metric-card:hover {
    transform: translateY(-4px);
    border-color: rgba(212,175,55,0.5);
    box-shadow: 0 10px 25px rgba(0,0,0,0.4);
}

.metric-title {
    color: #999;
    font-size: 0.9rem;
    margin-bottom: 10px;
}

.metric-value {
    color: white;
    font-size: 2rem;
    font-weight: 700;
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    color: white;
    border: none;
    border-radius: 12px;
    padding: 12px 24px;
    font-weight: 600;
    transition: 0.3s;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 5px 15px rgba(168,85,247,0.4);
}

/* Table */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 15px;
    overflow: hidden;
}

/* Inputs */
.stTextInput input {
    background: rgba(255,255,255,0.05);
    color: white;
    border-radius: 10px;
}

/* Sidebar Buttons */
[data-testid="stSidebar"] .stButton > button {
    width: 100%;
}

</style>
""", unsafe_allow_html=True)

# =====================================================
# SIDEBAR
# =====================================================

with st.sidebar:

    st.markdown("""
    <h1 class='glow-text' style='text-align:center;'>
    🚀 NEBULA
    </h1>
    """, unsafe_allow_html=True)

    st.caption("SaaS Dashboard Template")

    page = st.radio(
        "MENU",
        [
            "Dashboard",
            "Users",
            "Analytics",
            "Settings"
        ]
    )

# =====================================================
# DUMMY DATA
# =====================================================

users = pd.DataFrame({
    "Name": ["Alice", "Bob", "Charlie", "David", "Emma"],
    "Plan": ["Pro", "Free", "Business", "Pro", "Free"],
    "Status": ["Active", "Active", "Suspended", "Active", "Pending"],
    "Revenue": [1200, 0, 8500, 2200, 0]
})

# =====================================================
# DASHBOARD
# =====================================================

if page == "Dashboard":

    st.markdown("""
    <h1 class='glow-text'>
    Dashboard
    </h1>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    col1, col2, col3, col4 = st.columns(4)

    cards = [
        ("💰 Revenue", "$12,480"),
        ("👥 Users", "1,284"),
        ("🚀 Active", "932"),
        ("⚠️ Errors", "12")
    ]

    for col, card in zip([col1,col2,col3,col4], cards):

        with col:
            st.markdown(f"""
            <div class='metric-card'>
                <div class='metric-title'>{card[0]}</div>
                <div class='metric-value'>{card[1]}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("## Recent Activity")

    activity_df = pd.DataFrame({
        "Time": ["10:22", "10:25", "10:28", "10:30"],
        "User": ["Alice", "Bob", "Charlie", "Emma"],
        "Action": [
            "Created Project",
            "Upgraded Plan",
            "Login Failed",
            "Uploaded File"
        ]
    })

    st.dataframe(activity_df, use_container_width=True)

# =====================================================
# USERS
# =====================================================

elif page == "Users":

    st.markdown("""
    <h1 class='glow-text'>
    User Management
    </h1>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    search = st.text_input("🔍 Search User")

    filtered = users.copy()

    if search:
        filtered = filtered[
            filtered["Name"].str.contains(search, case=False)
        ]

    st.dataframe(filtered, use_container_width=True)

    st.markdown("## User Cards")

    cols = st.columns(3)

    for idx, row in users.iterrows():

        with cols[idx % 3]:

            color = "#2ecc71"

            if row["Status"] == "Suspended":
                color = "#e74c3c"

            elif row["Status"] == "Pending":
                color = "#f1c40f"

            st.markdown(f"""
            <div class='metric-card'>
                <h3>{row['Name']}</h3>
                <p>📦 {row['Plan']}</p>
                <p style='color:{color};'>
                ● {row['Status']}
                </p>
                <p>💰 ${row['Revenue']}</p>
            </div>
            """, unsafe_allow_html=True)

# =====================================================
# ANALYTICS
# =====================================================

elif page == "Analytics":

    st.markdown("""
    <h1 class='glow-text'>
    Analytics
    </h1>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    chart_df = pd.DataFrame({
        "Day": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"],
        "Sales": [120, 200, 150, 300, 280, 400, 350]
    })

    st.line_chart(chart_df.set_index("Day"))

    st.markdown("## Conversion Rate")

    progress = random.randint(50, 95)

    st.progress(progress / 100)

    st.markdown(f"""
    <div style='margin-top:10px; color:#D4AF37;'>
    Conversion Rate: {progress}%
    </div>
    """, unsafe_allow_html=True)

# =====================================================
# SETTINGS
# =====================================================

elif page == "Settings":

    st.markdown("""
    <h1 class='glow-text'>
    Settings
    </h1>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    st.toggle("Enable Notifications", value=True)

    st.toggle("Dark Mode", value=True)

    st.selectbox(
        "Language",
        ["Japanese", "English"]
    )

    st.slider(
        "AI Creativity",
        0,
        100,
        70
    )

    if st.button("💾 Save Settings"):
        st.success("Settings Saved")