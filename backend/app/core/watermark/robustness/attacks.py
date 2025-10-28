from __future__ import annotations

from typing import Optional, Tuple

import cv2
import numpy as np

Location = Tuple[Tuple[float, float], Tuple[float, float]]


def _ensure_image(input_filename: Optional[str], input_img: Optional[np.ndarray]) -> np.ndarray:
    if input_img is not None:
        return input_img.copy()
    if input_filename is None:
        raise ValueError("either input_filename or input_img must be provided")
    image = cv2.imread(input_filename, cv2.IMREAD_COLOR)
    if image is None:
        raise FileNotFoundError(f"image file '{input_filename}' not found")
    return image


def cut_and_scale(
    *,
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    loc: Optional[Tuple[int, int, int, int]] = None,
    loc_ratio: Optional[Location] = None,
    scale: Optional[float] = None,
    output_file_name: Optional[str] = None,
) -> np.ndarray:
    image = _ensure_image(input_filename, input_img)
    if loc is None:
        if loc_ratio is None:
            raise ValueError("either loc or loc_ratio must be provided")
        h, w, _ = image.shape
        (x1_r, y1_r), (x2_r, y2_r) = loc_ratio
        loc = (
            int(w * x1_r),
            int(h * y1_r),
            int(w * x2_r),
            int(h * y2_r),
        )
    x1, y1, x2, y2 = loc
    cropped = image[y1:y2, x1:x2].copy()
    if scale and scale != 1:
        height, width = cropped.shape[:2]
        cropped = cv2.resize(cropped, dsize=(round(width * scale), round(height * scale)))
    if output_file_name:
        cv2.imwrite(output_file_name, cropped)
    return cropped


def resize(
    *,
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    out_shape: Tuple[int, int] = (500, 500),
    output_file_name: Optional[str] = None,
) -> np.ndarray:
    image = _ensure_image(input_filename, input_img)
    resized = cv2.resize(image, dsize=out_shape)
    if output_file_name:
        cv2.imwrite(output_file_name, resized)
    return resized


def adjust_brightness(
    *,
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    ratio: float = 0.8,
    output_file_name: Optional[str] = None,
) -> np.ndarray:
    image = _ensure_image(input_filename, input_img).astype(np.float32)
    adjusted = np.clip(image * ratio, 0, 255).astype(np.uint8)
    if output_file_name:
        cv2.imwrite(output_file_name, adjusted)
    return adjusted


def shelter(
    *,
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    ratio: float = 0.1,
    blocks: int = 3,
    output_file_name: Optional[str] = None,
) -> np.ndarray:
    image = _ensure_image(input_filename, input_img)
    h, w, _ = image.shape
    output = image.copy()
    block_area_h = int(h * ratio)
    block_area_w = int(w * ratio)
    for _ in range(blocks):
        top = np.random.randint(0, max(1, h - block_area_h))
        left = np.random.randint(0, max(1, w - block_area_w))
        output[top : top + block_area_h, left : left + block_area_w] = 255
    if output_file_name:
        cv2.imwrite(output_file_name, output)
    return output


def salt_and_pepper(
    *,
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    ratio: float = 0.01,
    output_file_name: Optional[str] = None,
) -> np.ndarray:
    image = _ensure_image(input_filename, input_img)
    mask = np.random.rand(*image.shape[:2]) < ratio
    output = image.copy()
    output[mask] = 255
    if output_file_name:
        cv2.imwrite(output_file_name, output)
    return output


def rotate(
    *,
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    angle: float = 45,
    output_file_name: Optional[str] = None,
) -> np.ndarray:
    image = _ensure_image(input_filename, input_img)
    rows, cols = image.shape[:2]
    matrix = cv2.getRotationMatrix2D((cols / 2, rows / 2), angle=angle, scale=1.0)
    rotated = cv2.warpAffine(image, matrix, (cols, rows))
    if output_file_name:
        cv2.imwrite(output_file_name, rotated)
    return rotated

