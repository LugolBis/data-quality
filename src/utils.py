from typing import Optional, TypeGuard, TypeVar

T = TypeVar("T")


def some(option: Optional[T]) -> TypeGuard[T]:
    """
    Provide a concise and safe way to to check the `option` took in input isn't a 'None' value.

    :param option: An optional value, which can be a `None` or an object of type `T`
    :type option: Optional[T]
    :return: A wrapped boolean who's bring the power of `mypy`
    :rtype: TypeGuard[T]
    """
    return option is not None
