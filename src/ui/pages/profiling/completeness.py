from typing import TYPE_CHECKING, Any

import streamlit as st

from profiling.completeness import measure_scc, measure_wcc
from ui.components import _analyze_call, _dynamic_analysis
from ui.utils import _lazy_func

if TYPE_CHECKING:
    from collections.abc import Callable

_LAZY_FUNCS = {
    "CMS": _lazy_func(
        _analyze_call,
        func=measure_scc,
        key="CMS",
        flatten=["largest_components"],
    ),
    "CMW": _lazy_func(
        _analyze_call,
        func=measure_wcc,
        key="CMW",
        flatten=["largest_components"],
    ),
}


def render() -> None:
    _headers()
    st.divider()
    _render_scc()
    st.divider()
    _render_wcc()


def _headers() -> None:
    st.title("Completeness")
    st.markdown("#### Profiling of the completeness of the database.")


def _render_scc() -> None:
    lazy_render: Callable[[], Any] = _lazy_func(
        st.number_input,
        label="Select the minimum number of nodes a SCC component must have :",
        min_value=2,
        step=1,
        key="_completeness_scc_min",
    )

    _dynamic_analysis(
        "Measure Strongly Connected Components (SCC) in the graph.",
        "Useful for finding cyclic dependencies (loops) in directional relationships.",
        "CMS",
        lazy_renders=[lazy_render],
    )


def _render_wcc() -> None:
    lazy_render: Callable[[], Any] = _lazy_func(
        st.number_input,
        label="Select the minimum number of nodes a WCC component must have :",
        min_value=1,
        step=1,
        key="_completeness_wcc_min",
    )

    _dynamic_analysis(
        "Measure Weakly Connected Components (WCC) in the graph.",
        "Useful for finding isolated islands/fragments of data.",
        "CMW",
        lazy_renders=[lazy_render],
    )
