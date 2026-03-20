from typing import TYPE_CHECKING

import streamlit as st
from streamlit import session_state as app_st

from models.utils import format_label
from ui.components import _button, _static_score
from ui.enums import WidgetState
from ui.layout import _SECTIONS
from ui.utils import _lazy_func

if TYPE_CHECKING:
    from driver.neo4j_driver import Neo4jSession

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
    _button("Run all analysis", key)
    _render_scores()


def _cached_data() -> None:
    session: Neo4jSession = app_st["db_session"]

    query = (
        "MATCH (n) WITH labels(n) AS label, size(keys(n)) AS props  RETURN label,"
        " COUNT(*) AS count, max(props) AS count_props"
    )
    df = session.run_query(query).to_df()
    df["label"] = df["label"].apply(format_label)
    app_st[_KEY_NODE] = df

    query = (
        "MATCH ()-[r]->() WITH type(r) AS label, size(keys(r)) AS props RETURN label,"
        " COUNT(*) AS count, max(props) AS count_props"
    )
    app_st[_KEY_RELATIONSHIPS] = session.run_query(query).to_df()


def _run_all_analysis() -> None:
    for section in _SECTIONS["Data Quality"]:
        for key in app_st[section]:
            app_st[key]()


def _render_scores() -> None:
    empty = False

    for section in _SECTIONS["Data Quality"]:
        st.markdown(f"#### {section}")
        for key in app_st[section]:
            if key.endswith("_score"):
                continue

            key_res = f"{key}_res"

            if key_res in app_st:
                if app_st[key_res]["state"] != WidgetState.IDLE:
                    empty = _static_score(key) is None
            else:
                empty = True

    st.markdown("#### Final Data Quality Score :")
    if empty:
        st.warning(
            "Final score can't be computed due to missing scores."
            " Please run analysis functions to compute scores."
            " You can do it with ease by click on the button `Run all analysis`.",
        )
    else:
        score = 0
        count = 0
        for key, value in app_st.items():
            if key.endswith("_score_res"):  # type: ignore
                score += value["data"]
                count += 1
        st.metric(
            label="Final Quality score :",
            value=(score / count),
            format="percent",
            border=True,
        )
