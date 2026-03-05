from typing import TYPE_CHECKING, Any

from scoring.utils import _weighted

if TYPE_CHECKING:
    import pandas as pd


def numerical_outlier_ratio(
    df: pd.DataFrame | None,
    df_cached: pd.DataFrame,
    group_by: str = "label",
    population: str = "count",
    outlier_count: str = "outlier_count",
) -> float:
    """
    Compute a Weighted score based on the ratio of numerical outliers.

    :param df: Data containing detected outliers per label and property.
    :type df: Optional[pd.DataFrame]
    :param df_cached: Cached population data containing total element count per label.
    :type df_cached: pd.DataFrame
    :param group_by: Column to be used to group by on (e.g., 'label').
    :type group_by: str
    :param population: Column in `df_cached` representing the total number of elements.
    :type population: str
    :param outlier_count: Column in `df` representing the number of detected outliers.
    :type outlier_count: str
    :return: A quality score between `0.0` and `1.0`.
    :rtype: float
    """
    if df is None or df.empty:
        return 1.00

    invalid: pd.Series[Any] = df.groupby(group_by)[outlier_count].sum()

    total_pop: pd.Series[Any] = df_cached[population].copy()
    total_pop.index = df_cached[group_by]

    percent: pd.Series[Any] = (invalid / total_pop).fillna(0.00).clip(upper=1.0)

    inverted_score = _weighted(
        df_cached,
        score_label=percent,
        group_by=group_by,
        population=population,
    )

    return round(1.0 - inverted_score, 2)
