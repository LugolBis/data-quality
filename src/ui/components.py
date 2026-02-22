from typing import Any, Callable, Optional

import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from driver.neo4j_driver import Neo4jSession
from ui.enums import AnalysisState
from ui.utils import _to_dataframe
from utils.utils import some


def _static_analysis(
    section_name: str,
    description: str,
    button_label: str,
    func: Callable[..., Optional[Any]],
    func_args: dict[str, Any] | None = None,
    flatten: list[str] | None = None,
) -> None:
    """
    A Streamlit component for static analysis who needs to be persistent.

    :param section_name: Markdown text.
    :type section_name: str
    :param description: Markdown text to describe the section.
    :type description: str
    :param button_label: Text to be display on the button.
    :type button_label: str
    :param func: Analysis function.
    :type func: Callable[..., Optional[Any]]
    :param func_args: If necessary arguments to the function.
    :type func_args: dict[str, Any] | None
    :param flatten: List of properties of the result of `func` who needs to be flatten to be converted as a `pandas.DataFrame`.
    :type flatten: list[str] | None
    """
    key = f"_static_res_{func.__name__}"

    if func_args is None:
        func_args = {}

    if flatten is None:
        flatten = []

    st.markdown(section_name)
    st.markdown(description)

    session = app_st["db_session"]

    _button(button_label, key, func, session, func_args)

    _display_df(key, flatten)


def _dynamic_analysis(
    section_name: str,
    description: str,
    button_label: str,
    lazy_renders: list[Callable[[], Any]],
    func: Callable[..., Optional[Any]],
    func_args: dict[str, Any] | None = None,
    lazy_func_args: dict[str, str] | None = None,
    flatten: list[str] | None = None,
) -> None:
    """
    A Streamlit component for dynamic analysis who needs to be persistent.\n
    **Note** : the main difference with `_static_analysis` is that you can specify\n
        a list of **lazy** Streamlit functions constructed with `_lazy_render()`\n
        to specify Streamlit objects to be rendered in the analysis.

    :param section_name: Markdown text.
    :type section_name: str
    :param description: Markdown text to describe the section.
    :type description: str
    :param button_label: Text to be display on the button.
    :type button_label: str
    :param lazy_renders: Description
    :type lazy_renders: list[Callable[[], Any]]
    :param func: Analysis function.
    :type func: Callable[..., Optional[Any]]
    :param func_args: If necessary arguments to the function.
    :type func_args: dict[str, Any] | None
    :param lazy_func_args: Dict of lazy arguments who need to retrieved with `st.session_state[value]`. The keys needs to match the arguments of `func` and the value are used to retrieve them from the session state.
    :type lazy_func_args: dict[str, str] | None
    :param flatten: List of properties of the result of `func` who needs to be flatten to be converted as a `pandas.DataFrame`.
    :type flatten: list[str] | None
    Docstring for _dynamic_analysis
    """
    key = f"_dynamic_res_{func.__name__}"

    st.markdown(section_name)
    st.markdown(description)

    container = st.container()

    with container:
        for lazy_render in lazy_renders:
            lazy_render()

    session = app_st["db_session"]

    if func_args is None:
        func_args = dict()

    if some(lazy_func_args):
        func_args.update({key: app_st[value] for key, value in lazy_func_args.items()})

    if flatten is None:
        flatten = []

    _button(button_label, key, func, session, func_args)

    _display_df(key, flatten)


def _button(
    button_label: str,
    key: str,
    func: Callable[..., Optional[Any]],
    session: Neo4jSession,
    func_args: dict[str, Any],
) -> None:
    # Initialize state
    if key not in st.session_state:
        st.session_state[key] = {
            "state": AnalysisState.IDLE,
            "data": None,
        }

    if st.button(button_label, key=f"{key}_button"):
        try:
            with st.spinner("Analysis in progress..."):
                results = func(session, **func_args)

            if some(results):
                st.session_state[key] = {
                    "state": AnalysisState.SUCCESS,
                    "data": results,
                }
            else:
                st.session_state[key] = {"state": AnalysisState.EMPTY, "data": None}
        except Exception as error:
            st.session_state[key] = {"state": AnalysisState.ERROR, "data": error}


def _display_df(key: str, flatten: list[str]) -> None:
    # Persistent display
    stored = st.session_state[key]

    match stored["state"]:
        case AnalysisState.ERROR:
            st.exception(stored["data"])
        case AnalysisState.EMPTY:
            st.success("There isn't any data detected.")
        case AnalysisState.SUCCESS:
            df: Optional[pd.DataFrame] = _to_dataframe(
                objects=stored["data"], flatten=flatten
            )

            if some(df):
                st.warning("Result of the analysis:")
                st.dataframe(df, use_container_width=True)
        case _:
            pass
