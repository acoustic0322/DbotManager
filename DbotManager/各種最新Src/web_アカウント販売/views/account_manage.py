import streamlit as st

from database.account_repository import get_accounts
from components.account_card import render_account_card

def render_account_manage(user_name):

    st.markdown("""
    <h1>アカウント管理</h1>
    <div class='gold-line'></div>
    """, unsafe_allow_html=True)

    # DB取得
    accounts = get_accounts(user_name)

    search = st.text_input(
        "🔍 アカウント検索"
    )

    filtered = accounts.copy()

    if search:

        filtered = filtered[
            filtered["account_name"].str.contains(
                search,
                case=False,
                na=False
            )
        ]

    cols = st.columns(4)

    for idx, row in filtered.iterrows():

        with cols[idx % 4]:

            render_account_card({
                "id": row["id"],
                "name": row["name"],
                "id_text": row["id_text"],
                "status": row["status"],
                "followers_count": row["followers_count"]
            })