import re
from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st

from models.enums import Degree, Entity
from quality.completeness import existence_component, node_degree
from ui.components.analysis import _dataframe_analysis
from utils.utils import logger

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
    rows = dict_rows.get("added_rows")
    if rows is None:
        logger.error("Failed to get the key 'added_rows' from a data editor.")
        return None
    if len(rows) == 0:
        return None

    session = st.session_state["db_session"]
    analysis = []
    errors = []

    for idx, row in enumerate(rows):
        try:
            entity = Entity(row["Entity"])
            entity_alias = row["Entity alias"]
            label_start = row["Entity label"]
            graph_pattern = row["Graph Pattern"]

            result = existence_component(
                session,
                entity,
                entity_alias,
                label_start,
                graph_pattern,
            )
            if result:
                analysis.append(result)
        except re.error as e:
            errors.append(f"Line {idx + 1}: Invalid regex - {e}")
        except Exception as e:
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    return analysis if analysis else None


def _degree_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
    rows = dict_rows.get("added_rows")
    if rows is None:
        logger.error("Failed to get the key 'added_rows' from a data editor.")
        return None
    if len(rows) == 0:
        return None

    session = st.session_state["db_session"]
    analysis = []
    errors = []

    for idx, row in enumerate(rows):
        try:
            degree: Degree = Degree(row["Degree type"])
            label: str = row["Label"]
            expected: list[str] = row["Expected degree"]

            result = node_degree(
                session,
                degree,
                label,
                {int(x) for x in expected},
            )
            if result:
                analysis.append(result)
        except Exception as e:
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    return analysis if analysis else None


def _component_render() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Entity",
            "Entity alias",
            "Entity label",
            "Graph Pattern",
        ],
    )

    # Configuration for the data editor
    editor_config = {
        "num_rows": "dynamic",
        "column_config": {
            "Entity": st.column_config.SelectboxColumn(
                label="Entity",
                help="Choose the kind of Neo4j entity.",
                options=["NODE", "RELATIONSHIP"],
                required=True,
            ),
            "Entity alias": st.column_config.TextColumn(
                "Entity alias",
                help=(
                    "It's the alias used by `Graph Pattern` to reference the entity."
                ),
                required=True,
            ),
            "Entity label": st.column_config.TextColumn(
                "Entity label",
                help="You can select multiple labels by separate them with a '&'.",
                required=True,
            ),
            "Graph Pattern": st.column_config.TextColumn(
                "Graph Pattern",
                required=True,
            ),
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
            "Label",
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
            "Label": st.column_config.TextColumn(
                "Label",
                help="You can select multiple labels by separate them with a '&'.",
                required=True,
            ),
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
