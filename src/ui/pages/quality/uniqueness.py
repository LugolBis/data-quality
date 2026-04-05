from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st

from driver.neo4j_driver import Neo4jSession
from models.enums import Entity
from models.utils import get_label
from quality.uniqueness import (
    duplicate_multivalued,
    duplicate_nodes,
    duplicate_relationships,
)
from ui.components.analysis import _dataframe_analysis, _static_analysis
from ui.components.dynamic import _analyze_call, _editor_analyze
from ui.pages.quality.configs import (
    _COL_ENTITY,
    _COL_LABELS,
    _COL_LABELS_TYPE,
    _COL_PROPERTIES,
)
from ui.utils import _lazy_func

if TYPE_CHECKING:
    from collections.abc import Callable

_LAZY_FUNCS: dict[str, Callable[[], Any]] = {
    "UDRD": _lazy_func(
        _analyze_call,
        func=duplicate_relationships,
        key="UDRD",
    ),
}


def render() -> None:
    _headers()
    st.divider()
    _relationships()
    st.divider()
    _nodes_render()
    st.divider()
    _multivalued_render()


def _headers() -> None:
    st.title("Uniqueness")
    st.markdown("#### Analysis of the uniqueness of the database.")


def _relationships() -> None:
    _static_analysis(
        "Detection of duplicate **Relationships**.",
        (
            "Two relationships are considered as duplicates if they both have the exact"
            " same set of properties (values), label and source/destination node."
        ),
        "UDRD",
    )


def _nodes_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
    def _row_func(session: Neo4jSession, row: dict[str, Any]) -> list[dict] | None:
        labels: list[str] = row["Label(s)"]
        treshold: int = row["Relationships similarity treshold"]

        return duplicate_nodes(
            session,
            get_label(labels),
            (treshold / 100.00),
        )  # ty:ignore[invalid-return-type]

    return _editor_analyze(dict_rows, _row_func)


def _multivalued_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
    def _row_func(session: Neo4jSession, row: dict[str, Any]) -> list[dict] | None:
        entity: Entity = Entity(row["Entity"])
        labels: list[str] = row["Label(s) / Type"]
        properties: list[str] = row["Properties"]

        return duplicate_multivalued(
            session,
            entity,
            get_label(labels),
            set(properties),
        )  # ty:ignore[invalid-return-type]

    return _editor_analyze(dict_rows, _row_func)


def _nodes_render() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Label(s)",
            "Relationships similarity treshold",
        ],
    )

    # Configuration for the data editor
    editor_config = {
        "num_rows": "dynamic",
        "column_config": {
            "Label(s)": _COL_LABELS,
            "Relationships similarity treshold": st.column_config.NumberColumn(
                "Relationships similarity treshold",
                help=(
                    "This is the percent of shared relationships needed to consider"
                    " nodes as duplicates."
                ),
                min_value=0.0,
                max_value=100.0,
                default=50.0,
                required=True,
            ),
        },
    }

    _dataframe_analysis(
        section_name="Detection of duplicate **Nodes**.",
        description=(
            "Two nodes are considered as duplicates if they both have the exact same"
            " set of properties (values), labels and all of the relationships attached"
            " to them or duplicates if they was merged into one node."
        ),
        key="UDND",
        analysis_func=_nodes_analyze,
        df_template=df_template,
        editor_config=editor_config,
    )


def _multivalued_render() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Entity",
            "Label(s) / Type",
            "Properties",
        ],
    )

    # Configuration for the data editor
    editor_config = {
        "num_rows": "dynamic",
        "column_config": {
            "Entity": _COL_ENTITY,
            "Label(s) / Type": _COL_LABELS_TYPE,
            "Properties": _COL_PROPERTIES,
        },
    }

    _dataframe_analysis(
        section_name="Detection of duplicate in multivalued property.",
        description=("Detect the multivalued properties who had duplicates values."),
        key="UDMD",
        analysis_func=_multivalued_analyze,
        df_template=df_template,
        editor_config=editor_config,
    )
