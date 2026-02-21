from typing import Any, Callable, Optional

import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from ui.utils import _to_dataframe
from utils.utils import some


def _static_analysis(
    section_name: str,
    description: str,
    button_label: str,
    func: Callable[..., Optional[list[Any]]],
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
    :type func: Callable[..., Optional[list[Any]]]
    :param func_args: If necessary arguments to the function.
    :type func_args: dict[str, Any] | None
    :param flatten: List of properties of the result of `func` who needs to be flatten to be converted as a `pandas.DataFrame`.
    :type flatten: list[str] | None
    """
    key = f"_static_analysis_result_{func.__name__}"

    if func_args is None:
        func_args = {}

    if flatten is None:
        flatten = []

    st.markdown(section_name)
    st.markdown(description)

    session = app_st["db_session"]

    # Initialize state
    if key not in st.session_state:
        st.session_state[key] = None

    if st.button(button_label, key=f"{key}_button"):
        try:
            with st.spinner("Analysis in progress..."):
                results = func(session, **func_args)

            st.session_state[key] = results
        except Exception as error:
            st.session_state[key] = error

    # Persistent display
    stored = st.session_state[key]

    if isinstance(stored, Exception):
        st.exception(stored)
    elif stored is not None:
        if not stored:
            st.success("There isn't any inconsistent data detected.")
        else:
            df: Optional[pd.DataFrame] = _to_dataframe(objects=stored, flatten=flatten)

            if some(df):
                st.warning("Result of the analysis:")
                st.dataframe(df, use_container_width=True)


def _dynamic_analysis(
    section_name: str,
    description: str,
    button_label: str,
    lazy_renders: list[Callable[[], Any]],
    func: Callable[..., Optional[list[Any]]],
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
    :type func: Callable[..., Optional[list[Any]]]
    :param func_args: If necessary arguments to the function.
    :type func_args: dict[str, Any] | None
    :param lazy_func_args: Dict of lazy arguments who need to retrieved with `st.session_state[value]`. The keys needs to match the arguments of `func` and the value are used to retrieve them from the session state.
    :type lazy_func_args: dict[str, str] | None
    :param flatten: List of properties of the result of `func` who needs to be flatten to be converted as a `pandas.DataFrame`.
    :type flatten: list[str] | None
    Docstring for _dynamic_analysis
    """
    key = f"_static_analysis_result_{func.__name__}"

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

    # Initialize state
    if key not in st.session_state:
        st.session_state[key] = None

    if st.button(button_label, key=f"{key}_button"):
        try:
            with st.spinner("Analysis in progress..."):
                results = func(session, **func_args)

            st.session_state[key] = results
        except Exception as error:
            st.session_state[key] = error

    # Persistent display
    stored = st.session_state[key]

    if isinstance(stored, Exception):
        st.exception(stored)
    elif stored is not None:
        if not stored:
            st.success("There isn't any inconsistent data detected.")
        else:
            df: Optional[pd.DataFrame] = _to_dataframe(objects=stored, flatten=flatten)

            if some(df):
                st.warning("Result of the analysis:")
                st.dataframe(df, use_container_width=True)
