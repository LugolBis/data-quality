from typing import TYPE_CHECKING

if TYPE_CHECKING:
    import pandas as pd


def component_anomaly_ratio(
    df: pd.DataFrame | None,
    df_cached: pd.DataFrame,
    population: str = "count",
    size_col: str = "size",
) -> float:
    """
    Compute a global quality score based on the ratio of nodes involved in anomalous components.
    Used for WCC (Isolated components) and SCC (Circular dependencies).

    :param df: Data containing flattened component details (must have a size column).
    :type df: Optional[pd.DataFrame]
    :param df_cached: Cached population data containing total element count per label.
    :type df_cached: pd.DataFrame
    :param population: Column in `df_cached` representing the total number of elements.
    :type population: str
    :param size_col: Column in `df` representing the number of nodes in the component.
    :type size_col: str
    :return: A quality score between `0.0` and `1.0`.
    :rtype: float
    """
    if df is None or df.empty:
        return 1.00

    invalid_nodes = df[size_col].sum() if size_col in df.columns else len(df)

    total_pop = df_cached[population].sum()

    if total_pop == 0:
        return 1.00

    percent = min(invalid_nodes / total_pop, 1.0)

    final_score = round(1.0 - percent, 2)

    if invalid_nodes > 0 and final_score == 1.0:
        return 0.99

    return final_score
