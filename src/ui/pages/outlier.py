from typing import TYPE_CHECKING, Any

import streamlit as st

from quality.outlier import (
    detecter_outliers_numeriques,
    measure_average_centrality_by_label,
    measure_eigenvector_centrality,
)
from ui.components import _analyze_call, _dynamic_analysis, _static_analysis
from ui.pages.integrity import _SIMILARITY_SLIDER
from ui.utils import _lazy_func

if TYPE_CHECKING:
    from collections.abc import Callable

_LAZY_FUNCS = {
    "ODON": _lazy_func(
        _analyze_call,
        func=detecter_outliers_numeriques,
        key="ODON",
        lazy_func_args={"z_score_threshold": "_outlier_z_score_threshold"},
        flatten=["outliers"],
    ),
    "OMEC": _lazy_func(
        _analyze_call,
        func=measure_eigenvector_centrality,
        key="OMEC",
        lazy_func_args={"epsilon": "_outlier_ecs"},
    ),
    "OMACBL": _lazy_func(
        _analyze_call,
        func=measure_average_centrality_by_label,
        key="OMACBL",
    ),
}

_THRESHOLD_SLIDER = tuple(round(0.05 * x, 2) for x in range(-60, 61))


def render() -> None:
    _headers()
    st.divider()
    _numeric()
    st.divider()
    _outliers_centrality()
    st.divider()
    _avg_centrality()


def _headers() -> None:
    st.title("Outliers")
    st.markdown("#### Analysis of outliers property values.")


def _numeric() -> None:
    lazy_render: Callable[[], Any] = _lazy_func(
        st.select_slider,
        label="Select property Z-Score threshold :",
        options=_THRESHOLD_SLIDER,
        value=1.95,
        key="_outlier_z_score_threshold",
    )

    _dynamic_analysis(
        "Detection of **Nodes** properties numerical outliers.",
        (
            "Calculate mean, standard deviation and confidence interval"
            " to detect numerical outliers."
        ),
        "ODON",
        lazy_renders=[lazy_render],
    )


def _outliers_centrality() -> None:
    lazy_render: Callable[[], Any] = _lazy_func(
        st.select_slider,
        label="Selection of the lower bound of score :",
        options=_SIMILARITY_SLIDER,
        value=0.5,
        key="_outlier_ecs",
    )

    _dynamic_analysis(
        (
            "Detection of **Nodes** outliers based on their "
            "`Eigenvector Centrality` score."
        ),
        (
            "The `Eigenvector Centrality` is a measure of the influence of a node"
            " in a connected network."
        ),
        "OMEC",
        lazy_renders=[lazy_render],
    )


def _avg_centrality() -> None:
    _static_analysis(
        "Analyze `Eigenvector Centrality` of **Nodes**.",
        (
            "Check the graph topology and calculate the average Eigenvector Centrality"
            " grouped by node labels."
        ),
        "OMACBL",
    )
