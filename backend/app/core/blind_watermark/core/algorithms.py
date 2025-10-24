"""
DWT-DCT-SVD 演算法模組

實作水印嵌入與提取的核心演算法
"""
from typing import Tuple
import numpy as np
import numpy.typing as npt
from numpy.linalg import svd
from cv2 import dct, idct

from ..constants import (
    SVD_QUANTIZATION_OFFSET,
    SVD_WATERMARK_WEIGHT,
    PRIMARY_SINGULAR_VALUE_WEIGHT,
    SECONDARY_SINGULAR_VALUE_WEIGHT,
    TOTAL_WEIGHT
)
from ..types import BlockShape, ShuffleIndexArray


def embed_watermark_in_block_slow(
    block: npt.NDArray[np.float32],
    shuffler: ShuffleIndexArray,
    watermark_bit: bool,
    d1: int,
    d2: int,
    block_shape: BlockShape
) -> npt.NDArray[np.float32]:
    """
    在單個分塊中嵌入水印（慢速模式，使用兩個奇異值）
    
    流程：DCT → 打亂 → SVD → 修改奇異值 → 逆 SVD → 還原順序 → 逆 DCT
    
    Args:
        block: 4x4 分塊
        shuffler: 打亂索引
        watermark_bit: 要嵌入的水印位元（0 或 1）
        d1: 主要奇異值的量化步長
        d2: 次要奇異值的量化步長
        block_shape: 分塊形狀
        
    Returns:
        嵌入水印後的分塊
    """
    # DCT 變換
    block_dct = dct(block)
    
    # 打亂順序（加密）
    block_dct_shuffled = block_dct.flatten()[shuffler].reshape(
        block_shape.to_array()
    )
    
    # SVD 分解
    u, s, v = svd(block_dct_shuffled)
    
    # 修改奇異值嵌入水印
    # s[0] = (s[0] // d1 + 1/4 + 1/2 * wm_bit) * d1
    s[0] = (s[0] // d1 + SVD_QUANTIZATION_OFFSET + SVD_WATERMARK_WEIGHT * watermark_bit) * d1
    
    if d2:
        s[1] = (s[1] // d2 + SVD_QUANTIZATION_OFFSET + SVD_WATERMARK_WEIGHT * watermark_bit) * d2
    
    # 逆 SVD
    block_dct_modified = np.dot(u, np.dot(np.diag(s), v))
    
    # 還原順序（解密）
    block_dct_flatten = block_dct_modified.flatten()
    block_dct_restored = block_dct_flatten.copy()
    block_dct_restored[shuffler] = block_dct_flatten
    
    # 逆 DCT
    return idct(block_dct_restored.reshape(block_shape.to_array()))


def embed_watermark_in_block_fast(
    block: npt.NDArray[np.float32],
    watermark_bit: bool,
    d1: int
) -> npt.NDArray[np.float32]:
    """
    在單個分塊中嵌入水印（快速模式，僅使用主要奇異值）
    
    流程：DCT → SVD → 修改主奇異值 → 逆 SVD → 逆 DCT
    
    Args:
        block: 4x4 分塊
        watermark_bit: 要嵌入的水印位元
        d1: 主要奇異值的量化步長
        
    Returns:
        嵌入水印後的分塊
    """
    # DCT 變換
    block_dct = dct(block)
    
    # SVD 分解
    u, s, v = svd(block_dct)
    
    # 修改主奇異值
    s[0] = (s[0] // d1 + SVD_QUANTIZATION_OFFSET + SVD_WATERMARK_WEIGHT * watermark_bit) * d1
    
    # 逆 SVD 和逆 DCT
    return idct(np.dot(u, np.dot(np.diag(s), v)))


def extract_watermark_from_block_slow(
    block: npt.NDArray[np.float32],
    shuffler: ShuffleIndexArray,
    d1: int,
    d2: int,
    block_shape: BlockShape
) -> float:
    """
    從單個分塊中提取水印（慢速模式，使用兩個奇異值）
    
    流程：DCT → 打亂 → SVD → 提取水印位元
    
    Args:
        block: 4x4 分塊
        shuffler: 打亂索引
        d1: 主要奇異值的量化步長
        d2: 次要奇異值的量化步長
        block_shape: 分塊形狀
        
    Returns:
        提取的水印值（0-1 之間的浮點數）
    """
    # DCT 變換並打亂
    block_dct_shuffled = dct(block).flatten()[shuffler].reshape(
        block_shape.to_array()
    )
    
    # SVD 分解
    u, s, v = svd(block_dct_shuffled)
    
    # 從主奇異值提取
    wm_primary = float((s[0] % d1) > (d1 / 2))
    
    if d2:
        # 從次奇異值提取
        wm_secondary = float((s[1] % d2) > (d2 / 2))
        # 加權平均
        wm = (wm_primary * PRIMARY_SINGULAR_VALUE_WEIGHT + 
              wm_secondary * SECONDARY_SINGULAR_VALUE_WEIGHT) / TOTAL_WEIGHT
    else:
        wm = wm_primary
    
    return wm


def extract_watermark_from_block_fast(
    block: npt.NDArray[np.float32],
    d1: int
) -> float:
    """
    從單個分塊中提取水印（快速模式，僅使用主要奇異值）
    
    Args:
        block: 4x4 分塊
        d1: 主要奇異值的量化步長
        
    Returns:
        提取的水印值（0 或 1）
    """
    # DCT 變換
    block_dct = dct(block)
    
    # SVD 分解
    u, s, v = svd(block_dct)
    
    # 從主奇異值提取
    return float((s[0] % d1) > (d1 / 2))

