from typing import Optional

import pandas as pd


def sum_percent(
    df: Optional[pd.DataFrame],
    population_col: str = "count",
    invalid_col: str = "invalid",
) -> float:
    """
    1. For each `p` it compute `Sp = (population_col - invalid_col) / population_col` (get a percent)
    2. Compute `result = sum(Sp) / count(p)`
    """
    if df is None or len(df) == 0:
        return 1.0
    else:
        values: int = len(df)
        sum_: float = (
            (df[population_col] - df[invalid_col]) / df[population_col]
        ).sum()
        return round(sum_ / values, 2)


def weighted_hhi(
    df: Optional[pd.DataFrame],
    group_by: str,
    counted: str,
    pop: str = "count",
) -> float:
    if df is None or df.empty:
        return 1.0

    percent = df[counted] / df[pop]
    hhi = percent.pow(2).groupby(df[group_by]).sum()

    first_rows = df.drop_duplicates(subset=group_by)
    count_label = first_rows[pop].sum()

    weighted = hhi * first_rows.set_index(group_by)[pop]

    return round(weighted.sum() / count_label, 2)
