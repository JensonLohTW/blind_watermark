from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Tuple

import cv2
import numpy as np

from ..config import WatermarkConfig
from ..operations.algorithm import WatermarkAlgorithm

WatermarkMode = Literal["img", "str", "bit"]


@dataclass
class ExtractionResult:
    payload: np.ndarray
    mode: WatermarkMode


class WatermarkExtractor:
    def __init__(self, config: WatermarkConfig) -> None:
        config.validate()
        self.config = config
        self._algorithm = WatermarkAlgorithm(
            tuning=config.tuning,
            keys=config.keys,
            mode=config.runtime.mode,
            processes=config.runtime.processes,
        )

    @staticmethod
    def _read_image(path: str) -> np.ndarray:
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise FileNotFoundError(f"image file '{path}' not found")
        return image

    def extract(
        self,
        *,
        path: Optional[str] = None,
        image: Optional[np.ndarray] = None,
        watermark_length: Tuple[int, ...],
        mode: WatermarkMode,
    ) -> ExtractionResult:
        if image is None:
            if path is None:
                raise ValueError("either path or image must be provided")
            image = self._read_image(path)

        wm_size = int(np.prod(watermark_length))
        use_kmeans = mode in {"str", "bit"}
        payload = self._algorithm.extract(image, wm_size, use_kmeans=use_kmeans)
        return ExtractionResult(payload=payload, mode=mode)

    def decrypt(self, payload: np.ndarray, *, original_length: int) -> np.ndarray:
        indices = np.arange(original_length)
        np.random.RandomState(self.config.keys.watermark).shuffle(indices)
        restored = np.empty_like(payload)
        restored[indices] = payload.copy()
        return restored

    def decode(self, payload: np.ndarray, *, length: Tuple[int, ...], mode: WatermarkMode):
        total_length = int(np.prod(length))
        data = self.decrypt(payload, original_length=total_length)
        if mode == "img":
            image = (data.reshape(length) >= 0.5).astype(np.uint8) * 255
            return image
        if mode == "str":
            bits = "".join("1" if value >= 0.5 else "0" for value in data)
            if not bits:
                return ""
            integer = int(bits, 2)
            hex_string = hex(integer)[2:]
            if len(hex_string) % 2:
                hex_string = "0" + hex_string
            return bytes.fromhex(hex_string).decode("utf-8", errors="replace")
        if mode == "bit":
            return (data >= 0.5).astype(bool)
        raise ValueError("unsupported watermark mode")
