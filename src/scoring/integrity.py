from typing import TYPE_CHECKING, Any

from scoring.utils import _weighted

if TYPE_CHECKING:
    import pandas as pd


def pair_label_ratio(
    df: pd.DataFrame | None,
    df_cached: pd.DataFrame,
    group_by: str = "label",
    population: str = "count",
) -> float:
    if df is None:
        return 1.00

    lines_per_label: pd.DataFrame = df.groupby(group_by).count()
    # TODO! Count nodes per label
    size = len(df)
    entities = df_cached[population].sum()
    return size / ((entities * (entities - 1)) / 2)


def weighted_hhi(
    df: pd.DataFrame | None,
    group_by: str,
    counted: str,
    population: str = "count",
) -> float:
    """
    Compute a Weighted score based on HHI score.

    :param df: Data to analyze.
    :type df: Optional[pd.DataFrame]
    :param group_by: Column to be used to group by on.
    :type group_by: str
    :param counted: Column to get the number of tracked pattern
     (like number of properties, etc...)
    :type counted: str
    :param population: The number of elements in which `counted` is involved.
    :type population: str
    :return: A quality score between `0.0` and `1.0`.
    :rtype: float
    """

    if df is None or df.empty:
        return 1.0

    percent: pd.Series[Any] = df[counted] / df[population]
    hhi: pd.Series[Any] = percent.pow(2).groupby(df[group_by]).sum()

    return _weighted(
        df,
        score_label=hhi,
        group_by=group_by,
        population=population,
    )
