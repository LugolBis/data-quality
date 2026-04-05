from typing import TYPE_CHECKING

from quality.enums import BoolOperator, ConditionOp, ConditionType
from quality.types import Condition, ConditionValue

if TYPE_CHECKING:
    import pandas as pd


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
