import streamlit as st

from data.dummy_data import accounts
from components.account_card import render_account_card

def render_account_manage():

    st.markdown("""
    <h1>アカウント管理</h1>
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

            render_account_card(row)