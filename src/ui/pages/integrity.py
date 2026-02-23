from typing import Any, Callable

import streamlit as st

from quality.integrity import (
    detecter_doublons_node,
    detecter_doublons_relationships,
    distr_nodes_properties,
    distr_relationships_properties,
)
from ui.components import _dynamic_analysis, _static_analysis
from ui.utils import _lazy_render

SIMILARITY_SLIDER = (
    0.0,
    0.05,
    0.1,
    0.15,
    0.2,
    0.25,
    0.3,
    0.35,
    0.4,
    0.45,
    0.5,
    0.55,
    0.6,
    0.65,
    0.7,
    0.75,
    0.8,
    0.85,
    0.9,
    0.95,
    1.0,
)


def render() -> None:
    _headers()
    st.divider()
    _nodes_duplicates()
    st.divider()
    _relationships_duplicates()
    st.divider()
    _nodes_properties()
    st.divider()
    _rel_properties()


def _headers() -> None:
    st.title("Integrity")
    st.markdown("#### Analysis of the integrity of the database.")


def _nodes_duplicates() -> None:
    lazy_render: Callable[[], Any] = _lazy_render(
        st.select_slider,
        label="Select nodes similarity threshold :",
        options=SIMILARITY_SLIDER,
        value=0.5,
        key="_integrity_nodes_duplicates_treshold",
    )

    _dynamic_analysis(
        "#### Detection of duplicate **Nodes**.",
        "Scan all nodes to find potential duplicates based on string property similarity using SequenceMatcher.",
        lazy_renders=[lazy_render],
        func=detecter_doublons_node,
        lazy_func_args={"seuil_similarite": "_integrity_nodes_duplicates_treshold"},
    )


def _relationships_duplicates() -> None:
    lazy_render: Callable[[], Any] = _lazy_render(
        st.select_slider,
        label="Select relationships similarity threshold :",
        options=SIMILARITY_SLIDER,
        value=0.8,
        key="_integrity_relationships_duplicates_treshold",
    )

    _dynamic_analysis(
        "#### Detection of duplicate **Relationships**.",
        "Scan all relationships to find potential duplicates based on string property similarity using SequenceMatcher.",
        lazy_renders=[lazy_render],
        func=detecter_doublons_relationships,
        lazy_func_args={
            "seuil_similarite": "_integrity_relationships_duplicates_treshold"
        },
    )


def _nodes_properties() -> None:
    _static_analysis(
        "#### Analysis distribution of **Node** properties.",
        "Analyze if nodes with the same label combination share the exact same set of property keys.",
        distr_nodes_properties,
        flatten=["properties"],
    )


def _rel_properties() -> None:
    _static_analysis(
        "#### Analysis distribution of **Relationship** properties.",
        "Analyze if relationship with the same type share the exact same set of property keys.",
        distr_relationships_properties,
        flatten=["properties"],
    )
