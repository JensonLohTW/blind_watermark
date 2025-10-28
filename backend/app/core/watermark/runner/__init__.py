from __future__ import annotations

from dataclasses import dataclass
from typing import Optional, Sequence, Tuple

import cv2
import numpy as np

from ..config import AlgorithmTuning, BlockConfig, RuntimeConfig, WatermarkConfig, WatermarkKeys
from .encoder import WatermarkEmbedder, WatermarkPayload
from .extractor import WatermarkExtractor, WatermarkMode


@dataclass
class EmbedResult:
    image: np.ndarray
    watermark_length: int


class WatermarkPipeline:
    """高階浮水印操作流程，提供與舊版 WaterMark 類似的介面。"""

    def __init__(
        self,
        config: Optional[WatermarkConfig] = None,
        *,
        password_img: int = 1,
        password_wm: int = 1,
        block_shape: Tuple[int, int] = (4, 4),
        mode: str = "common",
        processes: Optional[int] = None,
        d1: float = 36.0,
        d2: float = 20.0,
    ) -> None:
        if config is None:
            config = WatermarkConfig(
                keys=WatermarkKeys(image=password_img, watermark=password_wm),
                tuning=AlgorithmTuning(d1=d1, d2=d2, block=BlockConfig(size=block_shape)),
                runtime=RuntimeConfig(mode=mode, processes=processes),
            )
        config.validate()
        self.config = config
        self._embedder = WatermarkEmbedder(config)
        self._extractor = WatermarkExtractor(config)
        self._cover_image: np.ndarray | None = None
        self._payload_meta: WatermarkPayload | None = None

    @staticmethod
    def _normalize_shape(shape: Sequence[int] | int) -> Tuple[int, ...]:
        if isinstance(shape, int):
            return (shape,)
        return tuple(shape)

    def read_img(self, filename: str | None = None, img: np.ndarray | None = None) -> np.ndarray:
        image = self._embedder.load_cover_image(path=filename, image=img)
        self._cover_image = image
        return image

    def read_wm(self, wm_content, mode: WatermarkMode = "img") -> WatermarkPayload:
        payload = self._embedder.load_watermark_from_source(wm_content, mode=mode)
        self._payload_meta = payload
        return payload

    def embed(self, filename: Optional[str] = None, compression_ratio: Optional[int] = None) -> np.ndarray:
        if self._cover_image is None:
            raise RuntimeError("cover image not loaded")
        if self._payload_meta is None:
            raise RuntimeError("watermark not loaded")
        embedded = self._embedder.embed()
        if filename is not None:
            self._write_image(filename, embedded, compression_ratio)
        return embedded

    @property
    def payload_bits(self) -> np.ndarray | None:
        payload = self._embedder.payload
        return None if payload is None else payload.bits

    def _write_image(self, filename: str, image: np.ndarray, compression_ratio: Optional[int]) -> None:
        if compression_ratio is None:
            cv2.imwrite(filename, image)
        elif filename.lower().endswith(".jpg"):
            cv2.imwrite(filename, image, params=[cv2.IMWRITE_JPEG_QUALITY, int(compression_ratio)])
        elif filename.lower().endswith(".png"):
            cv2.imwrite(filename, image, params=[cv2.IMWRITE_PNG_COMPRESSION, int(compression_ratio)])
        else:
            cv2.imwrite(filename, image)

    def extract(
        self,
        filename: Optional[str] = None,
        embed_img: Optional[np.ndarray] = None,
        wm_shape: Sequence[int] | int | None = None,
        out_wm_name: Optional[str] = None,
        mode: WatermarkMode = "img",
    ):
        if wm_shape is None:
            raise ValueError("wm_shape is required for extraction")
        if embed_img is None:
            if filename is None:
                raise ValueError("either filename or embed_img must be provided")
            embed_img = cv2.imread(filename, cv2.IMREAD_UNCHANGED)
            if embed_img is None:
                raise FileNotFoundError(f"image file '{filename}' not found")
        shape = self._normalize_shape(wm_shape)
        result = self._extractor.extract(image=embed_img, watermark_length=shape, mode=mode)
        decoded = self._extractor.decode(result.payload, length=shape, mode=mode)
        if mode == "img":
            if out_wm_name:
                cv2.imwrite(out_wm_name, decoded)
            return decoded
        return decoded

    def extract_decrypt(self, wm_avg: np.ndarray) -> np.ndarray:
        length = wm_avg.size
        indices = np.arange(length)
        np.random.RandomState(self.config.keys.watermark).shuffle(indices)
        restored = np.empty_like(wm_avg)
        restored[indices] = wm_avg.copy()
        return restored

    @property
    def wm_size(self) -> int:
        return self._payload_meta.size if self._payload_meta else 0
