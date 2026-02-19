import streamlit as st

from ui.pages import consistency, home
from ui.utils import _config_page


def main():
    pages = [
        st.Page(**_config_page(home.render)),
        st.Page(**_config_page(consistency.render)),
    ]

    pg = st.navigation(pages)
    pg.run()

    # page = st.sidebar.selectbox("Navigation", list(PAGES.keys()))
    # PAGES[page]()
