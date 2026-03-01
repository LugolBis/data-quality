import streamlit as st
from streamlit import session_state as app_st

from quality.lisibility import compute_graph_diameter, distr_node_degree
from scoring.lisibility import nodes_degree
from ui.components import _analyze_call, _button, _score_call, _static_analysis
from ui.utils import _lazy_func

_LAZY_FUNCS = {
    "LDND": _lazy_func(_analyze_call, func=distr_node_degree, key="LDND"),
    "LDND_score": _lazy_func(
        _score_call,
        func=nodes_degree,
        key="LDND",
        lazy_func_args={"df": "LDND_res"},
    ),
    "LCGD": _lazy_func(
        _analyze_call,
        func=compute_graph_diameter,
        key="LCGD",
        to_df=False,
    ),
}


def render() -> None:
    _headers()
    st.divider()
    _node_degree()
    st.divider()
    _graph_diameter()


def _headers() -> None:
    st.title("Lisibility")
    st.markdown("#### Analysis of the lisibilty of the database.")


def _node_degree() -> None:
    _static_analysis(
        "Distribution of **Nodes** degree.",
        "Compute statistics of the nodes degree.",
        "LDND",
    )


def _graph_diameter() -> None:
    st.markdown("Graph diameter.")
    st.markdown("Compute Graph diameter.")

    _button(
        "Analyse",
        "LCGD",
    )

    stored = app_st["LCGD_res"]
    st.metric("Graph Diameter", stored["data"], border=True)
