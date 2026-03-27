import streamlit as st

from quality.integrity import check_constraint_violation, check_index_violation
from scoring.integrity import constraint_score, index_score
from ui.components.analysis import _static_analysis
from ui.components.dynamic import (
    _analyze_call,
    _score_call,
)
from ui.utils import _lazy_func

_LAZY_FUNCS = {
    "PSCCV": _lazy_func(_analyze_call, func=check_constraint_violation, key="PSCCV"),
    "PSCCV_score": _lazy_func(
        _score_call,
        func=constraint_score,
        key="PSCCV",
        lazy_func_args={"df": "PSCCV_res"},
    ),
    "PSCIV": _lazy_func(_analyze_call, func=check_index_violation, key="PSCIV"),
    "PSCIV_score": _lazy_func(
        _score_call,
        func=index_score,
        key="PSCIV",
        lazy_func_args={
            "df": "PSCIV_res",
            "df_cached_nodes": "nodes_stats",
            "df_cached_rels": "rels_stats",
        },
    ),
}


def render() -> None:
    _headers()
    st.divider()
    _constraint()
    st.divider()
    _index()


def _headers() -> None:
    st.title("Property Schema")
    st.markdown("#### Analysis of compliance with the property schema")


def _constraint() -> None:
    description: str = (
        "Scan the database to search schema constraint violations.\n"
        "When it's `Constraint.UNIQUENESS` or `Constraint.KEY`, `count` is the number"
        " of distinct pair of entity who violate the constraint."
    )

    _static_analysis("Analyse constraint integrity", description, "PSCCV")


def _index() -> None:
    _static_analysis(
        "Analyse index integrity",
        (
            "Check if there is any **Node**/**Relationship** who has a `NULL` value"
            " on an indexed property."
        ),
        "PSCIV",
    )
