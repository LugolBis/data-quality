from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def constraint_score(
    df: pd.DataFrame | None,
) -> float:
    if df is None or df.empty:
        return 1.00
    return 0.00
