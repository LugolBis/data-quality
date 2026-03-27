from typing import Any

import streamlit as st

from ui.pages import load_data, log_in
from ui.pages.profiling import (
    completeness as pf_completeness,
)
from ui.pages.profiling import (
    consistency as pf_consistency,
)
from ui.pages.profiling import (
    integrity as pf_integrity,
)
from ui.pages.profiling import (
    labeling as pf_labeling,
)
from ui.pages.profiling import (
    lisibility as pf_lisibility,
)
from ui.pages.profiling import (
    outlier as pf_outlier,
)
from ui.pages.quality import completeness as ql_completeness
from ui.pages.quality import (
    consistency as ql_consistency,
)
from ui.pages.quality import (
    integrity as ql_integrity,
)
from ui.pages.quality import schema as ql_schema
from ui.pages.quality import uniqueness as ql_uniqueness
from ui.utils import _config_page

_SECTIONS = {
    "Database management": {
        "Log in": log_in,
        "Load data": load_data,
    },
    "Data Profiling": {
        "Completeness": pf_completeness,
        "Consistency": pf_consistency,
        "Integrity": pf_integrity,
        "Labeling": pf_labeling,
        "Lisibility": pf_lisibility,
        "Outlier": pf_outlier,
    },
    "Data Quality": {
        "Completeness": ql_completeness,
        "Consistency": ql_consistency,
        "Integrity": ql_integrity,
        "Schema": ql_schema,
        "Uniqueness": ql_uniqueness,
    },
}

from ui.pages import overview  # noqa: E402


def _get_pages(section: str, mods: dict[str, Any], code: int) -> list[Any]:
    res = []
    for title, mod in mods.items():
        res.append(st.Page(**_config_page(section, title, mod.render)))

        if code > 0:
            _config_init_session(mod)

            if code > 1:
                _config_section(title, mod)

    if code > 1:
        return [
            st.Page(**_config_page("Data Quality", "Overview", overview.render)),
            *res,
        ]
    return res


def _config_init_session(mod: Any) -> None:  # noqa: ANN401
    for key, value in mod._LAZY_FUNCS.items():  # noqa: SLF001
        st.session_state[key] = value


def _config_section(title: str, mod: Any) -> None:  # noqa: ANN401
    st.session_state[title] = list(mod._LAZY_FUNCS.keys())  # noqa: SLF001


def main() -> None:
    pages: dict[str, Any] = {}
    for code, (section, mods) in enumerate(_SECTIONS.items()):
        pages[section] = _get_pages(section, mods, code)

    displayed_pages: list[Any] | dict[str, Any]
    if not st.session_state.get("is_connected", False):
        displayed_pages = [st.Page(**_config_page("", "Log in", log_in.render))]
    else:
        displayed_pages = pages

    pg = st.navigation(displayed_pages)
    pg.run()
