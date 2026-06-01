import os
import base64

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

    if pd.isna(price):
        price = 0

    price = int(price)

    # =====================================================
    # アイコン画像
    # img/(ID).jpg を参照
    # =====================================================

    account_id = row.get("id", 0)

    image_path = f"img/icon/{row['id']}.jpg"

    icon_html = """
    <div style="font-size:60px;">
    👤
    </div>
    """

    if os.path.exists(image_path):

        with open(image_path, "rb") as f:

            image_base64 = base64.b64encode(
                f.read()
            ).decode()

        icon_html = f"""
        <img src="data:image/jpeg;base64,{image_base64}"
             style="
                width:80px;
                height:80px;
                border-radius:50%;
                object-fit:cover;
                border:3px solid #eee;
             ">
        """

    # =====================================================
    # CARD HTML
    # =====================================================

    card_html = f"""
    <div style="
        background:white;
        border:1px solid #e5e7eb;
        border-radius:12px;
        padding:20px;
        text-align:center;
        height:360px;
    ">

        {icon_html}

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
        {row['id_text']}
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
        height=380
    )