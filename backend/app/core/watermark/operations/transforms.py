from __future__ import annotations

from typing import Tuple

import cv2
import numpy as np


def convert_bgr_to_yuv(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_BGR2YUV)


def convert_yuv_to_bgr(image: np.ndarray) -> np.ndarray:
    return cv2.cvtColor(image, cv2.COLOR_YUV2BGR)


def pad_to_even(image: np.ndarray) -> np.ndarray:
    h_pad = image.shape[0] % 2
    w_pad = image.shape[1] % 2
    if h_pad == 0 and w_pad == 0:
        return image
    return cv2.copyMakeBorder(image, 0, h_pad, 0, w_pad, cv2.BORDER_CONSTANT, value=(0, 0, 0))


def remove_even_padding(image: np.ndarray, original_shape: Tuple[int, int]) -> np.ndarray:
    h, w = original_shape
    return image[:h, :w]


def clamp_to_uint8(image: np.ndarray) -> np.ndarray:
    return np.clip(image, a_min=0, a_max=255).astype(np.uint8)

