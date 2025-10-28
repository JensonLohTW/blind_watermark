from __future__ import annotations

from dataclasses import dataclass
from typing import Tuple

import cv2
import numpy as np
from numpy.linalg import svd
from pywt import dwt2, idwt2

from .blocks import BlockGeometry, BlockSequence
from .transforms import (
    clamp_to_uint8,
    convert_bgr_to_yuv,
    convert_yuv_to_bgr,
    pad_to_even,
    remove_even_padding,
)
from ..config import AlgorithmTuning, WatermarkKeys
from ..runtime import AutoPool


@dataclass
class WaveletComponents:
    original_shape: Tuple[int, int]
    alpha: np.ndarray | None
    ca_channels: Tuple[np.ndarray, np.ndarray, np.ndarray]
    hvd_channels: Tuple[Tuple[np.ndarray, np.ndarray, np.ndarray], ...]
    sequence: BlockSequence


def _split_alpha(image: np.ndarray) -> Tuple[np.ndarray, np.ndarray | None]:
    if image.shape[2] == 4 and np.any(image[:, :, 3] < 255):
        return image[:, :, :3], image[:, :, 3]
    return image, None


def _merge_alpha(image: np.ndarray, alpha: np.ndarray | None) -> np.ndarray:
    if alpha is None:
        return image
    return np.dstack([image, alpha])


def _init_sequence(keys: WatermarkKeys, ca_shape: Tuple[int, int], block_shape: Tuple[int, int]) -> BlockSequence:
    geometry = BlockGeometry.from_ca_shape(ca_shape, block_shape)
    shuffle_width = block_shape[0] * block_shape[1]
    return BlockSequence(geometry=geometry, shuffle_seed=keys.image, shuffle_width=shuffle_width)


