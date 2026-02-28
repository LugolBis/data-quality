from typing import Any

import numpy as np
import pandas as pd


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

    return _weighted_score(
        df,
        score_label=hhi,
        group_by=group_by,
        population=population,
    )


def nodes_degree(
    df: pd.DataFrame | None,
) -> float:
    """
    Use it only to compute a quality score on nodes degree statistics.

    :param df: The DataFrame who's containing label nodes degree statistics.
    :type df: Optional[pd.DataFrame]
    :return: A quality score between `0.0` and `1.0`.
    :rtype: float
    """
    if df is None:
        return 1.0
    df_c: pd.DataFrame = df.copy()

    # Step 1 : Compute S_conn
    df_c["pre_conn"] = np.where(df_c["median"] > 0, 0.5, 0.0)
    s_conn: pd.Series = df_c.groupby("label")["pre_conn"].sum()

    # Step 2 : Compute S_flux
    pivot: pd.DataFrame = df_c.pivot_table(
        index="label",
        columns="degree",
        values="average",
        aggfunc="mean",
    ).reindex(columns=["Degree.INCOMING", "Degree.OUTCOMING"], fill_value=0)

    s_flux: pd.Series[Any] = (
        1
        - (pivot["Degree.INCOMING"] - pivot["Degree.OUTCOMING"])
        .abs()
        .div(
            (pivot["Degree.INCOMING"] + pivot["Degree.OUTCOMING"]).replace(0, pd.NA),
        )
    ).fillna(0)

    # Step 3 : Compute S_stab
    df_c["CV"] = (
        (df_c["standard_deviation"]).div((df_c["average"]).replace(0, pd.NA)).fillna(2)
    )
    df_c["s_cv"] = np.where(df_c["CV"] <= 1, 1 - df_c["CV"], 0.0)

    s_stab: pd.Series[Any] = df_c.groupby("label")["s_cv"].sum() / 2

    # Step 4 : Compute Label score
    score_label: pd.Series[Any] = (s_conn + s_flux + s_stab) / 3

    # Step 5 : Compute Weighted score
    return _weighted_score(df_c, score_label, group_by="label", population="count")


def _weighted_score(
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
