import streamlit as st
import pandas as pd
import random

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="D-BOT",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# ORIGINAL DESIGN (ほぼそのまま)
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

html, body, [data-testid="stApp"] {
    font-family: 'Outfit', sans-serif;
    background: #0e1117;
    color: white;
}

/* Main */
.main {
    background: #0e1117;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141721 0%, #0e1117 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

/* Sidebar text */
[data-testid="stSidebar"] * {
    color: white !important;
}

/* Gold Line */
.gold-line {
    height: 1px;
    width: 500px;
    background: #D4AF37;
    margin: 0.3rem 0 1.5rem 0;
    box-shadow: 0 1px 4px rgba(212,175,55,0.3);
}

/* Glow */
.glow-text {
    color: white;
    text-shadow: 0 0 10px rgba(168,85,247,0.5);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    color: white !important;
    border: none;
    border-radius: 12px;
    padding: 0.8rem 2rem;
    font-weight: 600;
    transition: all 0.3s ease;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(168,85,247,0.4);
}

/* Cards */
.account-card {
    background: rgba(255,255,255,0.05);
    border: 1px solid rgba(212,175,55,0.2);
    border-radius: 16px;
    padding: 20px;
    transition: 0.3s;
    text-align: center;
    margin-bottom: 20px;
}

.account-card:hover {
    transform: translateY(-4px);
    border-color: rgba(212,175,55,0.8);
    box-shadow: 0 8px 20px rgba(212,175,55,0.2);
}

/* Metric */
.metric-box {
    background: rgba(255,255,255,0.04);
    border: 1px solid rgba(255,255,255,0.06);
    border-radius: 14px;
    padding: 25px;
}

.metric-title {
    color: #999;
    font-size: 0.9rem;
}

.metric-value {
    color: white;
    font-size: 2rem;
    font-weight: 700;
    margin-top: 10px;
}

/* Inputs */
.stTextInput input {
    background: rgba(255,255,255,0.05);
    color: white;
    border-radius: 10px;
}

/* Table */
[data-testid="stDataFrame"] {
    border: 1px solid rgba(255,255,255,0.05);
    border-radius: 15px;
    overflow: hidden;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <h1 class='glow-text'
    style='text-align:center;font-size:2.2rem;'>
    D-BOT
    </h1>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align:center;color:#888;font-size:0.8rem;margin-top:-15px;'>
    System v2.1.1 Stable
    </p>
    """, unsafe_allow_html=True)

    page = st.radio(
        "MENU",
        [
            "選手権",
            "アカウント管理",
            "分析",
            "設定"
        ]
    )

# =========================================================
# DUMMY DATA
# =========================================================

accounts = pd.DataFrame([
    {
        "name": "Alice",
        "id": "@alice",
        "status": "ACTIVE",
        "followers": 1280
    },
    {
        "name": "Bob",
        "id": "@bob",
        "status": "SUSPENDED",
        "followers": 350
    },
    {
        "name": "Charlie",
        "id": "@charlie",
        "status": "ACTIVE",
        "followers": 8200
    },
    {
        "name": "Emma",
        "id": "@emma",
        "status": "PENDING",
        "followers": 980
    }
])

# =========================================================
# PAGE : DASHBOARD
# =========================================================

if page == "選手権":

    st.markdown("""
    <h2 class='glow-text'
    style='margin-bottom:0;'>
    選手権
    </h2>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    # KPI
    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("👥 Accounts", "128"),
        ("🚀 Active", "95"),
        ("💬 Replies", "12,480"),
        ("⚠️ Errors", "4")
    ]

    for col, metric in zip([c1,c2,c3,c4], metrics):

        with col:
            st.markdown(f"""
            <div class='metric-box'>
                <div class='metric-title'>
                {metric[0]}
                </div>

                <div class='metric-value'>
                {metric[1]}
                </div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("## 実行設定")

    col1, col2 = st.columns(2)

    target = col1.text_input(
        "応援対象ID",
        placeholder="@target"
    )

    keyword = col2.text_input(
        "検索キーワード",
        placeholder="keyword"
    )

    st.markdown("### 詳細パラメータ")

    p1, p2, p3 = st.columns(3)

    like_count = p1.number_input("いいね", 0, 999, 50)
    rt_count = p2.number_input("RT", 0, 999, 20)
    reply_count = p3.number_input("Reply", 0, 999, 10)

    st.button("🚀 実行")

# =========================================================
# PAGE : ACCOUNT
# =========================================================

elif page == "アカウント管理":

    st.markdown("""
    <h2 class='glow-text'
    style='margin-bottom:0;'>
    アカウント管理
    </h2>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    search = st.text_input(
        "🔍 アカウント検索"
    )

    filtered = accounts.copy()

    if search:
        filtered = filtered[
            filtered["name"].str.contains(
                search,
                case=False
            )
        ]

    cols = st.columns(4)

    for idx, row in filtered.iterrows():

        with cols[idx % 4]:

            color = "#2ecc71"

            if row["status"] == "SUSPENDED":
                color = "#e74c3c"

            elif row["status"] == "PENDING":
                color = "#f1c40f"

            st.markdown(f"""
            <div class='account-card'>

                <div style='font-size:60px;'>
                👤
                </div>

                <div style='font-size:1.2rem;
                            font-weight:700;
                            color:#D4AF37;
                            margin-top:10px;'>

                {row['name']}

                </div>

                <div style='color:#aaa;margin-top:5px;'>
                {row['id']}
                </div>

                <div style='margin-top:10px;
                            color:{color};
                            font-weight:700;'>

                ● {row['status']}

                </div>

                <div style='margin-top:10px;
                            color:white;'>

                👥 {row['followers']}

                </div>

            </div>
            """, unsafe_allow_html=True)

# =========================================================
# PAGE : ANALYTICS
# =========================================================

elif page == "分析":

    st.markdown("""
    <h2 class='glow-text'
    style='margin-bottom:0;'>
    分析
    </h2>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    chart_df = pd.DataFrame({
        "DAY": [
            "MON","TUE","WED",
            "THU","FRI","SAT","SUN"
        ],
        "VALUE": [
            120,
            180,
            150,
            300,
            250,
            400,
            380
        ]
    })

    st.line_chart(
        chart_df.set_index("DAY")
    )

    st.markdown("## Conversion")

    progress = random.randint(60, 95)

    st.progress(progress / 100)

    st.markdown(f"""
    <div style='margin-top:10px;color:#D4AF37;'>
    {progress}% Complete
    </div>
    """, unsafe_allow_html=True)

# =========================================================
# PAGE : SETTINGS
# =========================================================

elif page == "設定":

    st.markdown("""
    <h2 class='glow-text'
    style='margin-bottom:0;'>
    設定
    </h2>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    st.toggle("通知を有効化", value=True)

    st.toggle("ダークモード", value=True)

    st.selectbox(
        "Language",
        [
            "Japanese",
            "English"
        ]
    )

    st.slider(
        "AI Creativity",
        0,
        100,
        70
    )

    if st.button("💾 保存"):
        st.success("保存しました")