from __future__ import annotations

from typing import Optional, Sequence, Tuple

import numpy as np

from .runner import WatermarkPipeline


class WaterMark:
    """提供與舊版 WaterMark 類似的高階操作介面。"""

    def __init__(
        self,
        password_wm: int = 1,
        password_img: int = 1,
        block_shape: Sequence[int] = (4, 4),
        mode: str = "common",
        processes: Optional[int] = None,
    ) -> None:
        self._pipeline = WatermarkPipeline(
            password_img=password_img,
            password_wm=password_wm,
            block_shape=tuple(block_shape),
            mode=mode,
            processes=processes,
        )
        self.wm_bit: Optional[np.ndarray] = None
        self.wm_size: int = 0
        self.wm_shape: Optional[Tuple[int, ...]] = None

    def read_img(self, filename: Optional[str] = None, img: Optional[np.ndarray] = None) -> np.ndarray:
        """讀取或設定嵌入用的原始圖片。"""
        return self._pipeline.read_img(filename=filename, img=img)

    def read_wm(self, wm_content, mode: str = "img") -> None:
        """讀取浮水印內容並記錄位元資訊。"""
        payload = self._pipeline.read_wm(wm_content, mode=mode)
        bits = self._pipeline.payload_bits
        self.wm_size = payload.size
        self.wm_bit = None if bits is None else bits.copy()
        self.wm_shape = payload.shape

    def embed(self, filename: Optional[str] = None, compression_ratio: Optional[int] = None) -> np.ndarray:
        """將浮水印嵌入先前讀取的圖片。"""
        return self._pipeline.embed(filename=filename, compression_ratio=compression_ratio)

    def extract_decrypt(self, wm_avg: np.ndarray) -> np.ndarray:
        """對提取出的位元進行解密。"""
        return self._pipeline.extract_decrypt(wm_avg)

    def extract(
        self,
        filename: Optional[str] = None,
        embed_img: Optional[np.ndarray] = None,
        wm_shape: Sequence[int] | int | None = None,
        out_wm_name: Optional[str] = None,
        mode: str = "img",
    ):
        """提取浮水印內容。"""
        result = self._pipeline.extract(
            filename=filename,
            embed_img=embed_img,
            wm_shape=wm_shape,
            out_wm_name=out_wm_name,
            mode=mode,
        )
        if wm_shape is not None:
            shape = (wm_shape,) if isinstance(wm_shape, int) else tuple(wm_shape)
            self.wm_size = int(np.prod(shape))
        return result
