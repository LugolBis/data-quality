import re
from typing import Any, Callable

import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from driver.neo4j_driver import Neo4jSession
from quality.consistency import check_properties_type, check_string_format
from quality.enums import Entity
from quality.utils import _to_dataframe
from ui.components import _analyze_call, _dynamic_analysis, _static_analysis
from ui.enums import WidgetState
from ui.utils import _lazy_func


def render() -> None:
    _headers()
    st.divider()
    _string_format()
    st.divider()
    _properties_type()


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
        ]
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
                help="You can select multiple labels by separate them with a '&' like in Neo4j queries.",
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
        "#### Analysis string properties format.",
        "It check the entities who does'nt respect the format specified by the Regex pattern.",
        "Cstrf",
        lazy_renders=[lazy_editor],
        button_label="Analyse string format",
    )

    st.markdown(
        "How it works : column `count` is the number of entities of the Label(s) / Type. "
        "And the column `invalid` is the number of nodes with the property who's not NULL "
        "and don't match the format specified by the Regex pattern."
    )


def _properties_type() -> None:
    _static_analysis(
        "#### Analysis properties type.",
        "Check if there is any pair of **Node**/**Relationship** who has one property with different type.",
        "Ccpt",
    )


def _run_string_format_analysis(editor_key: str) -> None:
    """Analyse les formats de chaînes à partir des règles saisies dans le data editor."""
    key_res = "Cstrf_res"
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
        except Exception as e:
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    if analysis:
        df_result = _to_dataframe(analysis)
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
    "Ccpt": _lazy_func(_analyze_call, func=check_properties_type, key="Ccpt"),
    "Cstrf": _lazy_func(
        _run_string_format_analysis, editor_key="_string_format_editor"
    ),
}
