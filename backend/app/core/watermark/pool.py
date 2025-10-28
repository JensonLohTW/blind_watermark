"""AutoPool 相容封裝。"""

from __future__ import annotations

from typing import Iterable, Sequence, TypeVar

from .runtime import AutoPool as _AutoPool

T = TypeVar("T")
R = TypeVar("R")


class AutoPool(_AutoPool):
    """維持舊版 API 的 Alias。"""

    def map(self, func, args: Iterable[T]) -> Sequence[R]:  # type: ignore[override]
        return super().map(func, args)

