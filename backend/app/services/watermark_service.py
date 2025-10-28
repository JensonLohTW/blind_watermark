"""
浮水印服務層：封裝核心浮水印邏輯（純記憶體流程）。
"""
from __future__ import annotations

import base64
import io
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from app.core.watermark import WaterMark


class WatermarkService:
    """浮水印服務類別"""

    @staticmethod
    def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()

    @staticmethod
    def bytes_to_base64(data: bytes) -> str:
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def base64_to_bytes(data: str) -> bytes:
        return base64.b64decode(data)

    @staticmethod
    def _decode_image(image_bytes: bytes) -> np.ndarray:
        array = np.frombuffer(image_bytes, dtype=np.uint8)
        image = cv2.imdecode(array, cv2.IMREAD_UNCHANGED)
        if image is None:
            raise ValueError("無法解析圖片檔案")
        return image

    @staticmethod
    def _encode_image(image: np.ndarray) -> bytes:
        success, buffer = cv2.imencode(".png", image)
        if not success:
            raise ValueError("圖片編碼失敗")
        return buffer.tobytes()

    def _prepare_watermark(
        self,
        bwm: WaterMark,
        mode: str,
        *,
        text: Optional[str],
        image_bytes: Optional[bytes],
        length: Optional[int],
    ) -> None:
        if mode == "str":
            if not text:
                raise ValueError("文字模式需要提供 watermark_text")
            bwm.read_wm(text, mode="str")
        elif mode == "img":
            if not image_bytes:
                raise ValueError("圖片模式需要提供 watermark_image")
            wm_image = self._decode_image(image_bytes)
            bwm.read_wm(wm_image, mode="img")
        elif mode == "bit":
            if length is None:
                raise ValueError("位元模式需要提供 watermark_length")
            wm_bits = np.random.randint(0, 2, length)
            bwm.read_wm(wm_bits, mode="bit")
        else:
            raise ValueError(f"不支援的模式: {mode}")

    def embed_watermark(
        self,
        image_bytes: bytes,
        mode: str,
        password_img: int,
        password_wm: int,
        watermark_text: Optional[str] = None,
        watermark_image_bytes: Optional[bytes] = None,
        watermark_length: Optional[int] = None,
    ) -> Tuple[bytes, int, Optional[Tuple[int, ...]]]:
        cover_img = self._decode_image(image_bytes)

        bwm = WaterMark(password_img=password_img, password_wm=password_wm)
        bwm.read_img(img=cover_img)

        self._prepare_watermark(
            bwm,
            mode,
            text=watermark_text,
            image_bytes=watermark_image_bytes,
            length=watermark_length,
        )

        embedded = bwm.embed()
        wm_length = len(bwm.wm_bit) if bwm.wm_bit is not None else 0
        wm_shape = bwm.wm_shape if mode == "img" and bwm.wm_shape else None
        return self._encode_image(embedded), wm_length, wm_shape

    def extract_watermark(
        self,
        image_bytes: bytes,
        mode: str,
        password_img: int,
        password_wm: int,
        watermark_length: int,
        watermark_shape: Optional[Tuple[int, ...]] = None,
    ) -> Tuple[Optional[str], Optional[bytes]]:
        embedded_img = self._decode_image(image_bytes)

        bwm = WaterMark(password_img=password_img, password_wm=password_wm)
        shape = watermark_shape or watermark_length
        result = bwm.extract(embed_img=embedded_img, wm_shape=shape, mode=mode)

        if mode == "str":
            return result, None
        if mode == "img":
            array = np.array(result, copy=False)
            if watermark_shape and array.ndim == 1:
                array = array.reshape(watermark_shape)
            return None, self._encode_image(array)
        if mode == "bit":
            return str(result.tolist()), None
        raise ValueError(f"不支援的模式: {mode}")
