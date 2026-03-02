import math
from typing import Any

import numpy as np
import pandas as pd

from quality.types import Eccentricity
from scoring.utils import _weighted


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
    return _weighted(df_c, score_label, group_by="label", population="count")


def eccentricity(
    eccentricity: Eccentricity,
) -> float:
    if math.isnan(eccentricity.diameter):
        return 0.00
    return 2 * (eccentricity.radius / eccentricity.diameter) - 1.00
