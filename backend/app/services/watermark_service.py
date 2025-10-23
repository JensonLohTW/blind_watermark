"""
浮水印服務層：封裝核心浮水印邏輯
"""
import base64
import io
import tempfile
from pathlib import Path
from typing import Optional, Tuple

import cv2
import numpy as np
from PIL import Image

from app.core.blind_watermark import WaterMark


class WatermarkService:
    """浮水印服務類別"""

    @staticmethod
    def image_to_bytes(image: Image.Image, format: str = "PNG") -> bytes:
        """將 PIL Image 轉換為位元組"""
        buffer = io.BytesIO()
        image.save(buffer, format=format)
        return buffer.getvalue()

    @staticmethod
    def bytes_to_base64(data: bytes) -> str:
        """將位元組轉換為 Base64 字串"""
        return base64.b64encode(data).decode("utf-8")

    @staticmethod
    def base64_to_bytes(data: str) -> bytes:
        """將 Base64 字串轉換為位元組"""
        return base64.b64decode(data)

    @staticmethod
    def save_temp_image(image_bytes: bytes) -> str:
        """儲存臨時圖片檔案並回傳路徑"""
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".png")
        temp_file.write(image_bytes)
        temp_file.close()
        return temp_file.name

    def embed_watermark(
        self,
        image_bytes: bytes,
        mode: str,
        password_img: int,
        password_wm: int,
        watermark_text: Optional[str] = None,
        watermark_image_bytes: Optional[bytes] = None,
        watermark_length: Optional[int] = None,
    ) -> Tuple[bytes, int]:
        """
        嵌入浮水印
        
        Args:
            image_bytes: 原始圖片位元組
            mode: 浮水印模式 (str/img/bit)
            password_img: 圖片密碼
            password_wm: 浮水印密碼
            watermark_text: 文字浮水印（mode=str 時使用）
            watermark_image_bytes: 圖片浮水印位元組（mode=img 時使用）
            watermark_length: 位元浮水印長度（mode=bit 時使用）
            
        Returns:
            (嵌入後圖片位元組, 浮水印位元長度)
        """
        # 儲存臨時檔案
        input_path = self.save_temp_image(image_bytes)
        output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name

        try:
            # 初始化浮水印物件
            bwm = WaterMark(password_img=password_img, password_wm=password_wm)
            bwm.read_img(input_path)

            # 根據模式讀取浮水印
            if mode == "str":
                if not watermark_text:
                    raise ValueError("文字模式需要提供 watermark_text")
                bwm.read_wm(watermark_text, mode="str")
            elif mode == "img":
                if not watermark_image_bytes:
                    raise ValueError("圖片模式需要提供 watermark_image_bytes")
                wm_path = self.save_temp_image(watermark_image_bytes)
                bwm.read_wm(wm_path, mode="img")
                Path(wm_path).unlink()
            elif mode == "bit":
                if watermark_length is None:
                    raise ValueError("位元模式需要提供 watermark_length")
                wm_bits = np.random.randint(0, 2, watermark_length)
                bwm.read_wm(wm_bits, mode="bit")
            else:
                raise ValueError(f"不支援的模式: {mode}")

            # 嵌入浮水印
            bwm.embed(output_path)
            wm_length = len(bwm.wm_bit)

            # 讀取輸出圖片
            with open(output_path, "rb") as f:
                output_bytes = f.read()

            return output_bytes, wm_length

        finally:
            # 清理臨時檔案
            Path(input_path).unlink(missing_ok=True)
            Path(output_path).unlink(missing_ok=True)

    def extract_watermark(
        self,
        image_bytes: bytes,
        mode: str,
        password_img: int,
        password_wm: int,
        watermark_length: int,
    ) -> Tuple[Optional[str], Optional[bytes]]:
        """
        提取浮水印
        
        Args:
            image_bytes: 含浮水印的圖片位元組
            mode: 浮水印模式 (str/img/bit)
            password_img: 圖片密碼
            password_wm: 浮水印密碼
            watermark_length: 浮水印位元長度
            
        Returns:
            (文字浮水印, 圖片浮水印位元組)
        """
        input_path = self.save_temp_image(image_bytes)

        try:
            # 初始化浮水印物件
            bwm = WaterMark(password_img=password_img, password_wm=password_wm)

            # 提取浮水印
            result = bwm.extract(input_path, wm_shape=watermark_length, mode=mode)

            if mode == "str":
                return result, None
            elif mode == "img":
                # 將提取的圖片轉為位元組
                output_path = tempfile.NamedTemporaryFile(delete=False, suffix=".png").name
                cv2.imwrite(output_path, result)
                with open(output_path, "rb") as f:
                    img_bytes = f.read()
                Path(output_path).unlink()
                return None, img_bytes
            elif mode == "bit":
                # 位元模式回傳字串表示
                return str(result.tolist()), None
            else:
                raise ValueError(f"不支援的模式: {mode}")

        finally:
            Path(input_path).unlink(missing_ok=True)

