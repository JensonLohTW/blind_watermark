"""
圖片預處理模組

處理圖片的 DWT 分解、分塊等預處理操作
"""
from typing import Tuple, List
import numpy as np
import numpy.typing as npt
import cv2
from pywt import dwt2

from ..types import BlockShape
from ..constants import (
    YUV_CHANNELS,
    WAVELET_BASIS,
    BORDER_VALUE_Y,
    BORDER_VALUE_U,
    BORDER_VALUE_V,
    PIXEL_MAX_VALUE
)


class ImageProcessor:
    """圖片預處理器"""
    
    def __init__(self, block_shape: BlockShape):
        """
        初始化
        
        Args:
            block_shape: 分塊形狀
        """
        self.block_shape = block_shape
        
        # 圖片資料
        self.img: npt.NDArray = None
        self.img_YUV: npt.NDArray = None
        self.img_shape: Tuple[int, int] = None
        self.alpha: npt.NDArray = None
        
        # DWT 分解結果
        self.ca: List[npt.NDArray] = [np.array([])] * YUV_CHANNELS
        self.hvd: List[Tuple] = [None] * YUV_CHANNELS
        
        # 分塊資料
        self.ca_block: List[npt.NDArray] = [np.array([])] * YUV_CHANNELS
        self.ca_part: List[npt.NDArray] = [np.array([])] * YUV_CHANNELS
        self.ca_shape: Tuple[int, int] = None
        self.ca_block_shape: Tuple[int, int, int, int] = None
        self.part_shape: npt.NDArray = None
        self.block_index: List[Tuple[int, int]] = []
    
    def process_image(self, img: npt.NDArray) -> None:
        """
        處理圖片
        
        流程：
        1. 處理透明通道
        2. 轉換為 YUV
        3. 填充邊界
        4. DWT 分解
        5. 分塊
        
        Args:
            img: 輸入圖片
        """
        # 處理透明通道
        self.alpha = None
        if len(img.shape) == 3 and img.shape[2] == 4:
            if img[:, :, 3].min() < PIXEL_MAX_VALUE:
                self.alpha = img[:, :, 3]
                img = img[:, :, :3]
        
        # 轉換為浮點數
        self.img = img.astype(np.float32)
        self.img_shape = self.img.shape[:2]
        
        # 轉換為 YUV 並填充邊界
        self.img_YUV = cv2.copyMakeBorder(
            cv2.cvtColor(self.img, cv2.COLOR_BGR2YUV),
            0, self.img.shape[0] % 2,
            0, self.img.shape[1] % 2,
            cv2.BORDER_CONSTANT,
            value=(BORDER_VALUE_Y, BORDER_VALUE_U, BORDER_VALUE_V)
        )
        
        # 計算 DWT 後的尺寸
        self.ca_shape = tuple((i + 1) // 2 for i in self.img_shape)
        
        # 計算分塊形狀
        self.ca_block_shape = (
            self.ca_shape[0] // self.block_shape.height,
            self.ca_shape[1] // self.block_shape.width,
            self.block_shape.height,
            self.block_shape.width
        )
        
        # 計算 stride
        strides = 4 * np.array([
            self.ca_shape[1] * self.block_shape.height,
            self.block_shape.width,
            self.ca_shape[1],
            1
        ])
        
        # 對每個通道進行 DWT 分解和分塊
        for channel in range(YUV_CHANNELS):
            self.ca[channel], self.hvd[channel] = dwt2(
                self.img_YUV[:, :, channel],
                WAVELET_BASIS
            )
            
            # 使用 stride tricks 進行分塊
            self.ca_block[channel] = np.lib.stride_tricks.as_strided(
                self.ca[channel].astype(np.float32),
                self.ca_block_shape,
                strides
            )
    
    def init_block_index(self) -> int:
        """
        初始化分塊索引
        
        Returns:
            分塊數量
        """
        block_num = self.ca_block_shape[0] * self.ca_block_shape[1]
        
        # 計算實際使用的部分形狀
        self.part_shape = np.array([
            self.ca_block_shape[0],
            self.ca_block_shape[1]
        ]) * self.block_shape.to_array()
        
        # 生成分塊索引
        self.block_index = [
            (i, j)
            for i in range(self.ca_block_shape[0])
            for j in range(self.ca_block_shape[1])
        ]
        
        return block_num
    
    def get_block_num(self) -> int:
        """獲取分塊數量"""
        return self.ca_block_shape[0] * self.ca_block_shape[1]

