"""
異常定義模組

定義盲水印系統中使用的自訂異常類別
"""


class WatermarkError(Exception):
    """水印處理基礎異常"""
    pass


class ImageReadError(WatermarkError):
    """圖片讀取失敗"""
    def __init__(self, filename: str):
        super().__init__(f"無法讀取圖片檔案: {filename}")
        self.filename = filename


class WatermarkReadError(WatermarkError):
    """水印讀取失敗"""
    def __init__(self, filename: str):
        super().__init__(f"無法讀取水印檔案: {filename}")
        self.filename = filename


class InvalidModeError(WatermarkError):
    """無效的水印模式"""
    def __init__(self, mode: str, valid_modes: tuple):
        super().__init__(f"無效的模式 '{mode}'，有效模式為: {valid_modes}")
        self.mode = mode
        self.valid_modes = valid_modes


class WatermarkCapacityError(WatermarkError):
    """水印容量溢出"""
    def __init__(self, required_bits: int, available_bits: int):
        super().__init__(
            f"水印容量不足: 需要 {required_bits / 1000:.1f}kb，"
            f"但僅可嵌入 {available_bits / 1000:.1f}kb"
        )
        self.required_bits = required_bits
        self.available_bits = available_bits


class WatermarkShapeError(WatermarkError):
    """水印形狀參數錯誤"""
    def __init__(self, message: str):
        super().__init__(f"水印形狀錯誤: {message}")


class ImageShapeError(WatermarkError):
    """圖片尺寸錯誤"""
    def __init__(self, message: str):
        super().__init__(f"圖片尺寸錯誤: {message}")


class AttackParameterError(WatermarkError):
    """攻擊參數錯誤"""
    def __init__(self, message: str):
        super().__init__(f"攻擊參數錯誤: {message}")

