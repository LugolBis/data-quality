from typing import TYPE_CHECKING, Any

import streamlit as st
from streamlit import session_state as app_st

from driver.neo4j_driver import Neo4jSession
from utils.utils import logger

if TYPE_CHECKING:
    from neo4j import Result
    from pandas import DataFrame


def render() -> None:
    _headers()


def _headers() -> None:
    st.title("Log in page")
    st.markdown(
        (
            "### Welcome on ***data-quality*** : a Data Quality tool designed for"
            "`Neo4j` database."
        ),
    )

    _log_in()
    st.divider()
    _query()


def _log_in() -> None:
    st.write("Getting started :")

    st.text_input("URI :", "neo4j://127.0.0.1:7687", key="uri")
    st.text_input("Username :", "neo4j", key="username")
    st.text_input("Password :", "", type="password", key="password")

    if not app_st.get("is_connected", False):
        st.text_input("Database name :", "", key="default_db")
    else:
        st.selectbox(
            "Select a database :",
            app_st["available_databases"],
            key="selected_db",
        )

    button_clicked: bool = st.button("Connect")
    container = st.container()

    if button_clicked:
        with container:
            _create_neo4j_session()

    if "login_result" in app_st:
        message = app_st["login_result"]

        with container:
            if message["type"] == "success":
                st.success(message["text"])
            elif message["type"] == "error":
                st.error(message["text"])

        del app_st["login_result"]


def _query() -> None:
    st.markdown("### Query the database :")
    st.text_input(
        "Execute only one statement :",
        placeholder="Your Cypher query",
        key="query",
    )

    button_clicked = st.button("Run query")
    container = st.container()

    if button_clicked:
        with container:
            _run_query()


def _run_query() -> None:
    if not app_st.get("is_connected", False):
        st.warning("Please connect first.")
        return

    query = app_st.get("query")

    if not query:
        st.warning("Please enter a query.")
        return

    try:
        result: Result = app_st["db_session"].run_query(query)
        df: DataFrame = result.to_df()
        st.dataframe(df)

    except Exception as error:
        logger.error(error)
        st.error("An error occurred while running the query.")


def _create_neo4j_session() -> None:
    try:
        db_name: str
        if "default_db" in app_st:
            db_name = app_st["default_db"]
            del app_st["default_db"]
        else:
            db_name = app_st["selected_db"]

        neo4j_session: Neo4jSession = Neo4jSession(
            app_st["uri"],
            app_st["username"],
            app_st["password"],
            db_name,
        )

        result: Result = neo4j_session.run_query(
            "SHOW DATABASES YIELD name RETURN name",
        )
        df: DataFrame = result.to_df()

        app_st["db_session"] = neo4j_session

        databases: list[Any] = df["name"].tolist()

        if "selected_db" not in app_st:
            app_st["selected_db"] = db_name

        app_st["available_databases"] = databases
        app_st["is_connected"] = True

        app_st["login_result"] = {
            "type": "success",
            "text": f"Connected to '{db_name}' as '{app_st['username']}'.",
        }
        st.rerun()
    except Exception as error:
        app_st["is_connected"] = False

        if "db_session" in app_st:
            del app_st["db_session"]

        logger.error(error)
        app_st["login_result"] = {
            "type": "error",
            "text": f"Failed to connect to Neo4j :\n{error}",
        }
        st.rerun()
