from typing import Any, Callable, Iterable, TypeVar


T = TypeVar(name="T")


def unique(seq: Iterable[T], key: Callable[[T], Any] = lambda x: x) -> Iterable[T]:
    """
    Return a sequence with duplicate values removed.

    :param key: Function which returns a key to use for checking for equality.
    """
    return {key(x): x for x in seq}.values()
