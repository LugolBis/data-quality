from typing import Any, Callable, Optional

import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from driver.neo4j_driver import Neo4jSession
from quality.evaluate import ratio
from quality.types import QualityScore
from quality.utils import _to_dataframe
from ui.enums import WidgetState
from utils.utils import some


def _static_analysis(
    section_name: str,
    description: str,
    key: str,
    button_label: str = "Analyse",
) -> None:
    """
    A Streamlit component for static analysis who needs to be persistent.

    :param section_name: Markdown text.
    :type section_name: str
    :param description: Markdown text to describe the section.
    :type description: str
    :param func: Analysis function.
    :type func: Callable[..., Optional[Any]]
    :param func_args: If necessary arguments to the function.
    :type func_args: dict[str, Any] | None
    :param flatten: List of properties of the result of `func` who needs to be flatten to be converted as a `pandas.DataFrame`.
    :type flatten: list[str] | None
    :param button_label: Text to be display on the button.
    :type button_label: str
    """

    st.markdown(section_name)
    st.markdown(description)

    _button(button_label, key)

    _display_df(key)


def _dynamic_analysis(
    section_name: str,
    description: str,
    key: str,
    lazy_renders: list[Callable[[], Any]],
    button_label: str = "Analyse",
) -> None:
    """
    A Streamlit component for dynamic analysis who needs to be persistent.\n
    **Note** : the main difference with `_static_analysis` is that you can specify\n
        a list of **lazy** Streamlit functions constructed with `_lazy_func()`\n
        to specify Streamlit objects to be rendered in the analysis.

    :param section_name: Markdown text.
    :type section_name: str
    :param description: Markdown text to describe the section.
    :type description: str
    :param lazy_funcs: Description
    :type lazy_funcs: list[Callable[[], Any]]
    :param func: Analysis function.
    :type func: Callable[..., Optional[Any]]
    :param func_args: If necessary arguments to the function.
    :type func_args: dict[str, Any] | None
    :param lazy_func_args: Dict of lazy arguments who need to retrieved with `app_st[value]`. The keys needs to match the arguments of `func` and the value are used to retrieve them from the session state.
    :type lazy_func_args: dict[str, str] | None
    :param flatten: List of properties of the result of `func` who needs to be flatten to be converted as a `pandas.DataFrame`.
    :type flatten: list[str] | None
    :param button_label: Text to be display on the button.
    :type button_label: str
    """

    st.markdown(section_name)
    st.markdown(description)

    container = st.container()

    with container:
        for lazy_render in lazy_renders:
            lazy_render()

    _button(button_label, key)

    _display_df(key)


def _analyze_call(
    func: Callable[..., Any],
    key: str,
    func_args: Optional[dict[str, Any]] = None,
    lazy_func_args: Optional[dict[str, str]] = None,
    flatten: Optional[list[str]] = None,
    to_df: bool = True,
    progress_message: str = "Analysis in progress...",
) -> None:
    # TODO ! Replace 'key' by 'key_res'
    key_res = f"{key}_res"

    func_args = dict(func_args) if func_args else {}
    lazy_func_args = dict(lazy_func_args) if lazy_func_args else {}
    flatten = list(flatten) if flatten else []

    try:
        with st.spinner(progress_message):
            session: Neo4jSession = app_st["db_session"]

            func_args.update({k: app_st[v] for k, v in lazy_func_args.items()})

            results = func(session=session, **func_args)

        if some(results):
            if to_df:
                df = _to_dataframe(objects=results, flatten=flatten)

                if some(df):
                    app_st[key_res] = {"state": WidgetState.SUCCESS, "data": df}
                else:
                    app_st[key_res] = {
                        "state": WidgetState.ERROR,
                        "data": "Failed to convert the result as pandas.DataFrame during _analyze_call().",
                    }
            else:
                app_st[key_res] = {"state": WidgetState.SUCCESS, "data": results}
        else:
            app_st[key_res] = {"state": WidgetState.EMPTY, "data": None}
    except Exception as error:
        app_st[key_res] = {"state": WidgetState.ERROR, "data": error}


def _spinner_call(
    func: Callable[..., Any],
    key_res: str,
    func_args: dict[str, Any] = dict(),
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


def _display_df(key: str) -> None:
    # Persistent display
    key_res = f"{key}_res"

    match app_st[key_res]["state"]:
        case WidgetState.ERROR:
            st.exception(app_st[key_res]["data"])
        case WidgetState.EMPTY:
            st.success("There isn't any data detected.")
        case WidgetState.SUCCESS:
            if isinstance(app_st[key_res]["data"], pd.DataFrame):
                st.warning("Result of the analysis:")
                st.dataframe(app_st[key_res]["data"], use_container_width=True)
            else:
                st.error(
                    f"You can't display a pandas.DataFrame from an object of {type(app_st[key_res]['data'])}"
                )
        case _:
            pass


def _display_score(key: str, func: Callable[[pd.DataFrame], int], total: int) -> None:
    score: Optional[QualityScore]

    match app_st[key]["state"]:
        case WidgetState.EMPTY:
            score = QualityScore(total, total)
        case WidgetState.SUCCESS:
            if isinstance(app_st[key]["data"], pd.DataFrame):
                score = ratio(app_st[key]["data"], func, total)
        case _:
            pass
