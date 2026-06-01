import streamlit as st

def render_sidebar():

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

        st.markdown("### MENU")

        if "page" not in st.session_state:
            st.session_state.page = "カテゴリ1"

        menu_list = [
            "カテゴリ１",
            "カテゴリ２",
            "カテゴリ３",
            "カテゴリ４"
        ]

        for menu in menu_list:

            button_type = "secondary"

            if st.session_state.page == menu:
                button_type = "primary"

            if st.button(
                menu,
                use_container_width=True,
                type=button_type
            ):
                st.session_state.page = menu

    return st.session_state.page