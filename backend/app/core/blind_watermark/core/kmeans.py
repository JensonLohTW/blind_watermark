"""
K-means 聚類演算法模組

用於水印提取時的二值化處理
"""
import numpy as np
import numpy.typing as npt

from ..constants import KMEANS_MAX_ITERATIONS, KMEANS_TOLERANCE
from ..types import WatermarkBitArray


def one_dim_kmeans(
    inputs: npt.NDArray[np.float64],
    max_iterations: int = KMEANS_MAX_ITERATIONS,
    tolerance: float = KMEANS_TOLERANCE
) -> WatermarkBitArray:
    """
    一維 K-means 聚類（k=2）
    
    將連續值陣列二值化為 0/1
    
    Args:
        inputs: 輸入的連續值陣列
        max_iterations: 最大迭代次數
        tolerance: 收斂容差
        
    Returns:
        二值化後的布林陣列
        
    演算法流程：
    1. 初始化兩個中心點為最小值和最大值
    2. 計算閾值（兩中心點的平均）
    3. 根據閾值將所有點分為兩類
    4. 重新計算兩類的中心點
    5. 檢查收斂條件，未收斂則回到步驟 2
    """
    # 初始化中心點
    center_0 = inputs.min()
    center_1 = inputs.max()
    threshold = (center_0 + center_1) / 2
    
    for iteration in range(max_iterations):
        # 分類
        is_class_1 = inputs > threshold
        
        # 重新計算中心點
        new_center_0 = inputs[~is_class_1].mean()
        new_center_1 = inputs[is_class_1].mean()
        new_threshold = (new_center_0 + new_center_1) / 2
        
        # 檢查收斂
        if np.abs(new_threshold - threshold) < tolerance:
            threshold = new_threshold
            break
        
        threshold = new_threshold
        center_0 = new_center_0
        center_1 = new_center_1
    
    # 返回最終分類結果
    return inputs > threshold

