import streamlit as st

from quality.completeness import measure_scc, measure_wcc
from ui.components import _analyze_call, _static_analysis
from ui.utils import _lazy_func

_LAZY_FUNCS = {
    "Cms": _lazy_func(
        _analyze_call, func=measure_scc, key="Cms", flatten=["largest_components"]
    ),
    "Cmw": _lazy_func(
        _analyze_call, func=measure_wcc, key="Cmw", flatten=["largest_components"]
    ),
}


def render() -> None:
    _headers()
    st.divider()
    _render_scc()
    st.divider()
    _render_wcc()


def _headers() -> None:
    st.title("Lisibility")
    st.markdown("#### Analysis of the lisibilty of the database.")


def _render_scc() -> None:
    _static_analysis(
        "#### Measure Strongly Connected Components (SCC) in the graph.",
        "Useful for finding cyclic dependencies (loops) in directional relationships.",
        "Cms",
    )


def _render_wcc() -> None:
    _static_analysis(
        "#### Measure Weakly Connected Components (WCC) in the graph.",
        "Useful for finding isolated islands/fragments of data.",
        "Cmw",
    )
