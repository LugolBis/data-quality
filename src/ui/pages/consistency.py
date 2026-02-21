import re
from typing import Optional

import pandas as pd
import streamlit as st
from streamlit import session_state as app_st

from quality.consistency import check_properties_type, check_string_format
from quality.enums import Entity
from quality.types import PairPropertiesType, TextFormat
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

    df: pd.DataFrame = pd.DataFrame(
        {
            "Entity": pd.Series(dtype="string"),
            "Label(s) / Type": pd.Series(dtype="string"),
            "Properties": pd.Series(dtype="string"),
            "Pattern": pd.Series(dtype="string"),
            "Ignore case": pd.Series(dtype="bool"),
            "Multiline": pd.Series(dtype="bool"),
            "Dotall": pd.Series(dtype="bool"),
        }
    )

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "Entity": st.column_config.SelectboxColumn(
                label="Entity",
                help="Choose the kind of Neo4j entity.",
                options=["NODE", "RELATIONSHIP"],
                required=True,
            ),
            "Label(s) / Type": st.column_config.TextColumn(
                "Label(s) / Type",
                help="You can select multiple labels by separate them with a '&' like in Neo4j queries.",
                required=True,
            ),
            "Properties": st.column_config.TextColumn(
                "Properties",
                help="Properties separated by a comma.",
                required=True,
            ),
            "Regex Pattern": st.column_config.TextColumn(
                "Pattern",
                help="https://neo4j.com/docs/cypher-manual/current/expressions/predicates/string-operators/#regular-expressions",
                required=True,
            ),
            "Ignore case": st.column_config.CheckboxColumn(
                "Ignore case",
                default=False,
            ),
            "Multiline": st.column_config.CheckboxColumn(
                "Multiline",
                default=False,
            ),
            "Dotall": st.column_config.CheckboxColumn(
                "Dotall",
                default=False,
            ),
        },
    )

    button: bool = st.button("Analyse string format")
    if button:
        analysis: list[TextFormat] = []
        for idx, row in edited_df.iterrows():
            try:
                case_insensitive, multiline, dotall = (
                    row["Ignore case"],
                    row["Multiline"],
                    row["Dotall"],
                )

                flags = 0
                if case_insensitive:
                    flags |= re.IGNORECASE
                if multiline:
                    flags |= re.MULTILINE
                if dotall:
                    flags |= re.DOTALL

                entity = Entity(row["Entity"])
                label = row["Label(s) / Type"]
                properties = [
                    p.strip() for p in row["Properties"].split(",") if p.strip()
                ]
                pattern = re.compile(row["Pattern"], flags)

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

                if results:
                    analysis.extend(results)

            except re.error as error:
                st.error(f"Invalid Regex : {error}")

            except Exception as error:
                st.exception(error)

        if len(analysis) == 0:
            st.success("There isn't any inconsistent data detected.")
        else:
            st.warning(f"There is {len(analysis)} inconsistant values :")
            st.dataframe(_to_dataframe(analysis), use_container_width=True)

            explanation: str = (
                "How it works : column `count` is the number of entities of the Label(s) / Type. "
                "And the column `invalid` is the number of nodes with the property who's not NULL "
                "and don't match the format specified by the Regex pattern."
            )
            st.markdown(explanation)


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
