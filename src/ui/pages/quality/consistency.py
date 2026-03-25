import re
from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from models.enums import Entity
from models.utils import to_dataframe
from quality.consistency import check_string_format
from scoring.consistency import invalid_ratio
from ui.components.analysis import (
    _dynamic_analysis,
)
from ui.components.dynamic import _score_call
from ui.enums import WidgetState
from ui.utils import _lazy_func

if TYPE_CHECKING:
    from collections.abc import Callable

    from driver.neo4j_driver import Neo4jSession


def render() -> None:
    _headers()
    st.divider()
    _string_format()


def _headers() -> None:
    st.title("Consistency")
    st.markdown("#### Analysis of the consistency of the database.")


def _string_format() -> None:
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

    lazy_editor = _lazy_func(
        st.data_editor,
        df_template,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
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
        key="_string_format_editor",
    )

    _dynamic_analysis(
        "Analysis string properties format.",
        "It check the entities who does'nt match the Regex pattern.",
        "CSTRF",
        lazy_renders=[lazy_editor],
        button_label="Analyse string format",
    )

    st.markdown(
        "How it works: column `count` is the number of entities of the Label(s) / Type."
        "The column `invalid` is the number of nodes with the property who's not NULL"
        "and don't match the format specified by the Regex pattern.",
    )


def _run_string_format_analysis(editor_key: str) -> None:  # noqa: C901, PLR0912
    """Analyzes string format rules defined in the data editor."""
    key_res = "CSTRF_res"
    df_edited = app_st.get(editor_key)

    if df_edited is None or len(df_edited["added_rows"]) == 0:
        app_st[key_res] = {"state": WidgetState.EMPTY, "data": None}
        return

    session: Neo4jSession = app_st["db_session"]
    analysis = []
    errors = []

    rows = df_edited["added_rows"]
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
        except Exception as e:  # noqa: BLE001
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    if analysis:
        df_result = to_dataframe(analysis)
        if df_result is not None:
            app_st[key_res] = {"state": WidgetState.SUCCESS, "data": df_result}
        else:
            app_st[key_res] = {
                "state": WidgetState.ERROR,
                "data": "Failed to convert results to DataFrame.",
            }
    else:
        app_st[key_res] = {"state": WidgetState.EMPTY, "data": None}


_LAZY_FUNCS: dict[str, Callable[[], Any]] = {
    "CSTRF": _lazy_func(
        _run_string_format_analysis,
        editor_key="_string_format_editor",
    ),
    "CSTRF_score": _lazy_func(
        _score_call,
        func=invalid_ratio,
        key="CSTRF",
        lazy_func_args={"df": "CSTRF_res"},
    ),
}
