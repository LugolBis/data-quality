from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from quality.utils import _to_dataframe
from ui.enums import WidgetState
from utils.utils import some

if TYPE_CHECKING:
    from collections.abc import Callable

    from driver.neo4j_driver import Neo4jSession


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
    :param flatten: List of properties of the result of `func` who needs to be flatten
     to be converted as a `pandas.DataFrame`.
    :type flatten: list[str] | None
    :param button_label: Text to be display on the button.
    :type button_label: str
    """

    st.markdown(f"#### {key} - {section_name}")
    st.markdown(description)

    _button(button_label, key)

    _display_df(f"{key}_res")


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
    :param lazy_func_args: Dict of lazy arguments who need to retrieved with
     `app_st[value]`. The keys needs to match the arguments of `func` and the value are
      used to retrieve them from the session state.
    :type lazy_func_args: dict[str, str] | None
    :param flatten: List of properties of the result of `func` who needs to be flatten
     to be converted as a `pandas.DataFrame`.
    :type flatten: list[str] | None
    :param button_label: Text to be display on the button.
    :type button_label: str
    """

    st.markdown(f"#### {key} - {section_name}")
    st.markdown(description)

    container = st.container()

    with container:
        for lazy_render in lazy_renders:
            lazy_render()

    _button(button_label, key)

    _display_df(f"{key}_res")


def _static_score(
    key: str,
    button_label: str = "Refresh",
) -> None:
    key_score: str = f"{key}_score"
    if key_score in app_st:
        app_st[key_score]()
    else:
        st.warning("This score computation isn't yet implemented.")
        return

    col1, col2 = st.columns(2)

    with col1:
        _display_score(key)

    with col2:
        _button(
            button_label,
            key_score,
        )


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
                df = _to_dataframe(objects=results, flatten=flatten)

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


def _display_df(key_res: str) -> None:
    # Persistent display
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
                    (
                        "You can't display a pandas.DataFrame from an object of"
                        f" {type(app_st[key_res]['data'])}"
                    ),
                )
        case _:
            pass


def _display_score(key: str) -> None:
    key_res = f"{key}_score_res"
    match app_st[key_res]["state"]:
        case WidgetState.ERROR:
            st.exception(app_st[key_res]["data"])
        case WidgetState.EMPTY:
            st.success("There isn't any data detected.")
        case WidgetState.SUCCESS:
            data = app_st[key_res]["data"]
            if isinstance(data, float):
                st.metric(
                    label=f"{key} - Quality score :",
                    value=data,
                    format="percent",
                    border=True,
                )
            else:
                st.error(
                    (
                        "You can't display a quality score from an object of"
                        f" {type(data)}"
                    ),
                )
        case _:
            pass
