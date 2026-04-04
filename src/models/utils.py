from dataclasses import asdict, is_dataclass
from typing import TYPE_CHECKING, Any

import pandas as pd

from models.enums import WILDCARD, Entity
from utils.utils import logger

if TYPE_CHECKING:
    from collections.abc import Iterable


def build_match(entity_type: Entity, label_str: str, alias: str = "e") -> str:
    match entity_type:
        case Entity.NODE:
            if label_str == WILDCARD:
                return f"MATCH ({alias}) "
            return f"MATCH ({alias}:{label_str}) "
        case Entity.RELATIONSHIP:
            if label_str == WILDCARD:
                return f"MATCH ()-[{alias}]->() "
            return f"MATCH ()-[{alias}:{label_str}]->() "
        case default:
            logger.error(f"Unknown entity : {default}")
            return f"// Unknown entity {default}\nMATCH ({alias}:{label_str}) "


def format_label(iterable: Iterable[str]) -> str:
    return "&".join(sorted(iterable))


def get_label(iterable: Iterable[str]) -> str:
    """
    This function is an extension of `format_label` that support `WILDCARD`.
    """
    label_set = set(iterable)
    if WILDCARD in label_set:
        return WILDCARD
    return format_label(label_set)


def to_dataframe(
    objects: list[Any],
    flatten: list[str] | None = None,
) -> pd.DataFrame | None:
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

    if flatten is None:
        flatten = []

    # Explode columns if needed
    for col in flatten:
        if col not in df.columns:
            continue

        # If the column contains list[] it explode it first
        if df[col].apply(lambda x: isinstance(x, list)).any():
            df = df.explode(col, ignore_index=True)

        # If the column contains dict[] it expands keys as columns
        if df[col].apply(lambda x: isinstance(x, dict)).any():
            expanded = pd.json_normalize(df[col])  # ty:ignore[invalid-argument-type]
            expanded.columns = [f"{col}_{k}" for k in expanded.columns]

            df = df.drop(columns=[col]).reset_index(drop=True)
            expanded = expanded.reset_index(drop=True)

            df = pd.concat([df, expanded], axis=1)

    return df
