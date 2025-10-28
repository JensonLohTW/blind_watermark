from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal, Optional, Tuple


RuntimeMode = Literal["common", "multithreading", "multiprocessing", "vectorization", "cached"]


@dataclass(frozen=True)
class WatermarkKeys:
    """儲存浮水印與影像混淆所需的密碼設定。"""

    image: int = 1
    watermark: int = 1


@dataclass(frozen=True)
class BlockConfig:
    """記錄 DWT 之後的區塊切割設定。"""

    size: Tuple[int, int] = (4, 4)

    def validate(self) -> None:
        if len(self.size) != 2 or min(self.size) <= 0:
            raise ValueError("block size must be a tuple of two positive integers")


@dataclass(frozen=True)
class AlgorithmTuning:
    """演算法調整參數，控制嵌入強度與品質。"""

    d1: float = 36.0
    d2: float = 20.0
    block: BlockConfig = field(default_factory=BlockConfig)

    def validate(self) -> None:
        if self.d1 <= 0:
            raise ValueError("d1 must be positive")
        if self.d2 < 0:
            raise ValueError("d2 must be non-negative")
        self.block.validate()


@dataclass(frozen=True)
class RuntimeConfig:
    """平行化與資源使用設定。"""

    mode: RuntimeMode = "common"
    processes: Optional[int] = None


@dataclass(frozen=True)
class WatermarkConfig:
    """整合所有與浮水印流程相關的設定。"""

    keys: WatermarkKeys = field(default_factory=WatermarkKeys)
    tuning: AlgorithmTuning = field(default_factory=AlgorithmTuning)
    runtime: RuntimeConfig = field(default_factory=RuntimeConfig)

    def validate(self) -> None:
        self.tuning.validate()

