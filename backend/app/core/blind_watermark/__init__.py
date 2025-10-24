"""
盲水印系統

基於 DWT-DCT-SVD 的數位水印嵌入與提取系統
"""

# 核心類別
from .core import WaterMark, WaterMarkCore

# 攻擊模擬
from .attacks import (
    crop_attack,
    resize_attack,
    rotation_attack,
    salt_pepper_attack,
    shelter_attack,
    brightness_attack
)

# 恢復演算法
from .recovery import estimate_crop_parameters, recover_crop

# 版本資訊
from .version import __version__, bw_notes

# 向後相容：匯出舊的攻擊函數名稱
from .attacks.geometric import cut_att3, cut_att2, resize_att, rot_att
from .attacks.noise import salt_pepper_att, shelter_att
from .attacks.color import bright_att

__all__ = [
    # 核心
    'WaterMark',
    'WaterMarkCore',
    # 攻擊
    'crop_attack',
    'resize_attack',
    'rotation_attack',
    'salt_pepper_attack',
    'shelter_attack',
    'brightness_attack',
    # 恢復
    'estimate_crop_parameters',
    'recover_crop',
    # 版本
    '__version__',
    'bw_notes',
    # 向後相容
    'cut_att3',
    'cut_att2',
    'resize_att',
    'rot_att',
    'salt_pepper_att',
    'shelter_att',
    'bright_att',
]