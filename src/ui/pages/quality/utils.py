import pandas as pd
import streamlit as st
from streamlit.elements.lib.column_types import ColumnConfig

from quality.enums import BoolOperator, ConditionOp, ConditionType
from quality.types import Condition, ConditionValue

_CONDITIONAL_DF_TEMPLATE: pd.DataFrame = pd.DataFrame(
    columns=[
        "Name",
        "Property",
        "Value type",
        "Value",
        "Operator",
        "Next Op.",
        "Next condition",
    ],
)

_CONDITIONAL_COL_CONFIG: dict[str, ColumnConfig] = {
    "Name": st.column_config.TextColumn("Name", required=True),
    "Property": st.column_config.TextColumn("Property", required=True),
    "Operator": st.column_config.SelectboxColumn(
        "Operator",
        options=[e.value for e in ConditionOp],
        required=True,
    ),
    "Value type": st.column_config.SelectboxColumn(
        "Value Type",
        options=[e.value for e in ConditionType],
        required=True,
    ),
    "Value": st.column_config.TextColumn("Value", required=True),
    "Next Op.": st.column_config.SelectboxColumn(
        "Next Op.",
        options=[e.value for e in BoolOperator],
    ),
    "Next condition": st.column_config.TextColumn(
        "Next condition",
        help="Select the name of next condition.",
    ),
}


def _generate_condition(
    df_cond: pd.DataFrame,
    target_name: str,
    line_visited: list[str],
) -> Condition | str:
    if target_name in line_visited:
        return (
            "Dependency cycle detected between conditions : "
            f"{' -> '.join([str(idx) for idx in line_visited])}"
            f" -X> {target_name}"
        )
    try:
        filtered = df_cond[df_cond["Name"] == target_name]
        row = filtered.iloc[0] if not filtered.empty else None
        if row is None:
            return f"Failed to retrieve the condition called {target_name}"

        property_ = row["Property"]
        value_type = ConditionType(row["Value type"])
        value = row["Value"]
        operator = ConditionOp(row["Operator"])
        next_op = row["Next Op."]
        next_cond = row["Next condition"]

        if not isinstance(next_cond, str):
            return Condition(
                property_,
                ConditionValue(value_type, value),
                operator,
                None,
            )
        line_visited.append(target_name)
        sub_condition = _generate_condition(df_cond, next_cond, line_visited)
        if isinstance(sub_condition, str):
            return f"{target_name} <X- {next_cond} : {sub_condition}"
        return Condition(
            property_,
            ConditionValue(value_type, value),
            operator,
            (BoolOperator(next_op), sub_condition),
        )
    except Exception as e:
        return str(e)
