"""水印主類別模組"""
from typing import Optional, Union, Tuple
import numpy as np
import numpy.typing as npt

from ..types import WatermarkMode, WatermarkBitArray, PoolMode
from ..exceptions import InvalidModeError, WatermarkShapeError
from ..utils import (
    load_image, load_grayscale_image, save_image,
    shuffle_watermark, unshuffle_watermark
)
from ..version import bw_notes
from .engine import WaterMarkCore
from .converters import (
    image_to_bits, string_to_bits,
    bits_to_image, bits_to_string, bits_to_boolean
)


class WaterMark:
    """
    盲水印主類別
    
    支援三種水印模式：
    - 'img': 圖片水印
    - 'str': 文字水印
    - 'bit': 位元陣列水印
    """
    
    VALID_MODES = ('img', 'str', 'bit')
    
    def __init__(
        self,
        password_wm: int = 1,
        password_img: int = 1,
        mode: PoolMode = 'common',
        processes: Optional[int] = None,
        robustness_primary: int = 36,
        robustness_secondary: int = 20,
        fast_mode: bool = False
    ):
        """
        初始化水印物件
        
        Args:
            password_wm: 水印層級密碼（用於打亂水印位元）
            password_img: 圖片層級密碼（用於打亂分塊順序）
            mode: 並行處理模式
            processes: 進程/執行緒數量
            robustness_primary: 主要魯棒性參數（越大越強但失真越大）
            robustness_secondary: 次要魯棒性參數
            fast_mode: 快速模式（僅使用主奇異值）
        """
        bw_notes.print_notes()
        
        self.bwm_core = WaterMarkCore(
            password_img=password_img,
            mode=mode,
            processes=processes,
            robustness_primary=robustness_primary,
            robustness_secondary=robustness_secondary,
            fast_mode=fast_mode
        )
        
        self.password_wm = password_wm
        self.wm_bit: Optional[WatermarkBitArray] = None
        self.wm_size: int = 0
    
    def read_img(
        self,
        filename: Optional[str] = None,
        img: Optional[npt.NDArray] = None
    ) -> npt.NDArray:
        """
        讀取原始圖片
        
        Args:
            filename: 圖片檔案路徑
            img: 已載入的圖片陣列
            
        Returns:
            圖片陣列
        """
        img_array = load_image(filename=filename, img=img)
        self.bwm_core.read_img_arr(img=img_array)
        return img_array
    
    def read_wm(self, wm_content: Union[str, npt.NDArray], mode: WatermarkMode = 'img') -> None:
        """讀取水印內容"""
        if mode not in self.VALID_MODES:
            raise InvalidModeError(mode, self.VALID_MODES)

        if mode == 'img':
            wm_img = load_grayscale_image(filename=wm_content)
            self.wm_bit = image_to_bits(wm_img)
        elif mode == 'str':
            self.wm_bit = string_to_bits(wm_content)
        else:  # mode == 'bit'
            self.wm_bit = np.array(wm_content, dtype=bool)

        self.wm_size = self.wm_bit.size
        self.wm_bit = shuffle_watermark(self.wm_bit, self.password_wm)
        self.bwm_core.read_wm(self.wm_bit)
    
    def embed(self, filename: Optional[str] = None, compression_ratio: Optional[int] = None) -> npt.NDArray:
        """嵌入水印"""
        embed_img = self.bwm_core.embed()
        if filename is not None:
            save_image(filename, embed_img, compression_ratio)
        return embed_img

    def extract(
        self,
        filename: Optional[str] = None,
        embed_img: Optional[npt.NDArray] = None,
        wm_shape: Optional[Union[int, Tuple[int, ...]]] = None,
        out_wm_name: Optional[str] = None,
        mode: WatermarkMode = 'img'
    ) -> Union[str, npt.NDArray]:
        """提取水印"""
        if wm_shape is None:
            raise WatermarkShapeError("必須提供 wm_shape 參數")
        if mode not in self.VALID_MODES:
            raise InvalidModeError(mode, self.VALID_MODES)

        img_array = load_image(filename=filename, img=embed_img)

        if isinstance(wm_shape, int):
            self.wm_size = wm_shape
            wm_shape_tuple = (wm_shape,)
        else:
            self.wm_size = int(np.prod(wm_shape))
            wm_shape_tuple = wm_shape

        if mode in ('str', 'bit'):
            wm_avg = self.bwm_core.extract_with_kmeans(img=img_array, wm_shape=wm_shape_tuple)
        else:
            wm_avg = self.bwm_core.extract(img=img_array, wm_shape=wm_shape_tuple)

        wm = unshuffle_watermark(wm_avg, self.password_wm)

        if mode == 'img':
            return bits_to_image(wm, wm_shape_tuple, out_wm_name)
        elif mode == 'str':
            return bits_to_string(wm)
        else:  # mode == 'bit'
            return bits_to_boolean(wm)

