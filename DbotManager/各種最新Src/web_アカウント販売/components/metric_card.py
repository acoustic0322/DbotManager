import streamlit as st

def render_metric_card(title, value):

    st.markdown(f"""
    <div class='metric-box'>

        <div class='metric-title'>
        {title}
        </div>

        <div class='metric-value'>
        {value}
        </div>

    </div>
    """, unsafe_allow_html=True)