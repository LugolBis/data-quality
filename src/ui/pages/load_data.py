from pathlib import Path
from typing import Any, Callable, Tuple

import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from load.enums import LoadResult
from load.neo4j import load_from_csv, load_from_dump, load_from_script
from ui.components import _button
from ui.enums import LoadMethod, WidgetState
from utils.utils import logger


def render() -> None:
    _headers()
    st.divider()
    _main()


def _headers() -> None:
    st.title("Load Data")
    st.markdown("#### Load data into the `Neo4j` database.")


def _main() -> None:
    key: str = "_load_data_result"

    def clear_result():
        app_st[key] = {"state": WidgetState.IDLE}

    method: LoadMethod = LoadMethod(
        st.selectbox(
            "Select the load method :",
            ["Cypher script", ".dump file", "CSV file"],
            key="_select_load_method",
            help="Choose a method to perform a massive import.",
            on_change=clear_result,
        )
    )

    if method in (LoadMethod.DUMP, LoadMethod.SCRIPT):
        st.text_input(
            "Enter the file path :",
            key="_load_file_path",
            placeholder="Enter the absolute file path of a single file.",
        )

    func: Callable[..., Any]
    func_args: dict[str, Any]

    match method:
        case LoadMethod.CSV:
            func, func_args = _from_csv()
        case LoadMethod.DUMP:
            func, func_args = _from_dump()
        case LoadMethod.SCRIPT:
            func, func_args = _from_script()
        case default:
            logger.error(f"Unknwon LoadMethod : {default}")
            st.exception(f"Unknwon load method : {default}")
            return

    _button(
        "Run import",
        key,
        func,
        app_st["db_session"],
        func_args,
        "Import in progress...",
    )

    stored = app_st[key]

    match stored["state"]:
        case WidgetState.ERROR:
            st.exception(stored["data"])
        case WidgetState.SUCCESS:
            _display_load(stored["data"])
        case _:
            pass


def _from_csv() -> Tuple[Callable[..., Any], dict[str, Any]]:
    func_args: dict[str, Any] = dict()
    func_args["new_db_name"] = st.text_input("New database name :")

    col1, col2 = st.columns(2)
    with col1:
        func_args["delimiter"] = st.text_input("Delimiter principal :", value=",")

    with col2:
        func_args["array_delimiter"] = st.text_input("Array delimiter :", value=";")

    col3, col4 = st.columns(2)
    with col3:
        func_args["overwrite_destination"] = st.checkbox(
            "Overwrite destination", value=True
        )

    with col4:
        func_args["verbose"] = st.checkbox("Verbose", value=True)

    func_args["nodes"] = _list_editor("Nodes files path", "_load_csv_nodes")
    func_args["relationships"] = _list_editor(
        "Relationships files path", "_load_csv_relationships"
    )

    return (load_from_csv, func_args)


def _from_dump() -> Tuple[Callable[..., Any], dict[str, Any]]:
    func_args: dict[str, Any] = dict()
    func_args["rename"] = st.text_input("[Optional] Rename the database as :")

    col1, col2 = st.columns(2)
    with col1:
        func_args["overwrite_destination"] = st.checkbox(
            "Overwrite destination", value=True
        )

    with col2:
        func_args["verbose"] = st.checkbox("Verbose", value=False)

    if func_args["rename"].strip() == "":
        func_args["rename"] = None

    func_args["dump_file_path"] = Path(app_st["_load_file_path"])

    return (load_from_dump, func_args)


def _from_script() -> Tuple[Callable[..., Any], dict[str, Any]]:
    func_args: dict[str, Any] = dict()

    func_args["new_db_name"] = st.text_input("[Optional] New database name :")

    func_args["overwrite_destination"] = st.checkbox(
        "Overwrite destination", value=True
    )

    if func_args["new_db_name"].strip() == "":
        func_args["new_db_name"] = None

    func_args["script_path"] = Path(app_st["_load_file_path"])

    return (load_from_script, func_args)


def _list_editor(label: str, key: str) -> list[str]:
    df = st.data_editor(
        pd.DataFrame({label: [""]}),
        num_rows="dynamic",
        use_container_width=True,
        key=key,
    )

    cleaned_list = (
        df[label].dropna().astype(str).str.strip().loc[lambda x: x != ""].tolist()
    )

    return cleaned_list


def _display_load(result: LoadResult) -> None:
    match result:
        case (
            LoadResult.NO_DB_HOME
            | LoadResult.LOAD_FAILED
            | LoadResult.STOP_FAILED
            | LoadResult.START_FAILED
            | LoadResult.RECOVERY_FAILED
        ):
            st.error(result.value)
        case LoadResult.RECOVERY_SUCCESS:
            st.warning(result.value)
        case LoadResult.LOAD_SUCCESS:
            st.success("Successfully import the database.")
