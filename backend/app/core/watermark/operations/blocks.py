from __future__ import annotations

from dataclasses import dataclass
from typing import Iterator, Sequence, Tuple

import numpy as np


@dataclass(frozen=True)
class BlockGeometry:
    """描述小波係數分塊後的幾何資訊。"""

    rows: int
    cols: int
    block_shape: Tuple[int, int]

    @property
    def block_num(self) -> int:
        return self.rows * self.cols

    @property
    def part_shape(self) -> Tuple[int, int]:
        return (
            self.rows * self.block_shape[0],
            self.cols * self.block_shape[1],
        )

    @classmethod
    def from_ca_shape(cls, ca_shape: Tuple[int, int], block_shape: Tuple[int, int]) -> "BlockGeometry":
        rows = ca_shape[0] // block_shape[0]
        cols = ca_shape[1] // block_shape[1]
        if rows == 0 or cols == 0:
            raise ValueError("image is too small for the configured block size")
        return cls(rows=rows, cols=cols, block_shape=block_shape)


class BlockSequence:
    """以高階介面管理區塊視圖與 shuffle 邏輯。"""

    def __init__(self, geometry: BlockGeometry, shuffle_seed: int, shuffle_width: int) -> None:
        self.geometry = geometry
        rng = np.random.RandomState(shuffle_seed)
        self._shuffle = rng.random(size=(geometry.block_num, shuffle_width)).argsort(axis=1)

    @property
    def shuffle(self) -> np.ndarray:
        return self._shuffle

    def view(self, array: np.ndarray) -> np.ndarray:
        """將二維陣列轉換為 (rows, cols, h, w) 的分塊視圖。"""
        rows, cols = self.geometry.rows, self.geometry.cols
        bh, bw = self.geometry.block_shape
        trimmed = array[: rows * bh, : cols * bw]
        reshaped = trimmed.reshape(rows, bh, cols, bw)
        return reshaped.swapaxes(1, 2)

    def combine(self, blocks: np.ndarray) -> np.ndarray:
        """將 (rows, cols, h, w) 的分塊視圖還原為二維陣列。"""
        rows, cols = self.geometry.rows, self.geometry.cols
        bh, bw = self.geometry.block_shape
        reshaped = blocks.swapaxes(1, 2)
        return reshaped.reshape(rows * bh, cols * bw)

    def iter_indices(self) -> Iterator[Tuple[int, int]]:
        for i in range(self.geometry.rows):
            for j in range(self.geometry.cols):
                yield i, j

    def shuffle_row(self, idx: int) -> np.ndarray:
        return self._shuffle[idx]

    def reshape_block(self, block: np.ndarray) -> np.ndarray:
        return block.reshape(self.geometry.block_shape)

    def flatten_block(self, block: np.ndarray) -> np.ndarray:
        return block.reshape(-1)

    def apply_shuffle(self, block: np.ndarray, shuffle_idx: np.ndarray) -> np.ndarray:
        flat = self.flatten_block(block)
        shuffled = flat[shuffle_idx]
        return shuffled.reshape(self.geometry.block_shape)

    def undo_shuffle(self, block: np.ndarray, shuffle_idx: np.ndarray) -> np.ndarray:
        flat = self.flatten_block(block)
        restored = np.empty_like(flat)
        restored[shuffle_idx] = flat
        return restored.reshape(self.geometry.block_shape)

