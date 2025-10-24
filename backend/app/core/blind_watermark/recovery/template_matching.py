"""
模板匹配模組

用於估計裁剪和縮放攻擊的參數
"""
from typing import Optional, Tuple
import functools
import cv2
import numpy as np
import numpy.typing as npt

from ..types import RecoveryResult, ImageShape, CropParameters
from ..constants import DEFAULT_SCALE_MIN, DEFAULT_SCALE_MAX, DEFAULT_SEARCH_NUM
from ..utils import load_grayscale_image


class TemplateMatchingCache:
    """
    模板匹配快取
    
    使用類別而非全域變數來管理快取狀態
    """
    
    def __init__(self):
        self.idx: int = 0
        self.image: Optional[npt.NDArray] = None
        self.template: Optional[npt.NDArray] = None
    
    def set_images(self, image: npt.NDArray, template: npt.NDArray) -> None:
        """設定圖片並更新索引"""
        self.idx += 1
        self.image = image
        self.template = template
    
    def clear(self) -> None:
        """清除快取"""
        self.image = None
        self.template = None


# 全域快取實例
_cache = TemplateMatchingCache()


@functools.lru_cache(maxsize=None, typed=False)
def _match_template_cached(
    width: int,
    height: int,
    idx: int
) -> Tuple[Tuple[int, int], float]:
    """
    快取的模板匹配函數
    
    Args:
        width: 縮放後的寬度
        height: 縮放後的高度
        idx: 快取索引（用於失效控制）
        
    Returns:
        (位置, 匹配分數)
    """
    resized = cv2.resize(_cache.template, dsize=(width, height))
    scores = cv2.matchTemplate(_cache.image, resized, cv2.TM_CCOEFF_NORMED)
    ind = np.unravel_index(np.argmax(scores, axis=None), scores.shape)
    return ind, float(scores[ind])


def match_template_by_scale(scale: float) -> Tuple[Tuple[int, int], float, float]:
    """
    按縮放比例進行模板匹配
    
    Args:
        scale: 縮放比例
        
    Returns:
        (位置, 匹配分數, 縮放比例)
    """
    width = round(_cache.template.shape[1] * scale)
    height = round(_cache.template.shape[0] * scale)
    ind, score = _match_template_cached(width, height, _cache.idx)
    return ind, score, scale


def search_best_scale(
    scale_range: Tuple[float, float] = (DEFAULT_SCALE_MIN, DEFAULT_SCALE_MAX),
    search_num: int = DEFAULT_SEARCH_NUM
) -> Tuple[Tuple[int, int], float, float]:
    """
    搜尋最佳縮放比例
    
    使用兩階段搜尋：
    1. 粗搜尋：在整個範圍內均勻採樣
    2. 精搜尋：在最佳點附近細化搜尋
    
    Args:
        scale_range: 縮放範圍 (min, max)
        search_num: 搜尋點數
        
    Returns:
        (位置, 匹配分數, 最佳縮放比例)
    """
    min_scale, max_scale = scale_range
    
    # 限制最大縮放比例（避免超出圖片範圍）
    max_scale = min(
        max_scale,
        _cache.image.shape[0] / _cache.template.shape[0],
        _cache.image.shape[1] / _cache.template.shape[1]
    )
    
    results = []
    
    # 兩階段搜尋
    for iteration in range(2):
        # 在當前範圍內均勻採樣
        scales = np.linspace(min_scale, max_scale, search_num)
        
        for scale in scales:
            ind, score, scale = match_template_by_scale(scale)
            results.append((ind, score, scale))
        
        # 找到最佳結果
        best_idx = max(range(len(results)), key=lambda i: results[i][1])
        
        # 縮小搜尋範圍到最佳點附近
        min_scale = results[max(0, best_idx - 1)][2]
        max_scale = results[min(len(results) - 1, best_idx + 1)][2]
        
        # 根據範圍調整搜尋點數
        search_num = 2 * int(
            (max_scale - min_scale) * max(_cache.template.shape[1], _cache.template.shape[0])
        ) + 1
    
    return results[best_idx]


def estimate_crop_parameters(
    original_file: Optional[str] = None,
    template_file: Optional[str] = None,
    ori_img: Optional[npt.NDArray] = None,
    tem_img: Optional[npt.NDArray] = None,
    scale: Tuple[float, float] = (DEFAULT_SCALE_MIN, DEFAULT_SCALE_MAX),
    search_num: int = DEFAULT_SEARCH_NUM
) -> RecoveryResult:
    """
    估計裁剪和縮放攻擊的參數
    
    Args:
        original_file: 原始圖片路徑
        template_file: 攻擊後的圖片路徑
        ori_img: 原始圖片陣列
        tem_img: 攻擊後的圖片陣列
        scale: 縮放範圍
        search_num: 搜尋點數
        
    Returns:
        RecoveryResult 包含恢復參數
    """
    # 載入圖片
    ori_img = load_grayscale_image(filename=original_file, img=ori_img)
    tem_img = load_grayscale_image(filename=template_file, img=tem_img)
    
    # 設定快取
    _cache.set_images(ori_img, tem_img)
    
    try:
        if scale[0] == scale[1] == 1.0:
            # 無縮放：直接匹配
            scores = cv2.matchTemplate(ori_img, tem_img, cv2.TM_CCOEFF_NORMED)
            ind = np.unravel_index(np.argmax(scores, axis=None), scores.shape)
            score = float(scores[ind])
            scale_infer = 1.0
        else:
            # 有縮放：搜尋最佳縮放比例
            ind, score, scale_infer = search_best_scale(scale, search_num)
        
        # 計算裁剪參數
        width = int(tem_img.shape[1] * scale_infer)
        height = int(tem_img.shape[0] * scale_infer)
        
        x1, y1 = ind[1], ind[0]
        x2, y2 = x1 + width, y1 + height
        
        crop_params = CropParameters(x1=x1, y1=y1, x2=x2, y2=y2)
        original_shape = ImageShape.from_array(ori_img)
        
        return RecoveryResult(
            crop_params=crop_params,
            original_shape=original_shape,
            match_score=score,
            scale=scale_infer
        )
    
    finally:
        # 清除快取
        _cache.clear()
        _match_template_cached.cache_clear()

