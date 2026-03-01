import streamlit as st

from quality.schema import check_constraint_violation, check_index_violation
from ui.components import _analyze_call, _static_analysis
from ui.utils import _lazy_func

_LAZY_FUNCS = {
    "PSccv": _lazy_func(_analyze_call, func=check_constraint_violation, key="PSccv"),
    "Pciv": _lazy_func(_analyze_call, func=check_index_violation, key="Pciv"),
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

    _static_analysis("Analyse constraint integrity", description, "PSccv")


def _index() -> None:
    _static_analysis(
        "Analyse index integrity",
        (
            "Check if there is any **Node**/**Relationship** who has a `NULL` value"
            " on an indexed property."
        ),
        "Pciv",
    )
