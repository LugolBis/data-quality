import re
from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st

from models.enums import Entity
from models.utils import get_label
from quality.enums import DateFmt, SetRelation
from quality.validity import (
    check_date_format,
    check_string_format,
    labeling_set,
    numerical_interval,
)
from scoring.validity import invalid_ratio
from ui.components.dynamic import _score_call
from ui.pages.quality.configs import (
    _COL_ENTITY,
    _COL_LABELS,
    _COL_LABELS_TYPE,
    _COL_PROPERTIES,
)
from ui.pages.quality.utils import (
    _CONDITIONAL_COL_CONFIG,
    _CONDITIONAL_DF_TEMPLATE,
    _generate_condition,
)
from ui.utils import _lazy_func
from utils.utils import logger

if TYPE_CHECKING:
    from collections.abc import Callable

    from quality.types import Condition


from streamlit import session_state as app_st

from ui.components.analysis import _dataframe_analysis

_LAZY_FUNCS: dict[str, Callable[[], Any]] = {
    "VSFMT_score": _lazy_func(
        _score_call,
        func=invalid_ratio,
        key="VSFMT",
        lazy_func_args={"df": "VSFMT_res"},
    ),
}
_CONDITION_EDITOR_KEY: str = "_ql_validity_condition_editor_key"


def render() -> None:
    _headers()
    st.divider()
    _string_format()
    st.divider()
    _date_format()
    st.divider()
    _lblg_set_render()
    st.divider()
    _interval_render()


def _headers() -> None:
    st.title("Validity")
    st.markdown("#### Analysis of the validity of the database.")


# Analysis function that takes the edited DataFrame and returns results
def _string_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:  # noqa: C901
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
            properties = row["Properties"]
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
                get_label(labels),
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


def _date_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
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
            properties: list[str] = row["Properties"]
            date_fmt: DateFmt = DateFmt(row["Date format"])
            skip_null: bool = row["Skip null values"]

            results = check_date_format(
                session,
                entity,
                get_label(labels),
                properties,
                date_fmt,
                skip_null,
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


def _lblg_set_analyze(dict_rows: dict[str, Any]) -> list[dict] | None:
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
            set_rel: SetRelation = SetRelation(row["Set relation"])
            cmp_list: list[str] = row["Label set"]

            result = labeling_set(
                session,
                get_label(labels),
                set_rel,
                set(cmp_list),
            )
            if result:
                analysis.append(result)
        except Exception as e:
            logger.error(e)
            errors.append(f"Line {idx + 1}: Unexpected error - {e}")

    if errors:
        for err in errors:
            st.error(err)

    return analysis if analysis else None


def _interval_analyze(  # noqa: C901
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
            properties: list[str] = row["Properties"]
            min_value: float = row["Min value"]
            max_value: float = row["Max value"]
            cond_name: str | None = row["Condition name"]

            condition: Condition | None = None
            if cond_name:
                condition_gen = _generate_condition(df_cond, cond_name, [])
                if isinstance(condition_gen, str):
                    errors.append(f"Line {idx + 1}: {condition_gen}")
                    continue
                condition = condition_gen

            results = numerical_interval(
                session,
                entity,
                get_label(labels),
                set(properties),
                min_value,
                max_value,
                condition,
            )
            if results:
                analysis.extend(results)
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
            "Entity": _COL_ENTITY,
            "Label(s) / Type": _COL_LABELS_TYPE,
            "Properties": _COL_PROPERTIES,
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
        key="VSFMT",
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


def _date_format() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Entity",
            "Label(s) / Type",
            "Properties",
            "Date format",
            "Skip null values",
        ],
    )

    # Configuration for the data editor
    editor_config = {
        "num_rows": "dynamic",
        "column_config": {
            "Entity": _COL_ENTITY,
            "Label(s) / Type": _COL_LABELS_TYPE,
            "Properties": _COL_PROPERTIES,
            "Date format": st.column_config.SelectboxColumn(
                "Date format",
                options=[str(fmt) for fmt in DateFmt],
                required=True,
            ),
            "Skip null values": st.column_config.CheckboxColumn(
                "Skip null values",
                default=True,
            ),
        },
    }

    _dataframe_analysis(
        section_name="Analysis date properties format.",
        description="It checks the entities which do not match the date format.",
        key="VDFMT",
        analysis_func=_date_analyze,
        df_template=df_template,
        editor_config=editor_config,
    )


def _lblg_set_render() -> None:
    # Template DataFrame with predefined columns
    df_template = pd.DataFrame(
        columns=[
            "Label(s)",
            "Set relation",
            "Label set",
        ],
    )

    # Configuration for the data editor
    editor_config = {
        "num_rows": "dynamic",
        "column_config": {
            "Label(s)": _COL_LABELS,
            "Set relation": st.column_config.SelectboxColumn(
                label="Entity",
                help="Choose a set realtion to compare the nodes label set.",
                options=[sr.value for sr in SetRelation],
                required=True,
            ),
            "Label set": st.column_config.ListColumn(
                "Label set",
                help=(
                    "Enter the set of labels to be compared with the ones"
                    " of matched nodes."
                ),
                required=True,
            ),
        },
    }

    _dataframe_analysis(
        section_name="Analysis set relation between labels.",
        description=(
            "It checks for a given label set if all the label set from nodes who match"
            " it respect a relation set with another defined set."
        ),
        key="VLBS",
        analysis_func=_lblg_set_analyze,
        df_template=df_template,
        editor_config=editor_config,
    )


def _interval_render() -> None:
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
            "Properties",
            "Min value",
            "Max value",
            "Condition name",
        ],
    )

    # Configuration for the data editor
    editor_config = {
        "num_rows": "dynamic",
        "column_config": {
            "Entity": _COL_ENTITY,
            "Label(s) / Type": _COL_LABELS_TYPE,
            "Properties": _COL_PROPERTIES,
            "Min value": st.column_config.NumberColumn(
                "Min value",
                help="Min accepted value (included in the interval).",
                required=True,
            ),
            "Max value": st.column_config.NumberColumn(
                "Max value",
                help="Max accepted value (included in the interval).",
                required=True,
            ),
            "Condition name": st.column_config.TextColumn(
                "Condition name",
                help=(
                    "Select the name of the condition written in the Condition editor."
                ),
            ),
        },
    }

    _dataframe_analysis(
        section_name="Analysis properties interval",
        description=(
            "It checks for a given label _L_ of the chosen entity if all of it's"
            " occurencies have their numerical properties in the choosen interval."
            " You can filter the matches with the (optional) condition."
        ),
        key="VNIC",
        analysis_func=_interval_analyze,
        df_template=df_template,
        editor_config=editor_config,
        lazy_renders=[lazy_render],
    )
