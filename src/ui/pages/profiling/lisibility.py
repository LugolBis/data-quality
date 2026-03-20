import streamlit as st
from streamlit import session_state as app_st

from profiling.lisibility import compute_graph_eccentricity, distr_node_degree
from scoring.lisibility import eccentricity, nodes_degree
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
        func=compute_graph_eccentricity,
        key="LCGD",
        to_df=False,
    ),
    "LCGD_score": _lazy_func(
        _score_call,
        func=eccentricity,
        key="LCGD",
        lazy_func_args={"eccentricity": "LCGD_res"},
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
    st.markdown("#### Profiling of the lisibilty of the database.")


def _node_degree() -> None:
    _static_analysis(
        "Distribution of **Nodes** degree.",
        "Compute statistics of the nodes degree.",
        "LDND",
    )


def _graph_diameter() -> None:
    st.markdown("Analyse Graph eccentricity.")
    st.markdown("Compute Graph diameter and radius.")

    _button(
        "Analyse",
        "LCGD",
    )

    stored = app_st["LCGD_res"]

    column1, column2 = st.columns(2)

    with column1:
        st.metric(
            label="Graph Diameter :",
            value=stored["data"].diameter,
            border=True,
        )

    with column2:
        st.metric(
            label="Graph Radius :",
            value=stored["data"].radius,
            border=True,
        )
