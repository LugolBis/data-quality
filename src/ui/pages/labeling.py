from typing import TYPE_CHECKING, Any

import streamlit as st

from quality.labeling import detect_label_anomalies_by_features
from ui.components import (
    _analyze_call,
    _dynamic_analysis,
)
from ui.pages.integrity import _SIMILARITY_SLIDER
from ui.utils import _lazy_func

if TYPE_CHECKING:
    from collections.abc import Callable

_LAZY_FUNCS = {
    "LBAF": _lazy_func(
        _analyze_call,
        func=detect_label_anomalies_by_features,
        key="LBAF",
        lazy_func_args={
            "similarity_threshold": "_labelling_similarity_threshold",
            "property_ratio": "_labelling_property_ratio",
        },
        flatten=["anomalies"],
    ),
}


def render() -> None:
    _headers()
    st.divider()
    _anomalies()


def _headers() -> None:
    st.title("Labeling")
    st.markdown("#### Analysis labelling of the database.")


def _anomalies() -> None:
    lazy_render_t: Callable[[], Any] = _lazy_func(
        st.select_slider,
        label="Minimum KNN similarity to be considered a match :",
        options=_SIMILARITY_SLIDER,
        value=0.85,
        key="_labelling_similarity_threshold",
    )

    lazy_render_r: Callable[[], Any] = _lazy_func(
        st.select_slider,
        label="How much weight to give node properties vs. graph topology in FastRP :",
        options=_SIMILARITY_SLIDER,
        value=0.5,
        key="_labelling_property_ratio",
    )

    _dynamic_analysis(
        "Detect nodes with highly similar features but different labels.",
        (
            "Transform relationships into nodes, extract topological + property "
            "features (FastRP), and use KNN to find nodes with highly similar features "
            "but DIFFERENT labels. Uses '__entity' to strictly separate original Nodes "
            "from Relationships."
        ),
        "LBAF",
        lazy_renders=[lazy_render_t, lazy_render_r],
    )
