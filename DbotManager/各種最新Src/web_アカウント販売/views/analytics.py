import streamlit as st
import pandas as pd

def render_analytics():

    st.markdown("""
    <h1>分析</h1>
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