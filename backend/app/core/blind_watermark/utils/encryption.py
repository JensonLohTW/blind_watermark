"""
加密/解密工具模組

提供水印位元的加密與解密功能
"""
import numpy as np
import numpy.typing as npt

from ..types import WatermarkBitArray, ShuffleIndexArray


def generate_shuffle_indices(
    password: int,
    size: int,
    block_shape: int
) -> ShuffleIndexArray:
    """
    生成打亂索引
    
    Args:
        password: 密碼種子
        size: 索引數量
        block_shape: 分塊大小
        
    Returns:
        打亂索引陣列，形狀為 (size, block_shape)
    """
    return np.random.RandomState(password) \
        .random(size=(size, block_shape)) \
        .argsort(axis=1)


def shuffle_watermark(
    wm_bit: WatermarkBitArray,
    password: int
) -> WatermarkBitArray:
    """
    加密水印位元（打亂順序）
    
    Args:
        wm_bit: 原始水印位元陣列
        password: 加密密碼
        
    Returns:
        加密後的水印位元陣列
    """
    shuffled = wm_bit.copy()
    np.random.RandomState(password).shuffle(shuffled)
    return shuffled


def unshuffle_watermark(
    wm_avg: npt.NDArray[np.float64],
    password: int
) -> npt.NDArray[np.float64]:
    """
    解密水印（還原順序）
    
    Args:
        wm_avg: 提取的水印平均值陣列
        password: 解密密碼
        
    Returns:
        解密後的水印陣列
    """
    wm_size = wm_avg.size
    wm_index = np.arange(wm_size)
    np.random.RandomState(password).shuffle(wm_index)
    
    # 還原順序
    result = wm_avg.copy()
    result[wm_index] = wm_avg.copy()
    return result

