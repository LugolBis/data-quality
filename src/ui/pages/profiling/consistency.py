import streamlit as st

from profiling.consistency import check_properties_type
from ui.components.analysis import _static_analysis
from ui.components.dynamic import (
    _analyze_call,
)
from ui.utils import _lazy_func

_LAZY_FUNCS = {
    "CCPT": _lazy_func(_analyze_call, func=check_properties_type, key="CCPT"),
}


def render() -> None:
    _headers()
    st.divider()
    _properties_type()


def _headers() -> None:
    st.title("Consistency")
    st.markdown("#### Profiling of the consistency of the database.")


def _properties_type() -> None:
    _static_analysis(
        "Analysis properties type.",
        (
            "Check if there is any pair of **Node**/**Relationship** who has one "
            "property with different type."
        ),
        "CCPT",
    )
