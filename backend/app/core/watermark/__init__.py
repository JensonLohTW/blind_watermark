"""新版浮水印核心 API。"""

from .config import WatermarkConfig, WatermarkKeys
from . import att
from .facade import WaterMark
from .pool import AutoPool
from .recover import estimate_crop_parameters, recover_crop
from .robustness import attacks, recovery
from .runner import WatermarkPipeline

__all__ = [
    "WatermarkConfig",
    "WatermarkKeys",
    "WatermarkPipeline",
    "WaterMark",
    "AutoPool",
    "attacks",
    "recovery",
    "estimate_crop_parameters",
    "recover_crop",
    "att",
]
