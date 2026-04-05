from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from models.enums import Entity
from models.utils import get_label
from quality.consistency import cfd, fd, gfd, query_validation
from ui.components.analysis import _dataframe_analysis
from ui.pages.quality.configs import _COL_ENTITY, _COL_LABELS_TYPE
from ui.pages.quality.utils import (
    _CONDITIONAL_COL_CONFIG,
    _CONDITIONAL_DF_TEMPLATE,
    _generate_condition,
)
from ui.utils import _lazy_func
from utils.utils import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from streamlit.elements.lib.column_types import ColumnConfig

_LAZY_FUNCS: dict[str, Callable[[], Any]] = {}
_CONDITION_EDITOR_KEY: str = "_ql_consistency_condition_editor_key"

_FD_EDITOR_CONFIG: dict[str, str | dict[str, ColumnConfig]] = {
    "num_rows": "dynamic",
    "column_config": {
        "Entity": _COL_ENTITY,
        "Label(s) / Type": _COL_LABELS_TYPE,
        "X": st.column_config.ListColumn(
            "X",
            help="Set of key properties.",
            required=True,
        ),
        "Y": st.column_config.ListColumn(
            "Y",
            help="Set of deduced properties.",
            required=True,
        ),
    },
}


def render() -> None:
    _headers()
    st.divider()
    _fd_render()
    st.divider()
    _cfd_render()
    st.divider()
    _gfd_render()
    st.divider()
    _dvq_render()


def _headers() -> None:
    st.title("Consistency")
    st.markdown("#### Analysis of the consistency of the database.")


def _fd_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
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
            labels: list[str] = row["Label(s) / Type"]
            x = set(row["X"])
            y = set(row["Y"])

            result = fd(
                session,
                entity,
                get_label(labels),
                x,
                y,
            )
            if result:
                analysis.append(result)
        except Exception as e:
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    return analysis if analysis else None


def _cfd_analyze(  # noqa: C901
    dict_rows: dict[str, Any],
) -> list[dict] | None:
    df_edited = app_st.get(_CONDITION_EDITOR_KEY)

    if df_edited is None or (isinstance(df_edited, pd.DataFrame) and df_edited.empty):
        return None
    df_cond = pd.DataFrame(df_edited.get("added_rows"))

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
            labels: list[str] = row["Label(s) / Type"]
            cond_name = row["Condition name"]
            x = set(row["X"])
            y = set(row["Y"])

            if cond_name is None:
                errors.append(f"Line {idx + 1}: Missing required field Condition Line")
                continue

            condition = _generate_condition(df_cond, cond_name, [])
            if isinstance(condition, str):
                errors.append(f"Line {idx + 1}: {condition}")
                continue

            result = cfd(
                session,
                entity,
                get_label(labels),
                condition,
                x,
                y,
            )
            if result:
                analysis.append(result)
        except Exception as e:
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    return analysis if analysis else None


def _gfd_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
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
            labels: list[str] = row["Label(s) / Type"]
            graph_pattern = row["Graph pattern"]
            x = set(row["X"])
            y = set(row["Y"])

            result = gfd(
                session,
                entity,
                entity_alias,
                get_label(labels),
                graph_pattern,
                x,
                y,
            )
            if result:
                analysis.append(result)
        except Exception as e:
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    return analysis if analysis else None


def _dvq_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
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
            query: str = row["Query"]
            should_be_empty: bool = row["Should be empty"]

            result = query_validation(
                session,
                query,
                should_be_empty,
            )
            if result:
                analysis.append(result)
        except Exception as e:
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    return analysis if analysis else None


def _fd_render() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Entity",
            "Label(s) / Type",
            "X",
            "Y",
        ],
    )

    # Configuration for the data editor
    editor_config = _FD_EDITOR_CONFIG

    _dataframe_analysis(
        section_name="Check functional dependencies (FD)",
        description=(
            "It checks for a given label _L_ of the chosen entity if all of it's"
            " occurencies verify the FD (X -> Y)"
        ),
        key="CVFD",
        analysis_func=_fd_analyze,
        df_template=df_template,
        editor_config=editor_config,
    )


def _cfd_render() -> None:
    lazy_render: Callable[[], Any] = _lazy_func(
        st.data_editor,
        data=_CONDITIONAL_DF_TEMPLATE,
        key=_CONDITION_EDITOR_KEY,
        use_container_width=True,
        num_rows="dynamic",
        column_config=_CONDITIONAL_COL_CONFIG,
    )

    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Entity",
            "Label(s) / Type",
            "Condition name",
            "X",
            "Y",
        ],
    )

    # Configuration for the data editor
    editor_config = _FD_EDITOR_CONFIG
    if isinstance(editor_config["column_config"], dict):
        editor_config["column_config"]["Condition name"] = st.column_config.TextColumn(
            "Condition name",
            help=("Select the name of the condition written in the Condition editor."),
            required=True,
        )

    _dataframe_analysis(
        section_name="Check conditional functional dependencies (CFD)",
        description=(
            "It checks for a given label _L_ of the chosen entity if all of it's"
            " occurencies verify the FD (X -> Y)"
        ),
        key="CCFD",
        analysis_func=_cfd_analyze,
        df_template=df_template,
        editor_config=editor_config,
        lazy_renders=[lazy_render],
    )


def _gfd_render() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Entity",
            "Entity alias",
            "Label(s) / Type",
            "Graph pattern",
            "X",
            "Y",
        ],
    )

    # Configuration for the data editor
    editor_config = _FD_EDITOR_CONFIG
    if isinstance(editor_config["column_config"], dict):
        editor_config["column_config"]["Entity alias"] = st.column_config.TextColumn(
            "Entity alias",
            help="It's the alias used by `Graph Pattern` to reference the entity.",
            required=True,
        )
        editor_config["column_config"]["Graph pattern"] = st.column_config.TextColumn(
            "Graph pattern",
            help="It's the alias used to reference the entity in the `Graph Pattern`.",
            required=True,
        )

    _dataframe_analysis(
        section_name="Check graph functional dependencies (GFD)",
        description=(
            "It checks for a given label _L_ of the chosen entity who match a given "
            "graph pattern if all of it's occurencies verify the FD (X -> Y). "
            "Paid attention to don't give alias to the entities who are part of the "
            "graph pattern because it is matched twice to verify the GFD."
        ),
        key="CGFD",
        analysis_func=_gfd_analyze,
        df_template=df_template,
        editor_config=editor_config,
    )


def _dvq_render() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Query",
            "Should be empty",
        ],
    )

    # Configuration for the data editor
    editor_config = {
        "num_rows": "dynamic",
        "column_config": {
            "Query": st.column_config.TextColumn(
                label="Query",
                help="Enter a Cypher query.",
                required=True,
            ),
            "Should be empty": st.column_config.CheckboxColumn(
                label="Should be empty",
                help="If the query shouldn't return values.",
                default=True,
                required=True,
            ),
        },
    }

    _dataframe_analysis(
        section_name="Data validation query",
        description=("Validate your data with a query approach for complex purpose."),
        key="CDVQ",
        analysis_func=_dvq_analyze,
        df_template=df_template,
        editor_config=editor_config,
    )
