import pandas as pd


def constraint_score(
    df: pd.DataFrame | None,
) -> float:
    if df is None or df.empty:
        return 1.00
    return 0.00


def index_score(
    df: pd.DataFrame | None,
    df_cached_nodes: pd.DataFrame,
    df_cached_rels: pd.DataFrame,
    population: str = "count",
    invalid: str = "invalid",
) -> float:
    if df is None or df.empty:
        return 1.00

    cached_labels: pd.Series[list[str]] = df_cached_nodes["label"].str.split("&")
    masked_labels: set[str] = set(df["label"])

    df_filtered: pd.DataFrame = pd.concat(
        [
            df_cached_nodes[
                cached_labels.apply(
                    lambda lst: all(label not in masked_labels for label in lst),
                )
            ],
            df_cached_rels[
                df_cached_rels["label"].apply(
                    lambda lst: all(label not in masked_labels for label in lst),
                )
            ],
        ],
        ignore_index=True,
    )

    invalid_sum: int = df[invalid].sum()
    population_sum: int = df[population].sum() + df_filtered[population].sum()
    return 1.00 - (invalid_sum / population_sum)
