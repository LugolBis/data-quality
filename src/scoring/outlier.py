from typing import TYPE_CHECKING, Any

from scoring.utils import _weighted

if TYPE_CHECKING:
    import pandas as pd


def numerical_outlier_ratio(
    df: pd.DataFrame | None,
    df_cached: pd.DataFrame,
    group_by: str = "label",
    population: str = "count",
) -> float:
    if df is None or df.empty:
        return 1.00

    invalid: pd.Series[Any] = df.groupby(group_by).size()

    df_cached_patched = df_cached.copy()
    if group_by not in df_cached_patched.index.names:
        df_cached_patched.set_index(group_by, inplace=True, drop=False)

    total_pop: pd.Series[Any] = df_cached_patched[population].copy()

    missing_labels = invalid.index.difference(total_pop.index)
    if not missing_labels.empty:
        for lbl in missing_labels:
            df_cached_patched.loc[lbl] = {group_by: lbl, population: invalid[lbl]}

        total_pop = df_cached_patched[population]

    percent: pd.Series[Any] = invalid.reindex(total_pop.index).fillna(0) / total_pop
    percent = percent.clip(upper=1.0)

    inverted_score = _weighted(
        df_cached_patched, score_label=percent, group_by=group_by, population=population
    )

    final_score = round(1.0 - inverted_score, 2)

    return final_score
