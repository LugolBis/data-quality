from typing import Any, Callable

import numpy as np
import streamlit as st

from quality.outlier import (
    detecter_outliers_numeriques,
    measure_average_centrality_by_label,
    measure_eigenvector_centrality,
)
from ui.components import _dynamic_analysis, _static_analysis
from ui.utils import _lazy_render


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
    lazy_render: Callable[[], Any] = _lazy_render(
        st.select_slider,
        label="Select property Z-Score threshold :",
        options=np.arange(-3, 3.05, 0.05).tolist(),
        value=1.95,
        key="_outlier_z_score_threshold",
    )

    _dynamic_analysis(
        "#### Detection of **Nodes** properties numerical outliers.",
        "Calculate mean, standard deviation and confidence interval to detect numerical outliers.",
        lazy_renders=[lazy_render],
        func=detecter_outliers_numeriques,
        lazy_func_args={"z_score_threshold": "_outlier_z_score_threshold"},
        flatten=["outliers"],
    )


def _outliers_centrality() -> None:
    _static_analysis(
        "#### Detection of **Nodes** outliers based on their `Eigenvector Centrality` score.",
        "The `Eigenvector Centrality` is a measure of the influence of a node in a connected network.",
        measure_eigenvector_centrality,
    )


def _avg_centrality() -> None:
    _static_analysis(
        "#### Analyze `Eigenvector Centrality` of **Nodes**.",
        "Check the graph topology and calculate the average Eigenvector Centrality grouped by node labels.",
        measure_average_centrality_by_label,
    )
