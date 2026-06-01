import streamlit as st

def render_settings():

    st.markdown("""
    <h1>設定</h1>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

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