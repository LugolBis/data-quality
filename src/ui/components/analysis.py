from typing import TYPE_CHECKING, Any

import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from models.utils import to_dataframe
from ui.components.dynamic import _button
from ui.components.static import _display_df
from ui.enums import WidgetState

if TYPE_CHECKING:
    from collections.abc import Callable


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


def _dataframe_analysis(  # noqa: PLR0913
    section_name: str,
    description: str,
    key: str,
    analysis_func: Callable[[dict[str, Any]], Any],
    df_template: pd.DataFrame | None = None,
    editor_config: dict | None = None,
    additional_controls: list[Callable[[], Any]] | None = None,
    result_to_df: bool = True,  # noqa: FBT001, FBT002
    progress_message: str = "Analysis in progress...",
    button_label: str = "Analyse",
) -> None:
    """
    Streamlit component for analysis based on an editable DataFrame.

    :param section_name: Markdown title for the section.
    :param description: Markdown description.
    :param key: Unique identifier for this component (used for state keys).
    :param analysis_func: Function that takes the edited DataFrame and returns a result.
    :param df_template: Initial DataFrame to display in the editor. Defaults to an empty
     DataFrame.
    :param editor_config: Additional keyword arguments for st.data_editor (e.g.,
     column_config, num_rows).
    :param additional_controls: List of lazy-rendered Streamlit widgets (e.g., sliders,
     selectors).
    :param result_to_df: If True, the result of analysis_func is converted to a pandas
     DataFrame using to_dataframe.
    :param progress_message: Message displayed while the analysis runs.
    :param button_label: Text on the button.
    """
    st.markdown(f"#### {key} - {section_name}")
    st.markdown(description)

    # Keys for editor and result
    editor_key = f"{key}_editor"
    result_key = f"{key}_res"

    # Initialize editor state if not present
    if df_template is None:
        df_template = pd.DataFrame()

    # Container for the editor and additional controls
    with st.container():
        # Render the data editor
        st.data_editor(
            df_template,
            key=editor_key,
            use_container_width=True,
            **(editor_config or {}),
        )

        # Render additional controls if any
        if additional_controls:
            for control in additional_controls:
                control()

    # Initialize result state
    app_st[result_key] = {
        "state": WidgetState.IDLE,
        "data": None,
    }

    # Button to trigger analysis
    if st.button(button_label, key=f"{key}_button"):
        with st.spinner(progress_message):
            df_edited = app_st.get(editor_key)
            print("\n\n\n\n", df_edited, "\n\n\n\n")

            if df_edited is None or (
                isinstance(df_edited, pd.DataFrame) and df_edited.empty
            ):
                app_st[result_key] = {
                    "state": WidgetState.EMPTY,
                    "data": None,
                }
            else:
                try:
                    result = analysis_func(df_edited)
                    if result_to_df:
                        df = to_dataframe(result)
                        if df is not None:
                            app_st[result_key] = {
                                "state": WidgetState.SUCCESS,
                                "data": df,
                            }
                        else:
                            app_st[result_key] = {
                                "state": WidgetState.ERROR,
                                "data": "Failed to convert result to DataFrame.",
                            }
                    else:
                        app_st[result_key] = {
                            "state": WidgetState.SUCCESS,
                            "data": result,
                        }
                except Exception as error:
                    app_st[result_key] = {
                        "state": WidgetState.ERROR,
                        "data": error,
                    }

    # Display result using the existing helper
    _display_df(result_key)
