from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st

from driver.neo4j_driver import Neo4jSession
from models.enums import Degree, Entity
from models.utils import get_label
from quality.completeness import existence_component, node_degree
from ui.components.analysis import _dataframe_analysis
from ui.components.dynamic import _editor_analyze
from ui.pages.quality.configs import (
    _COL_ENTITY,
    _COL_ENTITY_ALIAS,
    _COL_GRAPH_PATTERN,
    _COL_LABELS,
    _COL_LABELS_TYPE,
)

if TYPE_CHECKING:
    from collections.abc import Callable

_LAZY_FUNCS: dict[str, Callable[[], Any]] = {}


def render() -> None:
    _headers()
    st.divider()
    _component_render()
    st.divider()
    _degree_render()


def _headers() -> None:
    st.title("Completeness")
    st.markdown("#### Analysis of the completeness of the database.")


# Analysis function that takes the edited DataFrame and returns results
def _component_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
    def _row_func(session: Neo4jSession, row: dict[str, Any]) -> list[dict] | None:
        entity = Entity(row["Entity"])
        entity_alias = row["Entity alias"]
        labels: list[str] = row["Label(s) / Type"]
        graph_pattern = row["Graph Pattern"]

        result = existence_component(
            session,
            entity,
            entity_alias,
            get_label(labels),
            graph_pattern,
        )
        return [result] if result else None  # ty:ignore[invalid-return-type]

    return _editor_analyze(dict_rows, _row_func)


def _degree_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
    def _row_func(session: Neo4jSession, row: dict[str, Any]) -> list[dict] | None:
        degree: Degree = Degree(row["Degree type"])
        labels: list[str] = row["Label(s)"]
        expected: list[str] = row["Expected degree"]

        result = node_degree(
            session,
            degree,
            get_label(labels),
            {int(x) for x in expected},
        )
        return [result] if result else None  # ty:ignore[invalid-return-type]

    return _editor_analyze(dict_rows, _row_func)


def _component_render() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Entity",
            "Entity alias",
            "Label(s) / Type",
            "Graph Pattern",
        ],
    )

    # Configuration for the data editor
    editor_config = {
        "num_rows": "dynamic",
        "column_config": {
            "Entity": _COL_ENTITY,
            "Entity alias": _COL_ENTITY_ALIAS,
            "Label(s) / Type": _COL_LABELS_TYPE,
            "Graph Pattern": _COL_GRAPH_PATTERN,
        },
    }

    _dataframe_analysis(
        section_name="Analysis existence of components based on graph patterns.",
        description=(
            "It checks for given labels if all the nodes with it are part of"
            " a component defined by the graph pattern"
        ),
        key="CECG",
        analysis_func=_component_analyze,
        df_template=df_template,
        editor_config=editor_config,
    )


def _degree_render() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Degree type",
            "Label(s)",
            "Expected degree",
        ],
    )

    # Configuration for the data editor
    editor_config = {
        "num_rows": "dynamic",
        "column_config": {
            "Degree type": st.column_config.SelectboxColumn(
                label="Degree type",
                options=["INCOMING", "OUTCOMING"],
                required=True,
            ),
            "Label(s)": _COL_LABELS,
            "Expected degree": st.column_config.ListColumn(
                "Expected degree",
                help="You can select multiple expected degree.",
                required=True,
            ),
        },
    }

    _dataframe_analysis(
        section_name="Analysis the nodes degree.",
        description=(
            "It checks for given labels if all the nodes with it had the expected"
            " degree."
        ),
        key="CEND",
        analysis_func=_degree_analyze,
        df_template=df_template,
        editor_config=editor_config,
    )
