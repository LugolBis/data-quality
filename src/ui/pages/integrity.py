import streamlit as st

from quality.integrity import distr_nodes_properties, distr_relationships_properties
from ui.components import _static_analysis


def render() -> None:
    _headers()
    st.divider()
    _nodes_properties()
    st.divider()
    _rel_properties()


def _headers() -> None:
    st.title("Integrity")
    st.markdown("#### Analysis of the integrity of the database.")


def _nodes_properties() -> None:
    _static_analysis(
        "#### Analysis distribution of **Node** properties.",
        "Analyze if nodes with the same label combination share the exact same set of property keys.",
        "Analyse nodes properties type.",
        distr_nodes_properties,
        flatten=["properties"],
    )


def _rel_properties() -> None:
    _static_analysis(
        "#### Analysis distribution of **Relationship** properties.",
        "Analyze if relationship with the same type share the exact same set of property keys.",
        "Analyse relationships properties type.",
        distr_relationships_properties,
        flatten=["properties"],
    )
