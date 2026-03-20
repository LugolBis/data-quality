from typing import TYPE_CHECKING, Any

import streamlit as st

from quality.integrity import (
    detecter_doublons_node,
    detecter_doublons_relationships,
)
from scoring.integrity import pair_label_ratio
from ui.components import (
    _analyze_call,
    _dynamic_analysis,
    _score_call,
)
from ui.utils import _SIMILARITY_SLIDER, _lazy_func

if TYPE_CHECKING:
    from collections.abc import Callable

_LAZY_FUNCS = {
    "IDDN": _lazy_func(
        _analyze_call,
        func=detecter_doublons_node,
        key="IDDN",
        lazy_func_args={"seuil_similarite": "_integrity_nodes_duplicates_treshold"},
    ),
    "IDDN_score": _lazy_func(
        _score_call,
        func=pair_label_ratio,
        key="IDDN",
        lazy_func_args={"df": "IDDN_res", "df_cached": "nodes_stats"},
    ),
    "IDDR": _lazy_func(
        _analyze_call,
        func=detecter_doublons_relationships,
        key="IDDR",
        lazy_func_args={
            "seuil_similarite": "_integrity_relationships_duplicates_treshold",
        },
    ),
    "IDDR_score": _lazy_func(
        _score_call,
        func=pair_label_ratio,
        key="IDDR",
        lazy_func_args={"df": "IDDR_res", "df_cached": "rels_stats"},
    ),
}


def render() -> None:
    _headers()
    st.divider()
    _nodes_duplicates()
    st.divider()
    _relationships_duplicates()


def _headers() -> None:
    st.title("Integrity")
    st.markdown("#### Analysis of the integrity of the database.")


def _nodes_duplicates() -> None:
    lazy_render: Callable[[], Any] = _lazy_func(
        st.select_slider,
        label="Select nodes similarity threshold :",
        options=_SIMILARITY_SLIDER,
        value=0.8,
        key="_integrity_nodes_duplicates_treshold",
    )

    _dynamic_analysis(
        "Detection of duplicate **Nodes**.",
        (
            "Scan all nodes to find potential duplicates based on string property"
            "similarity using SequenceMatcher."
        ),
        "IDDN",
        lazy_renders=[lazy_render],
    )


def _relationships_duplicates() -> None:
    lazy_render: Callable[[], Any] = _lazy_func(
        st.select_slider,
        label="Select relationships similarity threshold :",
        options=_SIMILARITY_SLIDER,
        value=0.8,
        key="_integrity_relationships_duplicates_treshold",
    )

    _dynamic_analysis(
        "Detection of duplicate **Relationships**.",
        (
            "Scan all relationships to find potential duplicates based on string"
            " property similarity using SequenceMatcher."
        ),
        "IDDR",
        lazy_renders=[lazy_render],
    )
