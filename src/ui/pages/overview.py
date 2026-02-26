import streamlit as st
from streamlit import session_state as app_st

from driver.neo4j_driver import Neo4jSession
from ui.components import _button
from ui.utils import _lazy_func

_SECTIONS: list[str] = [
    "Consistency",
    "Integrity",
    "Lisibility",
    "Outlier",
    "Property schema",
]

_KEY_NODE: str = "nodes_stats"
_KEY_RELATIONSHIPS: str = "rels_stats"


def render() -> None:
    _headers()
    st.divider()
    _body()


def _headers() -> None:
    st.title("Data Quality - Overview")
    st.markdown("#### Overview of the data quality of the database.")


def _body() -> None:
    key: str = "Overview"

    if key not in app_st:
        app_st[key] = _lazy_func(_run_all_analysis)

    _cached_data()
    _button("Analyze data quality", key)


def _cached_data() -> None:
    session: Neo4jSession = app_st["db_session"]

    if _KEY_NODE not in app_st:
        query = "MATCH (n) UNWIND labels(n) AS label RETURN label, COUNT(*) AS count"
        app_st[_KEY_NODE] = session.run_query(query).to_df()

    if _KEY_RELATIONSHIPS not in app_st:
        query = "MATCH ()-[r]->() RETURN type(r) as label, COUNT(*) AS count"
        app_st[_KEY_RELATIONSHIPS] = session.run_query(query).to_df()


def _run_all_analysis() -> None:
    for section in _SECTIONS:
        st.markdown(f"#### {section}")
        for key in app_st[section]:
            app_st[key]()

            # TODO! Add in each pages a new key : 'key_score' who contains the score_function used to compute the score
            # TODO! Display score here based on 'key_res' data
