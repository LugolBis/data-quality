import streamlit as st

from profiling.integrity import (
    distr_nodes_properties,
    distr_relationships_properties,
)
from ui.components import (
    _analyze_call,
    _static_analysis,
)
from ui.utils import _lazy_func

_LAZY_FUNCS = {
    "IDNP": _lazy_func(
        _analyze_call,
        func=distr_nodes_properties,
        key="IDNP",
        flatten=["properties"],
    ),
    "IDRP": _lazy_func(
        _analyze_call,
        func=distr_relationships_properties,
        key="IDRP",
        flatten=["properties"],
    ),
}


def render() -> None:
    _headers()
    st.divider()
    _nodes_properties()
    st.divider()
    _rel_properties()


def _headers() -> None:
    st.title("Integrity")
    st.markdown("#### Profiling of the integrity of the database.")


def _nodes_properties() -> None:
    _static_analysis(
        "Analysis distribution of **Node** properties.",
        (
            "Analyze if nodes with the same label combination share the exact same set"
            "of property keys."
        ),
        "IDNP",
    )


def _rel_properties() -> None:
    _static_analysis(
        "Analysis distribution of **Relationship** properties.",
        (
            "Analyze if relationship with the same type share the exact same set of"
            " property keys."
        ),
        "IDRP",
    )
