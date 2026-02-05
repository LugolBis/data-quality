from typing import Optional, TypeGuard, TypeVar

T = TypeVar("T")


def some(option: Optional[T]) -> TypeGuard[T]:
    return option is not None
