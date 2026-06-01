import streamlit as st

from components.metric_card import render_metric_card

def render_dashboard():

    st.markdown("""
    <h1>選手権</h1>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    c1, c2, c3, c4 = st.columns(4)

    with c1:
        render_metric_card("Accounts", "128")

    with c2:
        render_metric_card("Active", "95")

    with c3:
        render_metric_card("Replies", "12,480")

    with c4:
        render_metric_card("Errors", "4")

    st.markdown("## 実行設定")

    col1, col2 = st.columns(2)

    col1.text_input(
        "応援対象ID",
        placeholder="@target"
    )

    col2.text_input(
        "検索キーワード",
        placeholder="keyword"
    )

    st.button("🚀 実行")