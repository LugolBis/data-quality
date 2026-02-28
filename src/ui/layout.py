from typing import TYPE_CHECKING, Any

import streamlit as st

from ui.pages import (
    completeness,
    consistency,
    integrity,
    lisibility,
    load_data,
    log_in,
    outlier,
    overview,
    property_schema,
)
from ui.utils import _config_page

if TYPE_CHECKING:
    from collections.abc import Callable

_LAZY_FUNCS = {
    "Completeness": completeness._LAZY_FUNCS,  # noqa: SLF001
    "Consistency": consistency._LAZY_FUNCS,  # noqa: SLF001
    "Integrity": integrity._LAZY_FUNCS,  # noqa: SLF001
    "Lisibility": lisibility._LAZY_FUNCS,  # noqa: SLF001
    "Outlier": outlier._LAZY_FUNCS,  # noqa: SLF001
    "Property schema": property_schema._LAZY_FUNCS,  # noqa: SLF001
}


def main() -> None:
    for key, value in _LAZY_FUNCS.items():
        _config_init_session(key, value)

    pages: list[Any] | dict[str, Any]

    if not st.session_state.get("is_connected", False):
        pages = [st.Page(**_config_page(log_in.render))]
    else:
        pages = {
            "Database management": [
                st.Page(**_config_page(log_in.render)),
                st.Page(**_config_page(load_data.render)),
            ],
            "Data Quality analysis": [
                st.Page(**_config_page(overview.render)),
                st.Page(**_config_page(completeness.render)),
                st.Page(**_config_page(consistency.render)),
                st.Page(**_config_page(integrity.render)),
                st.Page(**_config_page(lisibility.render)),
                st.Page(**_config_page(outlier.render)),
                st.Page(**_config_page(property_schema.render)),
            ],
        }

    pg = st.navigation(pages)
    pg.run()


def _config_init_session(section: str, constant: dict[str, Callable[[], Any]]) -> None:
    st.session_state[section] = list(constant.keys())

    for key, value in constant.items():
        st.session_state[key] = value
