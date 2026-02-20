import re
from typing import Optional

import streamlit as st
from streamlit import session_state as app_st

from quality.consistency import check_properties_type, check_string_format
from quality.types import Entity, PairPropertiesType, TextFormat
from ui.utils import _to_dataframe


def render() -> None:
    _headers()
    st.divider()
    _string_format()
    st.divider()
    _properties_type()


def _headers() -> None:
    st.title("Consistency")
    st.markdown("#### Analysis of the consistency of the database.")


def _string_format() -> None:
    st.markdown("#### Analysis string properties format.")
    st.write(
        "It check the entities who does'nt respect the format specified by the Regex pattern."
    )

    session = app_st["db_session"]

    entity = st.selectbox(
        "Choose the kind of Neo4j entity :",
        options=list(Entity),
        format_func=lambda e: e.name,
    )

    label = st.text_input(
        "Label(s) / Type :",
        help="You can select multiple labels by separate them with a '&' like in Neo4j queries.",
    )

    properties_input = st.text_input(
        "Properties (separated by a comma)", placeholder="name, age, ..."
    )

    properties = [p.strip() for p in properties_input.split(",") if p.strip()]

    pattern_input = st.text_input(
        "Regex pattern :",
        placeholder=r"^[A-Z].*",
        help="https://neo4j.com/docs/cypher-manual/current/expressions/predicates/string-operators/#regular-expressions",
    )

    col1, col2, col3 = st.columns(3)

    with col1:
        case_insensitive = st.checkbox("Ignore case")

    with col2:
        multiline = st.checkbox("Multiline")

    with col3:
        dotall = st.checkbox("Dotall")

    button: bool = st.button("Analyse string format")
    if button:
        if not pattern_input:
            st.warning("Please enter a regex pattern.")
            return None

        try:
            flags = 0
            if case_insensitive:
                flags |= re.IGNORECASE
            if multiline:
                flags |= re.MULTILINE
            if dotall:
                flags |= re.DOTALL

            pattern = re.compile(pattern_input, flags)

            with st.spinner("Analysis in progress..."):
                results: Optional[list[TextFormat]] = check_string_format(
                    session,
                    entity,
                    label,
                    properties,
                    pattern,
                    case_insensitive,
                    multiline,
                    dotall,
                )

            if not results:
                st.success("There isn't any inconsistent data detected.")
            else:
                st.warning(f"There is {len(results)} inconsistant values :")

                st.dataframe(_to_dataframe(results), use_container_width=True)

                explanation: str = (
                    "How it works : column `count` is the number of entities of the Label(s) / Type. "
                    "And the column `invalid` is the number of nodes with the property who's not NULL "
                    "and don't match the format specified by the Regex pattern."
                )
                st.markdown(explanation)

        except re.error as error:
            st.error(f"Invalid Regex : {error}")

        except Exception as error:
            st.exception(error)


def _properties_type() -> None:
    st.markdown("#### Analysis properties type.")
    st.markdown(
        "Check if there is any pair of **Node**/**Relationship** who has one property with different type."
    )

    session = app_st["db_session"]

    button: bool = st.button("Analyse properties type")
    if button:
        try:
            with st.spinner("Analysis in progress..."):
                results: Optional[list[PairPropertiesType]] = check_properties_type(
                    session
                )

            if not results:
                st.success("There isn't any inconsistent data detected.")
            else:
                st.warning(f"There is {len(results)} inconsistant values :")

                st.dataframe(_to_dataframe(results), use_container_width=True)

        except Exception as error:
            st.exception(error)
