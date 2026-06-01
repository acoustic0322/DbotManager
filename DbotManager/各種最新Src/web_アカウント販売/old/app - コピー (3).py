import streamlit as st
import pandas as pd

# =========================================================
# PAGE CONFIG
# =========================================================

st.set_page_config(
    page_title="D-BOT",
    page_icon="🤖",
    layout="wide"
)

# =========================================================
# CSS
# =========================================================

st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

html, body, [data-testid="stApp"] {
    font-family: 'Outfit', sans-serif;
}

/* Main Background */
.main {
    background: #ffffff;
}

/* Sidebar */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #141721 0%, #0e1117 100%);
    border-right: 1px solid rgba(255,255,255,0.05);
}

[data-testid="stSidebar"] * {
    color: white !important;
}

/* Glow Text */
.glow-text {
    color: white;
    text-shadow: 0 0 10px rgba(168,85,247,0.5);
}

/* Gold Line */
.gold-line {
    height: 1px;
    width: 500px;
    background: #D4AF37;
    margin: 0.3rem 0 1.5rem 0;
    box-shadow: 0 1px 4px rgba(212,175,55,0.3);
}

/* Buttons */
.stButton > button {
    background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
    color: white !important;
    border: none;
    border-radius: 10px;
    padding: 0.7rem 1.5rem;
    font-weight: 600;
}

.stButton > button:hover {
    transform: translateY(-2px);
    box-shadow: 0 4px 15px rgba(168,85,247,0.4);
}

/* Account Card */
.account-card {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 15px;
    text-align: center;
    margin-bottom: 15px;
    transition: 0.3s;
}

.account-card:hover {
    transform: translateY(-3px);
    box-shadow: 0 8px 20px rgba(0,0,0,0.08);
}

/* Search */
.stTextInput input {
    border-radius: 10px;
}

/* Metric Box */
.metric-box {
    background: white;
    border: 1px solid #e5e7eb;
    border-radius: 12px;
    padding: 20px;
}

.metric-title {
    color: #888;
    font-size: 0.9rem;
}

.metric-value {
    color: #111;
    font-size: 2rem;
    font-weight: 700;
    margin-top: 8px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("""
    <h1 class='glow-text'
    style='text-align:center;
           font-size:2.2rem;'>
    D-BOT
    </h1>
    """, unsafe_allow_html=True)

    st.markdown("""
    <p style='text-align:center;
              color:#888;
              font-size:0.8rem;
              margin-top:-15px;'>
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
    },
    {
        "name": "Mika",
        "id": "@mika",
        "status": "ACTIVE",
        "followers": 5220
    },
    {
        "name": "Taro",
        "id": "@taro",
        "status": "ACTIVE",
        "followers": 740
    }
])

# =========================================================
# PAGE : ACCOUNT
# =========================================================

if page == "アカウント管理":

    st.markdown("""
    <h1 style='font-size:3rem;
               font-weight:700;
               margin-bottom:0;'>
    アカウント管理
    </h1>

    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    st.markdown("### アカウント検索")

    search = st.text_input(
        "",
        placeholder="IDで絞り込み..."
    )

    st.markdown("""
    <div style='background:#eef4ff;
                padding:15px;
                border-radius:10px;
                margin-bottom:20px;'>

    📁 表示中のグループ : すべて

    </div>
    """, unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)

    with col1:
        st.button("全て選択", use_container_width=True)

    with col2:
        st.button("選択解除", use_container_width=True)

    with col3:
        st.button("未分類のみ選択", use_container_width=True)

    st.markdown("<br>", unsafe_allow_html=True)

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

            status_color = "#2ecc71"

            if row["status"] == "SUSPENDED":
                status_color = "#e74c3c"

            elif row["status"] == "PENDING":
                status_color = "#f1c40f"

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

                <div style='color:#888;
                            margin-top:5px;'>

                {row['id']}

                </div>

                <div style='margin-top:12px;
                            color:{status_color};
                            font-weight:700;'>

                ● {row['status']}

                </div>

                <div style='margin-top:12px;
                            color:#111;'>

                👥 {row['followers']}

                </div>

            </div>
            """, unsafe_allow_html=True)

# =========================================================
# PAGE : DASHBOARD
# =========================================================

elif page == "選手権":

    st.title("選手権")

    c1, c2, c3, c4 = st.columns(4)

    metrics = [
        ("Accounts", "128"),
        ("Active", "95"),
        ("Replies", "12,480"),
        ("Errors", "4")
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

# =========================================================
# PAGE : ANALYTICS
# =========================================================

elif page == "分析":

    st.title("分析")

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

# =========================================================
# PAGE : SETTINGS
# =========================================================

elif page == "設定":

    st.title("設定")

    st.toggle("通知", value=True)

    st.toggle("ダークモード", value=True)

    st.selectbox(
        "Language",
        [
            "Japanese",
            "English"
        ]
    )

    if st.button("保存"):
        st.success("保存しました")