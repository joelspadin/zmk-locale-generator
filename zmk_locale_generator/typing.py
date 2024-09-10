from typing import Any, TypeVar

from ruamel.yaml.comments import CommentedBase

_T = TypeVar("_T")
_K = TypeVar("_K")
_V = TypeVar("_V")


class CommentedSeq(list[_T], CommentedBase):
    """
    Type stub for ruamel.yaml.comments.CommentedSeq which can be used as a generic type.
    """


class CommentedMap(dict[_K, _V], CommentedBase):
    """
    Type stub for ruamel.yaml.comments.CommentedMap which can be used as a generic type.
    """

    def insert(
        self, pos: Any, key: _K, value: _V, comment: Any | None = None
    ) -> None: ...
