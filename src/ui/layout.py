from typing import Any

import streamlit as st

from ui.pages import consistency, integrity, log_in
from ui.utils import _config_page


def main() -> None:
    pages: list[Any]

    if not st.session_state.get("is_connected", False):
        pages = [st.Page(**_config_page(log_in.render))]
    else:
        pages = [
            st.Page(**_config_page(log_in.render)),
            st.Page(**_config_page(consistency.render)),
            st.Page(**_config_page(integrity.render)),
        ]

    pg = st.navigation(pages)
    pg.run()
