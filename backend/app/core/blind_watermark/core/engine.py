"""水印核心引擎模組"""
from typing import Tuple
import numpy as np
import numpy.typing as npt
import cv2
from pywt import idwt2

from ..types import WatermarkBitArray, BlockShape, PoolMode
from ..constants import (
    DEFAULT_ROBUSTNESS_PRIMARY,
    DEFAULT_ROBUSTNESS_SECONDARY,
    YUV_CHANNELS,
    WAVELET_BASIS,
    PIXEL_MAX_VALUE,
    PIXEL_MIN_VALUE
)
from ..exceptions import WatermarkCapacityError
from ..utils import AutoPool, generate_shuffle_indices
from .algorithms import (
    embed_watermark_in_block_slow,
    embed_watermark_in_block_fast,
    extract_watermark_from_block_slow,
    extract_watermark_from_block_fast
)
from .kmeans import one_dim_kmeans
from .image_processor import ImageProcessor


class WaterMarkCore:
    """水印核心引擎"""

    def __init__(
        self,
        password_img: int = 1,
        mode: PoolMode = 'common',
        processes: int = None,
        robustness_primary: int = DEFAULT_ROBUSTNESS_PRIMARY,
        robustness_secondary: int = DEFAULT_ROBUSTNESS_SECONDARY,
        fast_mode: bool = False
    ):
        """初始化核心引擎"""
        self.block_shape = BlockShape()
        self.password_img = password_img
        self.d1 = robustness_primary
        self.d2 = robustness_secondary
        self.fast_mode = fast_mode

        # 圖片處理器
        self.processor = ImageProcessor(self.block_shape)

        # 水印資料
        self.wm_bit: WatermarkBitArray = None
        self.wm_size: int = 0
        self.block_num: int = 0
        self.idx_shuffle: npt.NDArray = None

        # 並行處理池
        self.pool = AutoPool(mode=mode, processes=processes)
    
    def read_img_arr(self, img: npt.NDArray) -> None:
        """讀取圖片陣列並進行預處理"""
        self.processor.process_image(img)
    
    def read_wm(self, wm_bit: WatermarkBitArray) -> None:
        """讀取水印位元陣列"""
        self.wm_bit = wm_bit
        self.wm_size = wm_bit.size

    def init_block_index(self) -> None:
        """初始化分塊索引"""
        self.block_num = self.processor.init_block_index()

        # 檢查容量
        if self.wm_size > self.block_num:
            raise WatermarkCapacityError(
                required_bits=self.wm_size,
                available_bits=self.block_num
            )

    def embed(self) -> npt.NDArray:
        """嵌入水印"""
        self.init_block_index()
        self.idx_shuffle = generate_shuffle_indices(
            self.password_img, self.block_num, self.block_shape.size()
        )

        embed_ca = [ca.copy() for ca in self.processor.ca]
        embed_YUV = [np.array([])] * YUV_CHANNELS

        for channel in range(YUV_CHANNELS):
            if self.fast_mode:
                embed_func = lambda args: embed_watermark_in_block_fast(
                    args[0], self.wm_bit[args[2] % self.wm_size], self.d1
                )
            else:
                embed_func = lambda args: embed_watermark_in_block_slow(
                    args[0], args[1], self.wm_bit[args[2] % self.wm_size],
                    self.d1, self.d2, self.block_shape
                )

            args_list = [
                (self.processor.ca_block[channel][self.processor.block_index[i]], self.idx_shuffle[i], i)
                for i in range(self.block_num)
            ]
            embedded_blocks = self.pool.map(embed_func, args_list)

            for i in range(self.block_num):
                self.processor.ca_block[channel][self.processor.block_index[i]] = embedded_blocks[i]

            self.processor.ca_part[channel] = np.concatenate(
                np.concatenate(self.processor.ca_block[channel], 1), 1
            )
            embed_ca[channel][:self.processor.part_shape[0], :self.processor.part_shape[1]] = \
                self.processor.ca_part[channel]
            embed_YUV[channel] = idwt2(
                (embed_ca[channel], self.processor.hvd[channel]), WAVELET_BASIS
            )

        embed_img_YUV = np.stack(embed_YUV, axis=2)
        embed_img_YUV = embed_img_YUV[:self.processor.img_shape[0], :self.processor.img_shape[1]]
        embed_img = cv2.cvtColor(embed_img_YUV, cv2.COLOR_YUV2BGR)
        embed_img = np.clip(embed_img, PIXEL_MIN_VALUE, PIXEL_MAX_VALUE)

        if self.processor.alpha is not None:
            embed_img = cv2.merge([embed_img.astype(np.uint8), self.processor.alpha])
        return embed_img

    def extract_raw(self, img: npt.NDArray) -> npt.NDArray[np.float64]:
        """提取原始水印位元"""
        self.read_img_arr(img=img)
        self.init_block_index()
        self.idx_shuffle = generate_shuffle_indices(
            self.password_img, self.block_num, self.block_shape.size()
        )

        wm_block_bit = np.zeros(shape=(YUV_CHANNELS, self.block_num))

        for channel in range(YUV_CHANNELS):
            if self.fast_mode:
                extract_func = lambda args: extract_watermark_from_block_fast(
                    args[0], self.d1
                )
            else:
                extract_func = lambda args: extract_watermark_from_block_slow(
                    args[0], args[1], self.d1, self.d2, self.block_shape
                )

            args_list = [
                (self.processor.ca_block[channel][self.processor.block_index[i]], self.idx_shuffle[i])
                for i in range(self.block_num)
            ]
            wm_block_bit[channel, :] = self.pool.map(extract_func, args_list)

        return wm_block_bit

    def extract_avg(self, wm_block_bit: npt.NDArray[np.float64]) -> npt.NDArray[np.float64]:
        """
        對循環嵌入和 3 個通道求平均（向量化優化版本）

        原始版本使用迴圈，時間複雜度 O(wm_size × block_num)
        優化版本使用 reshape + mean，時間複雜度 O(block_num)
        """
        # 計算可以完整循環的部分
        num_complete_cycles = self.block_num // self.wm_size

        if num_complete_cycles > 0:
            # 截取完整循環部分
            complete_part = wm_block_bit[:, :num_complete_cycles * self.wm_size]
            # Reshape 並求平均：(3, num_cycles, wm_size) -> (wm_size,)
            reshaped = complete_part.reshape(YUV_CHANNELS, num_complete_cycles, self.wm_size)
            wm_avg = reshaped.mean(axis=(0, 1))

            # 處理剩餘部分
            remainder = self.block_num % self.wm_size
            if remainder > 0:
                remainder_part = wm_block_bit[:, -remainder:]
                # 將剩餘部分加權平均
                for i in range(remainder):
                    wm_avg[i] = (wm_avg[i] * num_complete_cycles + remainder_part[:, i].mean()) / (num_complete_cycles + 1)
        else:
            # 如果 block_num < wm_size，直接對每個位置求平均
            wm_avg = wm_block_bit.mean(axis=0)

        return wm_avg

    def extract(self, img: npt.NDArray, wm_shape: Tuple[int, ...]) -> npt.NDArray[np.float64]:
        """提取水印"""
        self.wm_size = int(np.prod(wm_shape))
        wm_block_bit = self.extract_raw(img=img)
        return self.extract_avg(wm_block_bit)

    def extract_with_kmeans(
        self, img: npt.NDArray, wm_shape: Tuple[int, ...]
    ) -> WatermarkBitArray:
        """提取水印並使用 K-means 二值化"""
        wm_avg = self.extract(img=img, wm_shape=wm_shape)
        return one_dim_kmeans(wm_avg)

