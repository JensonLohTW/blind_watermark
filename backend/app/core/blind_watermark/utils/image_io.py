"""
圖片讀寫工具模組

提供統一的圖片讀取、保存介面，並處理錯誤
"""
from typing import Optional
import cv2
import numpy as np
import numpy.typing as npt

from ..exceptions import ImageReadError
from ..constants import PIXEL_MAX_VALUE, PIXEL_MIN_VALUE


def load_image(
    filename: Optional[str] = None,
    img: Optional[npt.NDArray] = None,
    flags: int = cv2.IMREAD_UNCHANGED
) -> npt.NDArray:
    """
    載入圖片
    
    Args:
        filename: 圖片檔案路徑
        img: 已載入的圖片陣列
        flags: OpenCV 讀取標誌
        
    Returns:
        圖片陣列
        
    Raises:
        ImageReadError: 圖片讀取失敗
        ValueError: filename 和 img 都未提供
    """
    if img is not None:
        return img
    
    if filename is None:
        raise ValueError("必須提供 filename 或 img 參數")
    
    result = cv2.imread(filename, flags=flags)
    if result is None:
        raise ImageReadError(filename)
    
    return result


def load_grayscale_image(
    filename: Optional[str] = None,
    img: Optional[npt.NDArray] = None
) -> npt.NDArray:
    """
    載入灰階圖片
    
    Args:
        filename: 圖片檔案路徑
        img: 已載入的圖片陣列
        
    Returns:
        灰階圖片陣列
    """
    return load_image(filename, img, flags=cv2.IMREAD_GRAYSCALE)


def save_image(
    filename: str,
    img: npt.NDArray,
    compression_ratio: Optional[int] = None
) -> None:
    """
    保存圖片
    
    Args:
        filename: 輸出檔案路徑
        img: 圖片陣列
        compression_ratio: 壓縮比率 (0-100)，None 表示不壓縮
    """
    # 確保像素值在有效範圍內
    img_clipped = np.clip(img, PIXEL_MIN_VALUE, PIXEL_MAX_VALUE)
    
    if compression_ratio is None:
        cv2.imwrite(filename, img_clipped)
    elif filename.endswith('.jpg') or filename.endswith('.jpeg'):
        cv2.imwrite(
            filename,
            img_clipped,
            params=[cv2.IMWRITE_JPEG_QUALITY, compression_ratio]
        )
    elif filename.endswith('.png'):
        cv2.imwrite(
            filename,
            img_clipped,
            params=[cv2.IMWRITE_PNG_COMPRESSION, compression_ratio]
        )
    else:
        cv2.imwrite(filename, img_clipped)


def ensure_even_dimensions(img: npt.NDArray) -> npt.NDArray:
    """
    確保圖片尺寸為偶數（DWT 要求）
    
    Args:
        img: 輸入圖片
        
    Returns:
        尺寸為偶數的圖片
    """
    pad_height = img.shape[0] % 2
    pad_width = img.shape[1] % 2
    
    if pad_height == 0 and pad_width == 0:
        return img
    
    return cv2.copyMakeBorder(
        img,
        0, pad_height,
        0, pad_width,
        cv2.BORDER_CONSTANT,
        value=(0, 0, 0)
    )

