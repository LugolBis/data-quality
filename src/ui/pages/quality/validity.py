import re
from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st

from models.enums import Entity
from quality.validity import check_string_format
from scoring.validity import invalid_ratio
from ui.components.dynamic import _score_call
from ui.utils import _lazy_func
from utils.utils import logger

if TYPE_CHECKING:
    from collections.abc import Callable


from ui.components.analysis import _dataframe_analysis

_LAZY_FUNCS: dict[str, Callable[[], Any]] = {
    "VSTRF_score": _lazy_func(
        _score_call,
        func=invalid_ratio,
        key="VSTRF",
        lazy_func_args={"df": "VSTRF_res"},
    ),
}


def render() -> None:
    _headers()
    st.divider()
    _string_format()


def _headers() -> None:
    st.title("Validity")
    st.markdown("#### Analysis of the validity of the database.")


# Analysis function that takes the edited DataFrame and returns results
def _string_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
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
            properties = [p.strip() for p in row["Properties"].split(",") if p.strip()]
            case_insensitive = row["Ignore case"]
            multiline = row["Multiline"]
            dotall = row["Dotall"]

            flags = 0
            if case_insensitive:
                flags |= re.IGNORECASE
            if multiline:
                flags |= re.MULTILINE
            if dotall:
                flags |= re.DOTALL

            pattern = re.compile(row["Pattern"], flags)

            results = check_string_format(
                session,
                entity,
                label,
                properties,
                pattern,
                case_insensitive,
                multiline,
                dotall,
            )
            if results:
                analysis.extend(results)
        except re.error as e:
            errors.append(f"Line {idx + 1}: Invalid regex - {e}")
        except Exception as e:
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    return analysis if analysis else None


def _string_format() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Entity",
            "Label(s) / Type",
            "Properties",
            "Pattern",
            "Ignore case",
            "Multiline",
            "Dotall",
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
            "Properties": st.column_config.TextColumn(
                "Properties",
                help="Properties separated by a comma.",
                required=True,
            ),
            "Pattern": st.column_config.TextColumn(
                "Regex Pattern",
                help="https://neo4j.com/docs/cypher-manual/current/expressions/predicates/string-operators/#regular-expressions",
                required=True,
            ),
            "Ignore case": st.column_config.CheckboxColumn(
                "Ignore case",
                default=False,
            ),
            "Multiline": st.column_config.CheckboxColumn(
                "Multiline",
                default=False,
            ),
            "Dotall": st.column_config.CheckboxColumn(
                "Dotall",
                default=False,
            ),
        },
    }

    _dataframe_analysis(
        section_name="Analysis string properties format.",
        description="It checks the entities which do not match the Regex pattern.",
        key="VSTRF",
        analysis_func=_string_analyze,
        df_template=df_template,
        editor_config=editor_config,
        progress_message="Analyzing string formats...",
        button_label="Analyse string format",
    )

    st.markdown(
        "How it works: column `count` is the number of entities of the Label(s) / Type."
        "The column `invalid` is the number of nodes with the property who's not NULL"
        "and don't match the format specified by the Regex pattern.",
    )
