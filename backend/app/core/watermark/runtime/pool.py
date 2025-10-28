from __future__ import annotations

from contextlib import AbstractContextManager
from typing import Callable, Iterable, Optional, Sequence, TypeVar

import multiprocessing
import sys
import warnings

T = TypeVar("T")
R = TypeVar("R")


class _CommonPool:
    def map(self, func: Callable[[T], R], args: Iterable[T]) -> Sequence[R]:
        return list(map(func, args))

    def close(self) -> None:  # pragma: no cover - for interface parity
        return None

    def join(self) -> None:  # pragma: no cover - for interface parity
        return None


class AutoPool(AbstractContextManager["AutoPool"]):
    """根據執行設定自動選擇平行化策略。"""

    def __init__(self, mode: str, processes: Optional[int]) -> None:
        if mode == "multiprocessing" and sys.platform == "win32":
            warnings.warn("multiprocessing not supported on Windows; fallback to multithreading")
            mode = "multithreading"

        if mode == "multithreading":
            from multiprocessing.dummy import Pool as ThreadPool

            self._pool = ThreadPool(processes=processes)
            self._closer = self._pool.close
            self._joiner = self._pool.join
        elif mode == "multiprocessing":
            ctx = multiprocessing.get_context("fork") if sys.platform != "win32" else multiprocessing.get_context()
            self._pool = ctx.Pool(processes=processes)
            self._closer = self._pool.close
            self._joiner = self._pool.join
        elif mode in {"vectorization", "cached"}:
            warnings.warn(f"mode '{mode}' currently behaves the same as 'common'")
            self._pool = _CommonPool()
            self._closer = self._pool.close
            self._joiner = self._pool.join
        else:
            self._pool = _CommonPool()
            self._closer = self._pool.close
            self._joiner = self._pool.join

    def map(self, func: Callable[[T], R], args: Iterable[T]) -> Sequence[R]:
        return self._pool.map(func, args)

    def __exit__(self, exc_type, exc, tb):  # type: ignore[override]
        self._closer()
        self._joiner()
        return False

