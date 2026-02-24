from functools import partial
from typing import Any, Callable

from driver.neo4j_driver import Neo4jSession
from ui.components import _button_call


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


def _lazy_analyze(
    key: str,
    func: Callable[..., Any],
    session: Neo4jSession,
    func_args: dict[str, Any],
    progress_message: str,
) -> Callable[[], None]:
    """
    Wrap an analyze function who's called by buttons.

    :param key: Key state of the button call.
    :type key: str
    :param func: Analyze function.
    :type func: Callable[..., Any]
    :param session: A `Neo4j` session to query the database.
    :type session: Neo4jSession
    :param func_args: Arguments to be passed to the analyze function.
    :type func_args: dict[str, Any]
    :param progress_message: Message to be display during the analyzing.
    :type progress_message: str
    :return: A lazy function.
    :rtype: Callable[[], None]
    """

    return partial(
        _button_call,
        key,
        func,
        session,
        func_args,
        progress_message,
    )
