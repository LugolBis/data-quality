from dataclasses import asdict, is_dataclass
from math import nan, sqrt
from typing import Any, Iterable, List, Optional

import pandas as pd

from quality.enums import Entity
from quality.types import Statistics
from utils.utils import logger


def _build_match(entity_type: Entity, label_str: str, alias: str = "e") -> str:
    match entity_type:
        case Entity.NODE:
            return f"MATCH ({alias}:{label_str}) "
        case Entity.RELATIONSHIP:
            return f"MATCH ()-[{alias}:{label_str}]->() "
        case default:
            logger.error(f"Unknown entity : {default}")
            return f"// Unknown entity {default}\nMATCH ({alias}:{label_str}) "


def _format_label(iterable: Iterable[str]) -> str:
    return "&".join(sorted(iterable))


def _compute_statistics(data: list[int | float]) -> Optional[Statistics]:
    if len(data) < 1:
        return None
    sorted_data = sorted(data)
    n = len(sorted_data)

    count = n
    limits = (sorted_data[0], sorted_data[-1])
    sum_ = sum(sorted_data)
    average = sum(sorted_data) / n

    # Variance (population)
    variance = sum((x - average) ** 2 for x in sorted_data) / n
    standard_deviation = sqrt(variance)

    # Median (Q2)
    median = _compute_median(sorted_data)
    q2 = median

    # Quartiles (median of halves method, not including the median if n odd)
    if n % 2 == 0:
        lower_half = sorted_data[: n // 2]
        upper_half = sorted_data[n // 2 :]
    else:
        lower_half = sorted_data[: n // 2]
        upper_half = sorted_data[n // 2 + 1 :]

    q1 = _compute_median(lower_half)
    q3 = _compute_median(upper_half)

    return Statistics(
        count,
        limits,
        sum_,
        average,
        median,
        variance,
        standard_deviation,
        q1,
        q2,
        q3,
    )


def _compute_median(sorted_values: list[int | float]) -> float:
    try:
        m = len(sorted_values)
        mid = m // 2
        if m % 2 == 0:
            return (sorted_values[mid - 1] + sorted_values[mid]) / 2
        else:
            return sorted_values[mid]
    except IndexError:
        return nan


def _to_dataframe(
    objects: List[Any], flatten: List[str] = []
) -> Optional[pd.DataFrame]:
    """
    Convert a list of Python `@dataclass` object into a `pandas.DataFrame`.

    :param objects: A list of Python objects.
    :type objects: List[Any]
    :param flatten: The list of parameters/fields who needs to be flattened.
    :type flatten: List[str]
    :return: A `pandas.DataFrame`.
    :rtype: DataFrame
    """

    if not objects:
        return pd.DataFrame()

    if not is_dataclass(objects[0]):
        logger.error(f"The objects not contains @dataclass objects : {type(objects)}")
        return None

    records = [asdict(obj) for obj in objects]
    df = pd.DataFrame(records)

    # Explode columns if needed
    for col in flatten:
        if col not in df.columns:
            continue

        # If the column contains list[] it explode it first
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df = df.explode(col, ignore_index=True)

        # If the column contains dict[] it expands keys as columns
        if df[col].apply(lambda x: isinstance(x, dict)).any():
            expanded = pd.json_normalize(df[col])  # type: ignore
            expanded.columns = [f"{col}_{k}" for k in expanded.columns]

            df = df.drop(columns=[col]).reset_index(drop=True)
            expanded = expanded.reset_index(drop=True)

            df = pd.concat([df, expanded], axis=1)

    return df
