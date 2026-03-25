from typing import TYPE_CHECKING, Any

import streamlit as st
from streamlit import session_state as app_st

from models.utils import to_dataframe
from ui.components.static import _display_score
from ui.enums import WidgetState
from utils.utils import some

if TYPE_CHECKING:
    from collections.abc import Callable

    from driver.neo4j_driver import Neo4jSession


def _static_score(
    key: str,
    button_label: str = "Refresh",
) -> bool | None:
    key_score: str = f"{key}_score"

    if key_score in app_st:
        app_st[key_score]()
    else:
        st.warning("This score computation isn't yet implemented.")
        return True

    col1, col2 = st.columns(2)

    with col1:
        _display_score(key)

    with col2:
        _button(
            button_label,
            key_score,
        )
    return None


def _analyze_call(  # noqa: PLR0913
    func: Callable[..., Any],
    key: str,
    func_args: dict[str, Any] | None = None,
    lazy_func_args: dict[str, str] | None = None,
    flatten: list[str] | None = None,
    to_df: bool = True,  # noqa: FBT001, FBT002
    progress_message: str = "Analysis in progress...",
) -> None:
    # TODO ! Replace 'key' by 'key_res'
    key_res = f"{key}_res"

    func_args = func_args if func_args else {}
    lazy_func_args = lazy_func_args if lazy_func_args else {}
    flatten = flatten if flatten else []

    try:
        with st.spinner(progress_message):
            session: Neo4jSession = app_st["db_session"]

            for k, v in lazy_func_args.items():
                if v in app_st:
                    func_args[k] = app_st[v]

            results = func(session=session, **func_args)

        if some(results):
            if to_df:
                df = to_dataframe(objects=results, flatten=flatten)

                if some(df):
                    app_st[key_res] = {"state": WidgetState.SUCCESS, "data": df}
                else:
                    app_st[key_res] = {
                        "state": WidgetState.ERROR,
                        "data": (
                            "Failed to convert the result as pandas.DataFrame during"
                            " _analyze_call()."
                        ),
                    }
            else:
                app_st[key_res] = {"state": WidgetState.SUCCESS, "data": results}
        else:
            app_st[key_res] = {"state": WidgetState.EMPTY, "data": None}
    except Exception as error:
        app_st[key_res] = {"state": WidgetState.ERROR, "data": error}


def _score_call(
    func: Callable[..., Any],
    key: str,
    func_args: dict[str, Any] | None = None,
    lazy_func_args: dict[str, str] | None = None,
    progress_message: str = "Compute Quality score...",
) -> None:
    func_args = dict(func_args) if func_args else {}
    lazy_func_args = dict(lazy_func_args) if lazy_func_args else {}

    key_score_res: str = f"{key}_score_res"

    try:
        with st.spinner(progress_message):
            for k, v in lazy_func_args.items():
                if v in app_st:
                    if v.endswith("_res"):
                        func_args[k] = app_st[v]["data"]
                    else:
                        func_args[k] = app_st[v]

            score = func(**func_args)

        app_st[key_score_res] = {"state": WidgetState.SUCCESS, "data": score}
    except Exception as error:
        app_st[key_score_res] = {"state": WidgetState.ERROR, "data": error}


def _spinner_call(
    func: Callable[..., Any],
    key_res: str,
    func_args: dict[str, Any] = dict(),  # noqa: B006, C408
    progress_message: str = "Work in progress...",
) -> None:
    try:
        with st.spinner(progress_message):
            session: Neo4jSession = app_st["db_session"]

            result = func(session=session, **func_args)

            if result is not None:
                app_st[key_res] = {"state": WidgetState.SUCCESS, "data": result}
            else:
                app_st[key_res] = {"state": WidgetState.EMPTY, "data": None}
    except Exception as error:
        app_st[key_res] = {"state": WidgetState.ERROR, "data": error}


def _button(
    button_label: str,
    key: str,
) -> None:
    # Initialize state
    key_res = f"{key}_res"

    if key_res not in app_st:
        app_st[key_res] = {
            "state": WidgetState.IDLE,
            "data": None,
        }

    if st.button(button_label, key=f"{key}_button"):
        app_st[key]()
