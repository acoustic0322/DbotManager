import streamlit as st

def load_css():

    st.markdown("""
    <style>

    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;600&display=swap');

    html, body, [data-testid="stApp"] {
        font-family: 'Outfit', sans-serif;
    }

    .main {
        background: #ffffff;
    }

    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #141721 0%, #0e1117 100%);
        border-right: 1px solid rgba(255,255,255,0.05);
    }

    [data-testid="stSidebar"] * {
        color: white !important;
    }

    .gold-line {
        height: 1px;
        width: 500px;
        background: #D4AF37;
        margin: 0.3rem 0 1.5rem 0;
        box-shadow: 0 1px 4px rgba(212,175,55,0.3);
    }

    .glow-text {
        color: white;
        text-shadow: 0 0 10px rgba(168,85,247,0.5);
    }

    .stButton > button {
        background: linear-gradient(135deg, #6366f1 0%, #a855f7 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.7rem 1.5rem;
        font-weight: 600;
    }

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