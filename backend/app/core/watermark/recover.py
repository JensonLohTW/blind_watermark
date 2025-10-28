"""攻擊恢復相容函式。"""

from __future__ import annotations

from typing import Optional, Tuple

import cv2
import numpy as np

from .robustness import recovery


def estimate_crop_parameters(
    original_file: Optional[str] = None,
    template_file: Optional[str] = None,
    ori_img: Optional[np.ndarray] = None,
    tem_img: Optional[np.ndarray] = None,
    scale: Tuple[float, float] = (0.5, 2.0),
    search_num: int = 200,
):
    return recovery.estimate_crop_parameters(
        original_file=original_file,
        template_file=template_file,
        original_img=ori_img,
        template_img=tem_img,
        scale_range=scale,
        search_steps=search_num,
    )


def recover_crop(
    template_file: Optional[str] = None,
    tem_img: Optional[np.ndarray] = None,
    output_file_name: Optional[str] = None,
    loc: Tuple[int, int, int, int] = (0, 0, 0, 0),
    image_o_shape: Tuple[int, int] = (0, 0),
    base_img: Optional[np.ndarray] = None,
):
    if tem_img is None:
        if template_file is None:
            raise ValueError("template_file 或 tem_img 必須至少提供一種")
        tem_img = cv2.imread(template_file, cv2.IMREAD_UNCHANGED)
        if tem_img is None:
            raise FileNotFoundError(f"template file '{template_file}' not found")

    if tem_img.ndim == 2:
        template_color = cv2.cvtColor(tem_img, cv2.COLOR_GRAY2BGR)
    else:
        template_color = tem_img.copy()

    x1, y1, x2, y2 = loc
    recovered_region = cv2.resize(template_color, dsize=(x2 - x1, y2 - y1))

    if base_img is not None:
        if base_img.shape[:2] != image_o_shape:
            raise ValueError("base_img 尺寸必須與 image_o_shape 相符")
        recovered = base_img.copy()
    else:
        recovered = np.zeros((image_o_shape[0], image_o_shape[1], 3), dtype=np.uint8)

    recovered[y1:y2, x1:x2] = recovered_region
    if output_file_name:
        cv2.imwrite(output_file_name, recovered)
    return recovered
