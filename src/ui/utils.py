from functools import partial
from typing import Any, Callable


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


def _lazy_func(call: Callable[..., Any], *args, **kwargs) -> Callable[[], Any]:
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
