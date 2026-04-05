from typing import TYPE_CHECKING

import streamlit as st

if TYPE_CHECKING:
    from streamlit.elements.lib.column_types import ColumnConfig

_COL_ENTITY: ColumnConfig = st.column_config.SelectboxColumn(
    label="Entity",
    help="Choose the kind of Neo4j entity.",
    options=["NODE", "RELATIONSHIP"],
    required=True,
)

_COL_LABELS_TYPE: ColumnConfig = st.column_config.ListColumn(
    "Label(s) / Type",
    help=(
        "Select the set of labels combination, use the wildcard '_'"
        " to match any entity."
    ),
    required=True,
)

_COL_LABELS: ColumnConfig = st.column_config.ListColumn(
    "Label(s)",
    help=(
        "Select the set of labels combination, use the wildcard '_' to match any node."
    ),
    required=True,
)

_COL_ENTITY_ALIAS: ColumnConfig = st.column_config.TextColumn(
    "Entity alias",
    help=("It's the alias used by `Graph Pattern` to reference the entity."),
    required=True,
)

_COL_GRAPH_PATTERN: ColumnConfig = st.column_config.TextColumn(
    "Graph Pattern",
    required=True,
)

_COL_PROPERTIES: ColumnConfig = st.column_config.ListColumn(
    "Properties",
    help=(
        "Select the set of multivalued properties who shouldn't contains duplicates."
    ),
    required=True,
)
