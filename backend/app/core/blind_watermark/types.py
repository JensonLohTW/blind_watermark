"""
型別定義模組

定義盲水印系統中使用的核心資料結構與型別別名
"""
from dataclasses import dataclass
from typing import Tuple, Optional, Literal, Union
import numpy as np
import numpy.typing as npt

# 型別別名
ImageArray = npt.NDArray[np.float32]
WatermarkBitArray = npt.NDArray[np.bool_]
ShuffleIndexArray = npt.NDArray[np.int_]

# 水印模式
WatermarkMode = Literal['img', 'str', 'bit']

# 並行處理模式
PoolMode = Literal['common', 'multithreading', 'multiprocessing', 'vectorization', 'cached']


@dataclass(frozen=True)
class ImageShape:
    """圖片尺寸"""
    height: int
    width: int
    channels: int = 3
    
    @classmethod
    def from_array(cls, img: npt.NDArray) -> 'ImageShape':
        """從 numpy 陣列創建"""
        if len(img.shape) == 2:
            return cls(height=img.shape[0], width=img.shape[1], channels=1)
        return cls(height=img.shape[0], width=img.shape[1], channels=img.shape[2])
    
    def to_tuple(self) -> Tuple[int, int]:
        """轉換為 (height, width) tuple"""
        return (self.height, self.width)
    
    def to_full_tuple(self) -> Tuple[int, int, int]:
        """轉換為 (height, width, channels) tuple"""
        return (self.height, self.width, self.channels)


@dataclass(frozen=True)
class BlockShape:
    """分塊尺寸"""
    height: int = 4
    width: int = 4
    
    def to_array(self) -> npt.NDArray[np.int_]:
        """轉換為 numpy 陣列"""
        return np.array([self.height, self.width])
    
    def size(self) -> int:
        """總元素數"""
        return self.height * self.width


@dataclass(frozen=True)
class CropParameters:
    """裁剪參數"""
    x1: int
    y1: int
    x2: int
    y2: int
    
    def to_tuple(self) -> Tuple[int, int, int, int]:
        """轉換為 tuple"""
        return (self.x1, self.y1, self.x2, self.y2)
    
    @classmethod
    def from_tuple(cls, loc: Tuple[int, int, int, int]) -> 'CropParameters':
        """從 tuple 創建"""
        return cls(x1=loc[0], y1=loc[1], x2=loc[2], y2=loc[3])
    
    def width(self) -> int:
        """寬度"""
        return self.x2 - self.x1
    
    def height(self) -> int:
        """高度"""
        return self.y2 - self.y1


@dataclass(frozen=True)
class AttackResult:
    """攻擊結果"""
    image: npt.NDArray
    parameters: Optional[CropParameters] = None
    scale: float = 1.0
    
    
@dataclass(frozen=True)
class RecoveryResult:
    """恢復結果"""
    crop_params: CropParameters
    original_shape: ImageShape
    match_score: float
    scale: float
    
    
@dataclass(frozen=True)
class WatermarkConfig:
    """水印配置"""
    password_wm: int = 1
    password_img: int = 1
    block_shape: BlockShape = BlockShape()
    mode: PoolMode = 'common'
    processes: Optional[int] = None
    
    # 魯棒性參數（越大越強但失真越大）
    robustness_primary: int = 36  # d1
    robustness_secondary: int = 20  # d2
    
    # 快速模式（僅使用主要奇異值）
    fast_mode: bool = False


@dataclass
class WatermarkData:
    """水印資料"""
    bit_array: WatermarkBitArray
    size: int
    mode: WatermarkMode
    original_content: Union[str, npt.NDArray, None] = None
    
    def __post_init__(self):
        """驗證資料一致性"""
        if self.size != self.bit_array.size:
            raise ValueError(f"size ({self.size}) 與 bit_array.size ({self.bit_array.size}) 不一致")

