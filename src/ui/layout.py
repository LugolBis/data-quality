from typing import Any

import streamlit as st

from ui.pages import (
    consistency,
    integrity,
    lisibility,
    log_in,
    outlier,
    property_schema,
)
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
            st.Page(**_config_page(lisibility.render)),
            st.Page(**_config_page(outlier.render)),
            st.Page(**_config_page(property_schema.render)),
        ]

    pg = st.navigation(pages)
    pg.run()
