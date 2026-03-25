import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from ui.enums import WidgetState


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
