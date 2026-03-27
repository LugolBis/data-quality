from typing import TYPE_CHECKING, Any

import streamlit as st

from quality.uniqueness import duplicate_nodes, duplicate_relationships
from ui.components.analysis import _static_analysis
from ui.components.dynamic import _analyze_call
from ui.utils import _lazy_func

if TYPE_CHECKING:
    from collections.abc import Callable

_LAZY_FUNCS: dict[str, Callable[[], Any]] = {
    "UDRD": _lazy_func(
        _analyze_call,
        func=duplicate_relationships,
        key="UDRD",
    ),
    "UDND": _lazy_func(
        _analyze_call,
        func=duplicate_nodes,
        key="UDND",
    ),
}


def render() -> None:
    _headers()
    st.divider()
    _relationships()
    st.divider()
    _nodes()


def _headers() -> None:
    st.title("Uniqueness")
    st.markdown("#### Analysis of the uniqueness of the database.")


def _relationships() -> None:
    _static_analysis(
        "Detection of duplicate **Relationships**.",
        (
            "Two relationships are considered as duplicates if they both have the exact"
            " same set of properties (values), label and source/destination node."
        ),
        "UDRD",
    )


def _nodes() -> None:
    _static_analysis(
        "Detection of duplicate **Nodes**.",
        (
            "Two nodes are considered as duplicates if they both have the exact same"
            " set of properties (values), labels and all of the relationships attached"
            " to them or duplicates if they was merged into one node."
        ),
        "UDND",
    )
