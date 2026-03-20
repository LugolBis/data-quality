from functools import partial
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Callable


def _config_page(
    section: str,
    title: str,
    function: Callable[..., None],
) -> dict[str, Any]:
    """
    Generate the configuration for a `StreamlitPage`.

    :param function: Function used to render a page.
    :type function: Callable[..., None]
    :return: A dictionnary of the arguments required by `st.Page()`.
    :rtype: dict[str, Any]
    """

    url_path: str = f"{section.replace(' ', '_')}_{title.lower()}"

    return {
        "page": function,
        "title": title,
        "url_path": url_path,
    }


def _lazy_func(call: Callable[..., Any], *args, **kwargs) -> Callable[[], Any]:  # noqa: ANN002, ANN003
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


_SIMILARITY_SLIDER = (
    0.0,
    0.05,
    0.1,
    0.15,
    0.2,
    0.25,
    0.3,
    0.35,
    0.4,
    0.45,
    0.5,
    0.55,
    0.6,
    0.65,
    0.7,
    0.75,
    0.8,
    0.85,
    0.9,
    0.95,
    1.0,
)

_THRESHOLD_SLIDER = tuple(round(0.05 * x, 2) for x in range(-60, 61))
