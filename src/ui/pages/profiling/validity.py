import streamlit as st

from profiling.validity import check_properties_type
from ui.components.analysis import _static_analysis
from ui.components.dynamic import (
    _analyze_call,
)
from ui.utils import _lazy_func

_LAZY_FUNCS = {
    "VCPT": _lazy_func(_analyze_call, func=check_properties_type, key="VCPT"),
}


def render() -> None:
    _headers()
    st.divider()
    _properties_type()


def _headers() -> None:
    st.title("Validity")
    st.markdown("#### Profiling of the validity of the database.")


def _properties_type() -> None:
    _static_analysis(
        "Analysis properties type.",
        (
            "Check if there is any pair of **Node**/**Relationship** who has one "
            "property with different type."
        ),
        "VCPT",
    )
