"""攻擊模擬相容函式。"""

from __future__ import annotations

from typing import Optional, Tuple

import numpy as np

from .robustness import attacks


def cut_att3(
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    output_file_name: Optional[str] = None,
    loc_r: Optional[Tuple[Tuple[float, float], Tuple[float, float]]] = None,
    loc: Optional[Tuple[int, int, int, int]] = None,
    scale: Optional[float] = None,
) -> np.ndarray:
    return attacks.cut_and_scale(
        input_filename=input_filename,
        input_img=input_img,
        loc_ratio=loc_r,
        loc=loc,
        scale=scale,
        output_file_name=output_file_name,
    )


def cut_att(
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    output_file_name: Optional[str] = None,
    loc: Optional[Tuple[Tuple[float, float], Tuple[float, float]]] = None,
) -> np.ndarray:
    return attacks.cut_and_scale(
        input_filename=input_filename,
        input_img=input_img,
        loc_ratio=loc,
        output_file_name=output_file_name,
    )


def cut_att2(*args, **kwargs):  # pragma: no cover - 保留舊版別名
    return cut_att3(*args, **kwargs)


def resize_att(
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    output_file_name: Optional[str] = None,
    out_shape: Tuple[int, int] = (500, 500),
) -> np.ndarray:
    return attacks.resize(
        input_filename=input_filename,
        input_img=input_img,
        output_file_name=output_file_name,
        out_shape=out_shape,
    )


def bright_att(
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    output_file_name: Optional[str] = None,
    ratio: float = 0.8,
) -> np.ndarray:
    return attacks.adjust_brightness(
        input_filename=input_filename,
        input_img=input_img,
        output_file_name=output_file_name,
        ratio=ratio,
    )


def shelter_att(
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    output_file_name: Optional[str] = None,
    ratio: float = 0.1,
    n: int = 3,
) -> np.ndarray:
    return attacks.shelter(
        input_filename=input_filename,
        input_img=input_img,
        output_file_name=output_file_name,
        ratio=ratio,
        blocks=n,
    )


def salt_pepper_att(
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    output_file_name: Optional[str] = None,
    ratio: float = 0.01,
) -> np.ndarray:
    return attacks.salt_and_pepper(
        input_filename=input_filename,
        input_img=input_img,
        output_file_name=output_file_name,
        ratio=ratio,
    )


def rot_att(
    input_filename: Optional[str] = None,
    input_img: Optional[np.ndarray] = None,
    output_file_name: Optional[str] = None,
    angle: float = 45,
) -> np.ndarray:
    return attacks.rotate(
        input_filename=input_filename,
        input_img=input_img,
        output_file_name=output_file_name,
        angle=angle,
    )
