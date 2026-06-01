import streamlit.components.v1 as components

import pandas as pd

def render_account_card(row):

    status_color = "#2ecc71"

    if row["status"] == "SUSPENDED":
        status_color = "#e74c3c"

    elif row["status"] == "PENDING":
        status_color = "#f1c40f"

    # followers null対策
    followers = row.get("followers_count", 0)

    if pd.isna(followers):
        followers = 0

    followers = int(followers)

    # price null対策
    price = row.get("price", 0)

    if price is None:
        price = 0

    price = int(price)

    card_html = f"""
    <div style="
        background:white;
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:20px;
        text-align:center;
        height:320px;
    ">

        <div style="font-size:60px;">
        👤
        </div>

        <div style="
            font-size:1.2rem;
            font-weight:700;
            color:#D4AF37;
            margin-top:10px;
        ">
        {row['name']}
        </div>

        <div style="
            color:#888;
            margin-top:5px;
        ">
        {row['id']}
        </div>

        <div style="
            margin-top:12px;
            color:{status_color};
            font-weight:700;
        ">
        ● {row['status']}
        </div>

        <div style="
            margin-top:12px;
            color:#111;
            font-size:1.1rem;
        ">
        👥 {followers:,}
        </div>

        <div style="
            margin-top:12px;
            color:#6366f1;
            font-size:1.2rem;
            font-weight:700;
        ">
        ¥ {price:,}
        </div>

    </div>
    """

    components.html(
        card_html,
        height=340
    )