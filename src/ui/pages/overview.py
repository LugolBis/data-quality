import streamlit as st
from streamlit import session_state as app_st

from ui.components import _button
from ui.utils import _lazy_func

_SECTIONS: list[str] = [
    "Consistency",
    "Integrity",
    "Lisibility",
    "Outlier",
    "Property schema",
]


def render() -> None:
    _headers()
    st.divider()
    _body()


def _headers() -> None:
    st.title("Data Quality - Overview")
    st.markdown("#### Overview of the data quality of the database.")


def _body() -> None:
    key: str = "Overview"

    if key not in app_st:
        app_st[key] = _lazy_func(_run_all_analysis)

    _button("Analyze data quality", key)


def _run_all_analysis() -> None:
    for section in _SECTIONS:
        st.markdown(f"#### {section}")
        for key in app_st[section]:
            app_st[key]()

            # TODO! Display score here based on 'key_res' data
