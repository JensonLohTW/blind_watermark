"""
顏色攻擊模組

包含亮度調整等顏色相關攻擊
"""
from typing import Optional
import numpy as np
import numpy.typing as npt

from ..types import AttackResult
from ..constants import PIXEL_MAX_VALUE
from ..utils import load_image, save_image


def brightness_attack(
    input_filename: Optional[str] = None,
    input_img: Optional[npt.NDArray] = None,
    output_file_name: Optional[str] = None,
    ratio: float = 0.8
) -> AttackResult:
    """
    亮度調整攻擊
    
    Args:
        input_filename: 輸入圖片路徑
        input_img: 輸入圖片陣列
        output_file_name: 輸出檔案路徑
        ratio: 亮度比例（>1 變亮，<1 變暗）
        
    Returns:
        AttackResult 包含攻擊後的圖片
    """
    img = load_image(filename=input_filename, img=input_img)
    
    # 調整亮度
    output_img = img * ratio
    
    # 限制在有效範圍內
    output_img = np.clip(output_img, 0, PIXEL_MAX_VALUE)
    
    if output_file_name:
        save_image(output_file_name, output_img)
    
    return AttackResult(image=output_img)


# 向後相容的別名
bright_att = brightness_attack

