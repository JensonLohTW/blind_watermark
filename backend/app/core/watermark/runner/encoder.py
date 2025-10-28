from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional, Tuple

import cv2
import numpy as np

from ..config import WatermarkConfig
from ..operations.algorithm import WatermarkAlgorithm

WatermarkMode = Literal["img", "str", "bit"]


@dataclass
class WatermarkPayload:
    bits: np.ndarray
    shape: Tuple[int, ...] | None = None

    @property
    def size(self) -> int:
        return int(self.bits.size)


class WatermarkEmbedder:
    """管理載體圖與浮水印資料的載入與嵌入流程。"""

    def __init__(self, config: WatermarkConfig) -> None:
        config.validate()
        self.config = config
        self._algorithm = WatermarkAlgorithm(
            tuning=config.tuning,
            keys=config.keys,
            mode=config.runtime.mode,
            processes=config.runtime.processes,
        )
        self._cover: Optional[np.ndarray] = None
        self._payload: Optional[WatermarkPayload] = None

    @staticmethod
    def _read_image(path: str) -> np.ndarray:
        image = cv2.imread(path, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise FileNotFoundError(f"image file '{path}' not found")
        return image

    def load_cover_image(self, *, path: Optional[str] = None, image: Optional[np.ndarray] = None) -> np.ndarray:
        if image is None:
            if path is None:
                raise ValueError("either path or image must be provided")
            image = self._read_image(path)
        self._cover = image
        return image

    def load_watermark(self, payload: WatermarkPayload) -> None:
        if payload.size == 0:
            raise ValueError("watermark payload cannot be empty")
        shuffled = payload.bits.copy()
        np.random.RandomState(self.config.keys.watermark).shuffle(shuffled)
        self._payload = WatermarkPayload(bits=shuffled, shape=payload.shape)

    def embed(self) -> np.ndarray:
        if self._cover is None:
            raise RuntimeError("cover image not loaded")
        if self._payload is None:
            raise RuntimeError("watermark not loaded")
        return self._algorithm.embed(self._cover, self._payload.bits)

    @staticmethod
    def encode_text(content: str) -> WatermarkPayload:
        byte_string = content.encode("utf-8")
        integer = int.from_bytes(byte_string, byteorder="big")
        binary = bin(integer)[2:]
        bits = np.array([ch == "1" for ch in binary], dtype=bool)
        return WatermarkPayload(bits=bits, shape=(bits.size,))

    @staticmethod
    def encode_image(source: str | np.ndarray) -> WatermarkPayload:
        if isinstance(source, str):
            image = cv2.imread(source, cv2.IMREAD_GRAYSCALE)
            if image is None:
                raise FileNotFoundError(f"watermark image '{source}' not found")
        else:
            image = source
            if image.ndim == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        bits = image.flatten() > 128
        return WatermarkPayload(bits=bits, shape=image.shape)

    @staticmethod
    def encode_bits(bits: np.ndarray) -> WatermarkPayload:
        array = np.array(bits, dtype=bool)
        return WatermarkPayload(bits=array, shape=array.shape)

    def load_watermark_from_source(self, content, mode: WatermarkMode) -> WatermarkPayload:
        if mode == "str":
            payload = self.encode_text(str(content))
        elif mode == "img":
            payload = self.encode_image(content)
        elif mode == "bit":
            payload = self.encode_bits(np.asarray(content))
        else:
            raise ValueError("unsupported watermark mode")
        self.load_watermark(payload)
        return payload

    @property
    def payload(self) -> Optional[WatermarkPayload]:
        return self._payload
