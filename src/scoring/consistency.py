from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def invalid_ratio(
    df: pd.DataFrame | None,
    population: str = "count",
    invalid: str = "invalid",
) -> float:
    if df is None:
        return 1.000
    population = df[population].sum()
    return (population - df[invalid].sum()) / population


def sum_percent(
    df: pd.DataFrame | None,
    population: str = "count",
    invalid: str = "invalid",
) -> float:
    """
    1. For each `p` it compute `Sp = (population_col - invalid_col) / population_col`
     (get a percent)
    2. Compute `result = sum(Sp) / count(p)`
    """
    if df is None or len(df) == 0:
        return 1.0
    values: int = len(df)
    sum_: float = ((df[population] - df[invalid]) / df[population]).sum()
    return round(sum_ / values, 4)