def _embed_block(block: np.ndarray, shuffle_idx: np.ndarray, wm_bit: int, tuning: AlgorithmTuning) -> np.ndarray:
    block_dct = cv2.dct(block)
    shuffled = block_dct.flatten()[shuffle_idx].reshape(block.shape)
    u, s, v = svd(shuffled)
    s0 = (s[0] // tuning.d1 + 0.25 + 0.5 * wm_bit) * tuning.d1
    s[0] = s0
    if tuning.d2 > 0:
        s[1] = (s[1] // tuning.d2 + 0.25 + 0.5 * wm_bit) * tuning.d2
    recomposed = np.dot(u, np.dot(np.diag(s), v)).flatten()
    restored = recomposed.copy()
    restored[shuffle_idx] = recomposed
    return cv2.idct(restored.reshape(block.shape))


def _extract_block(block: np.ndarray, shuffle_idx: np.ndarray, tuning: AlgorithmTuning) -> float:
    block_dct = cv2.dct(block)
    shuffled = block_dct.flatten()[shuffle_idx].reshape(block.shape)
    _, s, _ = svd(shuffled)
    wm = 1.0 if s[0] % tuning.d1 > tuning.d1 / 2 else 0.0
    if tuning.d2 > 0:
        tmp = 1.0 if s[1] % tuning.d2 > tuning.d2 / 2 else 0.0
        wm = (wm * 3 + tmp) / 4
    return wm


def _embed_task(args: tuple[np.ndarray, np.ndarray, int, AlgorithmTuning]) -> np.ndarray:
    block, shuffle_idx, wm_bit, tuning = args
    return _embed_block(block, shuffle_idx, wm_bit, tuning)


def _extract_task(args: tuple[np.ndarray, np.ndarray, AlgorithmTuning]) -> float:
    block, shuffle_idx, tuning = args
    return _extract_block(block, shuffle_idx, tuning)


def _average_payload(values: np.ndarray, wm_size: int) -> np.ndarray:
    wm_avg = np.zeros(shape=wm_size)
    for idx in range(wm_size):
        wm_avg[idx] = values[:, idx::wm_size].mean()
    return wm_avg


def one_dim_kmeans(values: np.ndarray, *, max_iter: int = 300) -> np.ndarray:
    centers = [float(values.min()), float(values.max())]
    if centers[0] == centers[1]:
        return np.zeros_like(values, dtype=bool)
    for _ in range(max_iter):
        threshold = sum(centers) / 2
        mask = values > threshold
        new_centers = [values[~mask].mean(), values[mask].mean()]
        if np.isnan(new_centers[0]) or np.isnan(new_centers[1]):
            break
        new_threshold = sum(new_centers) / 2
        if abs(new_threshold - threshold) < 1e-6:
            threshold = new_threshold
            mask = values > threshold
            return mask
        centers = new_centers
    threshold = sum(centers) / 2
    return values > threshold


class WatermarkAlgorithm:
    """封裝 DWT-DCT-SVD 核心演算法。"""

    def __init__(self, tuning: AlgorithmTuning, keys: WatermarkKeys, mode: str, processes: int | None) -> None:
        self.tuning = tuning
        self.keys = keys
        self.mode = mode
        self.processes = processes

    def _decompose(self, image: np.ndarray) -> WaveletComponents:
        bgr, alpha = _split_alpha(image)
        bgr = bgr.astype(np.float32)
        original_shape = bgr.shape[:2]
        yuv = pad_to_even(convert_bgr_to_yuv(bgr))
        ca_channels = []
        hvd_channels = []
        for channel in range(3):
            ca, hvd = dwt2(yuv[:, :, channel], "haar")
            ca_channels.append(ca.astype(np.float32))
            hvd_channels.append(hvd)
        sequence = _init_sequence(self.keys, ca_channels[0].shape, self.tuning.block.size)
        return WaveletComponents(
            original_shape=original_shape,
            alpha=alpha,
            ca_channels=(ca_channels[0], ca_channels[1], ca_channels[2]),
            hvd_channels=tuple(hvd_channels),
            sequence=sequence,
        )

    def embed(self, image: np.ndarray, wm_bits: np.ndarray) -> np.ndarray:
        components = self._decompose(image)
        geometry = components.sequence.geometry
        if wm_bits.size >= geometry.block_num:
            raise ValueError("watermark too large for host image")
        embedded_channels = []
        with AutoPool(self.mode, self.processes) as pool:
            for idx, ca in enumerate(components.ca_channels):
                blocks_view = components.sequence.view(ca)
                flat_blocks = blocks_view.reshape(geometry.block_num, *self.tuning.block.size)
                tasks = [
                    (flat_blocks[i], components.sequence.shuffle[i], int(wm_bits[i % wm_bits.size]), self.tuning)
                    for i in range(geometry.block_num)
                ]
                results = pool.map(_embed_task, tasks)
                updated_blocks = np.stack(results, axis=0)
                reshaped = updated_blocks.reshape(blocks_view.shape)
                ca_updated = ca.copy()
                ca_updated[: geometry.part_shape[0], : geometry.part_shape[1]] = components.sequence.combine(reshaped)
                channel = idwt2((ca_updated, components.hvd_channels[idx]), "haar")
                embedded_channels.append(channel)
        stacked = np.stack(embedded_channels, axis=2)
        restored = remove_even_padding(stacked, components.original_shape)
        bgr = convert_yuv_to_bgr(restored)
        return clamp_to_uint8(_merge_alpha(bgr, components.alpha))

    def extract(self, image: np.ndarray, wm_size: int, *, use_kmeans: bool) -> np.ndarray:
        components = self._decompose(image)
        geometry = components.sequence.geometry
        blocks_per_channel = np.zeros((3, geometry.block_num))

        with AutoPool(self.mode, self.processes) as pool:
            for idx, ca in enumerate(components.ca_channels):
                blocks_view = components.sequence.view(ca)
                flat_blocks = blocks_view.reshape(geometry.block_num, *self.tuning.block.size)
                tasks = [
                    (flat_blocks[i], components.sequence.shuffle[i], self.tuning)
                    for i in range(geometry.block_num)
                ]
                results = pool.map(_extract_task, tasks)
                blocks_per_channel[idx, :] = np.array(results)

        wm_avg = _average_payload(blocks_per_channel, wm_size)
        if use_kmeans:
            return one_dim_kmeans(wm_avg)
        return wm_avg
