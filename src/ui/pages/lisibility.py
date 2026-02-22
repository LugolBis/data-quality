import streamlit as st
from streamlit import session_state as app_st

from quality.lisibility import compute_graph_diameter, distr_node_degree
from ui.components import _button, _static_analysis


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
        "#### Distribution of **Nodes** degree.",
        "Compute statistics of the nodes degree.",
        "Analyse",
        distr_node_degree,
    )


def _graph_diameter() -> None:
    key = "_static_analysis_result_graph_diameter"

    st.markdown("#### Graph diameter.")
    st.markdown("Compute Graph diameter.")

    session = app_st["db_session"]

    _button(
        "Analyse",
        key,
        compute_graph_diameter,
        session,
        {"gds_graph_name": "gds_diameter"},
    )

    stored = st.session_state[key]
    st.markdown("|  " + str(stored["data"]) + "  |")
