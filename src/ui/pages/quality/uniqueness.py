from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st

from models.enums import Entity
from models.utils import format_label
from quality.uniqueness import (
    duplicate_multivalued,
    duplicate_nodes,
    duplicate_relationships,
)
from ui.components.analysis import _dataframe_analysis, _static_analysis
from ui.components.dynamic import _analyze_call
from ui.utils import _lazy_func
from utils.utils import logger

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
            labels: list[str] = row["Label(s)"]
            treshold: int = row["Relationships similarity treshold"]

            for label in labels:
                result = duplicate_nodes(
                    session,
                    label,
                    (treshold / 100.00),
                )
                if result:
                    analysis.extend(result)
        except Exception as e:
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    return analysis if analysis else None


def _multivalued_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
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
            entity: Entity = Entity(row["Entity"])
            label: list[str] = row["Label(s) / Type"]
            properties: list[str] = row["Properties"]

            result = duplicate_multivalued(
                session,
                entity,
                format_label(label),
                set(properties),
            )
            if result:
                analysis.extend(result)
        except Exception as e:
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    return analysis if analysis else None


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
            "Label(s)": st.column_config.ListColumn(
                "Label(s)",
                help=(
                    "You can select combined labels by separate them with a '&' in"
                    " the same entry."
                ),
                required=True,
            ),
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
            "Entity": st.column_config.SelectboxColumn(
                label="Entity",
                help="Choose the kind of Neo4j entity.",
                options=["NODE", "RELATIONSHIP"],
                required=True,
            ),
            "Label(s) / Type": st.column_config.ListColumn(
                "Label(s)",
                help=("Select the set of label of the targeted entity."),
                required=True,
            ),
            "Properties": st.column_config.ListColumn(
                "Properties",
                help=(
                    "Select the set of multivalued properties who shouldn't contains"
                    " duplicates."
                ),
                required=True,
            ),
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
