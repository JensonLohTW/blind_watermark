from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import cv2
import numpy as np


@dataclass
class TemplateMatch:
    location: Tuple[int, int]
    score: float
    scale: float


def _load_grayscale(path: Optional[str], image: Optional[np.ndarray]) -> np.ndarray:
    if image is not None:
        if image.ndim == 3:
            return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        return image
    if path is None:
        raise ValueError("either file path or image must be provided")
    loaded = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if loaded is None:
        raise FileNotFoundError(f"image file '{path}' not found")
    return loaded


def _match_at_scale(image: np.ndarray, template: np.ndarray, scale: float) -> TemplateMatch:
    resized = cv2.resize(template, dsize=(int(template.shape[1] * scale), int(template.shape[0] * scale)))
    scores = cv2.matchTemplate(image, resized, cv2.TM_CCOEFF_NORMED)
    index = np.unravel_index(np.argmax(scores), scores.shape)
    return TemplateMatch(location=(index[1], index[0]), score=float(scores[index]), scale=scale)


def _refine_scales(scales: Sequence[float], image: np.ndarray, template: np.ndarray) -> TemplateMatch:
    best = TemplateMatch(location=(0, 0), score=-1.0, scale=scales[0])
    for scale in scales:
        match = _match_at_scale(image, template, scale)
        if match.score > best.score:
            best = match
    return best


def search_template(
    *,
    original_file: Optional[str] = None,
    template_file: Optional[str] = None,
    original_img: Optional[np.ndarray] = None,
    template_img: Optional[np.ndarray] = None,
    scale_range: Tuple[float, float] = (0.5, 2.0),
    search_steps: int = 200,
) -> TemplateMatch:
    image = _load_grayscale(original_file, original_img)
    template = _load_grayscale(template_file, template_img)

    min_scale, max_scale = scale_range
    max_scale = min(max_scale, image.shape[0] / template.shape[0], image.shape[1] / template.shape[1])

    scales = np.linspace(min_scale, max_scale, search_steps)
    coarse = _refine_scales(scales, image, template)

    window = max((max_scale - min_scale) / search_steps, 0.01)
    fine_scales = np.linspace(max(coarse.scale - window, min_scale), min(coarse.scale + window, max_scale), max(5, int(2 / window)))
    return _refine_scales(fine_scales, image, template)


def estimate_crop_parameters(
    *,
    original_file: Optional[str] = None,
    template_file: Optional[str] = None,
    original_img: Optional[np.ndarray] = None,
    template_img: Optional[np.ndarray] = None,
    scale_range: Tuple[float, float] = (0.5, 2.0),
    search_steps: int = 200,
) -> Tuple[Tuple[int, int, int, int], Tuple[int, int], float, float]:
    image = _load_grayscale(original_file, original_img)
    template = _load_grayscale(template_file, template_img)

    if scale_range[0] == scale_range[1] == 1:
        match = _match_at_scale(image, template, scale=1.0)
    else:
        match = search_template(
            original_img=image,
            template_img=template,
            scale_range=scale_range,
            search_steps=search_steps,
        )
    w = int(template.shape[1] * match.scale)
    h = int(template.shape[0] * match.scale)
    x1, y1 = match.location
    x2, y2 = x1 + w, y1 + h
    return (x1, y1, x2, y2), image.shape, match.score, match.scale


def recover_crop(
    *,
    template_file: Optional[str] = None,
    template_img: Optional[np.ndarray] = None,
    location: Tuple[int, int, int, int],
    output_shape: Tuple[int, int],
    output_file_name: Optional[str] = None,
) -> np.ndarray:
    template = _load_grayscale(template_file, template_img)
    x1, y1, x2, y2 = location
    recovered = np.zeros((output_shape[0], output_shape[1], 3), dtype=np.uint8)
    resized = cv2.resize(template, dsize=(x2 - x1, y2 - y1))
    recovered[y1:y2, x1:x2] = cv2.cvtColor(resized, cv2.COLOR_GRAY2BGR)
    if output_file_name:
        cv2.imwrite(output_file_name, recovered)
    return recovered

