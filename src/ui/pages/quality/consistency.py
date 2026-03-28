import re
from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st

from models.enums import Entity
from quality.consistency import fd
from ui.components.analysis import _dataframe_analysis
from utils.utils import logger

if TYPE_CHECKING:
    from collections.abc import Callable

_LAZY_FUNCS: dict[str, Callable[[], Any]] = {}


def render() -> None:
    _headers()
    st.divider()
    _fd_render()


def _headers() -> None:
    st.title("Consistency")
    st.markdown("#### Analysis of the consistency of the database.")


def _fd_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
    rows = dict_rows.get("added_rows")
    if rows is None:
        logger.error("Failed to get the key 'added_rows' from a data editor.")
        return None
    if len(rows) == 0:
        return []

    session = st.session_state["db_session"]
    analysis = []
    errors = []

    for idx, row in enumerate(rows):
        try:
            entity = Entity(row["Entity"])
            label = row["Label(s) / Type"]
            x = set(row["X"])
            y = set(row["Y"])

            result = fd(
                session,
                entity,
                label,
                x,
                y,
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
    editor_config = {
        "num_rows": "dynamic",
        "column_config": {
            "Entity": st.column_config.SelectboxColumn(
                label="Entity",
                help="Choose the kind of Neo4j entity.",
                options=["NODE", "RELATIONSHIP"],
                required=True,
            ),
            "Label(s) / Type": st.column_config.TextColumn(
                "Label(s) / Type",
                help="You can select multiple labels by separate them with a '&'.",
                required=True,
            ),
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

    _dataframe_analysis(
        section_name="Check functional dependency (FD)",
        description=(
            "It checks for a given label _L_ of the chosen entity if all of it's"
            " occurencies verify the FD (X -> Y)"
        ),
        key="CVFD",
        analysis_func=_fd_analyze,
        df_template=df_template,
        editor_config=editor_config,
    )
