"""
水印格式轉換模組

處理不同格式水印之間的轉換
"""
from typing import Tuple
import numpy as np
import numpy.typing as npt

from ..types import WatermarkBitArray
from ..constants import IMAGE_BINARIZATION_THRESHOLD, PIXEL_MAX_VALUE
from ..utils import save_image


def image_to_bits(wm_img: npt.NDArray) -> WatermarkBitArray:
    """
    將灰階圖片轉換為位元陣列
    
    Args:
        wm_img: 灰階圖片陣列
        
    Returns:
        位元陣列
    """
    return wm_img.flatten() > IMAGE_BINARIZATION_THRESHOLD


def string_to_bits(text: str) -> WatermarkBitArray:
    """
    將文字轉換為位元陣列
    
    Args:
        text: 文字內容
        
    Returns:
        位元陣列
    """
    byte_str = bin(int(text.encode('utf-8').hex(), base=16))[2:]
    return np.array(list(byte_str), dtype=bool) == '1'


def bits_to_image(
    wm_bits: npt.NDArray[np.float64],
    shape: Tuple[int, int],
    output_file: str = None
) -> npt.NDArray:
    """
    將位元陣列轉換為灰階圖片
    
    Args:
        wm_bits: 位元陣列（可以是浮點數）
        shape: 圖片形狀 (height, width)
        output_file: 輸出檔案路徑（可選）
        
    Returns:
        灰階圖片陣列
    """
    wm_img = PIXEL_MAX_VALUE * wm_bits.reshape(shape[0], shape[1])
    
    if output_file:
        save_image(output_file, wm_img)
    
    return wm_img


def bits_to_string(wm_bits: npt.NDArray[np.float64]) -> str:
    """
    將位元陣列轉換為文字
    
    Args:
        wm_bits: 位元陣列（可以是浮點數）
        
    Returns:
        文字內容
    """
    # 轉換為二進位字串
    byte_str = ''.join(str(int(i >= 0.5)) for i in wm_bits)
    
    try:
        # 轉換為十六進位再解碼
        wm_str = bytes.fromhex(hex(int(byte_str, base=2))[2:]).decode(
            'utf-8', errors='replace'
        )
    except ValueError:
        wm_str = ''
    
    return wm_str


def bits_to_boolean(wm_bits: npt.NDArray[np.float64]) -> WatermarkBitArray:
    """
    將浮點數位元陣列轉換為布林陣列
    
    Args:
        wm_bits: 浮點數位元陣列
        
    Returns:
        布林陣列
    """
    return wm_bits >= 0.5

