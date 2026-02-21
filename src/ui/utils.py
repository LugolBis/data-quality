from dataclasses import asdict, is_dataclass
from functools import partial
from typing import Any, Callable, List, Optional
from venv import logger

import pandas as pd


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


def _config_page(function: Callable[..., None]) -> dict[str, Any]:
    """
    Generate the configuration for a `StreamlitPage`.

    :param function: Function used to render a page.
    :type function: Callable[..., None]
    :return: A dictionnary of the arguments required by `st.Page()`.
    :rtype: dict[str, Any]
    """

    module_name: str = function.__module__
    page_name: str = module_name.split(".")[-1]
    title: str = page_name.replace("_", " ").capitalize()
    url_path: str = page_name.lower()

    return {
        "page": function,
        "title": title,
        "url_path": url_path,
    }


def _lazy_render(call: Callable[..., Any], *args, **kwargs) -> Callable[[], Any]:
    """
    Wrap a Streamlit call into a lazy callable.

    :param call: A streamlit function.
    :type call: Callable[..., Any]
    :param args: Parameters to be passed to to the Streamlit function.
    :param kwargs: Extended parameters.
    :return: A lazy Streamlit function with the arguments setted.
    :rtype: Callable[[], Any]
    """
    return partial(call, *args, **kwargs)
