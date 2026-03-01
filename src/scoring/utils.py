from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    import pandas as pd


def _weighted(
    df: pd.DataFrame,
    score_label: pd.Series[Any],
    group_by: str = "label",
    population: str = "count",
) -> float:
    """
    Compute a weighted score such as :
     **SUM(Score_label * Count_label) / SUM(Count_label)**

    :param df: The DataFrame who contains the `group_by` and `population` columns.
    :type df: pd.DataFrame
    :param score_label: The score computed for each label
     (which name is in the `group_by` column).
    :type score_label: pd.Series[Any]
    :param group_by: The column used to aggregate the computed score of `score_label`.
    :type group_by: str
    :param population: The column who contains weight of each value of `score_label`.
    :type population: str
    :return: Return a Quality score.
    :rtype: float
    """
    first_rows: pd.DataFrame = df.drop_duplicates(subset=group_by)
    count_label: int = first_rows[population].sum()
    weighted: pd.Series[Any] = score_label * first_rows.set_index(group_by)[population]

    return round(weighted.sum() / count_label, 4)
