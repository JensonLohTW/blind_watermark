"""測試重構後的程式碼"""
import pytest
import numpy as np


def test_imports():
    """測試所有模組可以正常導入"""
    from app.core.blind_watermark import WaterMark, WaterMarkCore
    from app.core.blind_watermark import (
        crop_attack, resize_attack, rotation_attack,
        salt_pepper_attack, shelter_attack, brightness_attack
    )
    from app.core.blind_watermark import estimate_crop_parameters, recover_crop
    from app.core.blind_watermark.types import WatermarkConfig, AttackResult
    from app.core.blind_watermark.constants import (
        DEFAULT_ROBUSTNESS_PRIMARY,
        DEFAULT_ROBUSTNESS_SECONDARY
    )
    from app.core.blind_watermark.exceptions import (
        WatermarkError,
        ImageReadError,
        WatermarkCapacityError
    )
    
    assert WaterMark is not None
    assert WaterMarkCore is not None


def test_watermark_config():
    """測試 WatermarkConfig 資料類別"""
    from app.core.blind_watermark.types import WatermarkConfig
    
    config = WatermarkConfig(
        password_wm=123,
        password_img=456,
        robustness_primary=40,
        robustness_secondary=25
    )
    
    assert config.password_wm == 123
    assert config.password_img == 456
    assert config.robustness_primary == 40
    assert config.robustness_secondary == 25


def test_attack_result():
    """測試 AttackResult 資料類別"""
    from app.core.blind_watermark.types import AttackResult
    
    img = np.zeros((100, 100, 3), dtype=np.uint8)
    result = AttackResult(
        output_img=img,
        attack_type="crop",
        parameters={"x1": 10, "y1": 10, "x2": 90, "y2": 90}
    )
    
    assert result.attack_type == "crop"
    assert result.parameters["x1"] == 10


def test_constants():
    """測試常數定義"""
    from app.core.blind_watermark.constants import (
        PIXEL_MAX_VALUE,
        PIXEL_MIN_VALUE,
        IMAGE_BINARIZATION_THRESHOLD,
        DEFAULT_ROBUSTNESS_PRIMARY,
        DEFAULT_ROBUSTNESS_SECONDARY,
        YUV_CHANNELS
    )
    
    assert PIXEL_MAX_VALUE == 255
    assert PIXEL_MIN_VALUE == 0
    assert IMAGE_BINARIZATION_THRESHOLD == 128
    assert DEFAULT_ROBUSTNESS_PRIMARY == 36
    assert DEFAULT_ROBUSTNESS_SECONDARY == 20
    assert YUV_CHANNELS == 3


def test_exceptions():
    """測試異常類別"""
    from app.core.blind_watermark.exceptions import (
        WatermarkError,
        ImageReadError,
        WatermarkCapacityError
    )
    
    # 測試基礎異常
    with pytest.raises(WatermarkError):
        raise WatermarkError("測試錯誤")
    
    # 測試圖片讀取異常
    with pytest.raises(ImageReadError):
        raise ImageReadError("test.jpg")
    
    # 測試容量異常
    with pytest.raises(WatermarkCapacityError):
        raise WatermarkCapacityError(required_bits=1000, available_bits=500)


def test_converters():
    """測試格式轉換器"""
    from app.core.blind_watermark.core.converters import (
        string_to_bits,
        bits_to_string,
        bits_to_boolean
    )
    
    # 測試字串轉位元
    text = "Hello"
    bits = string_to_bits(text)
    assert isinstance(bits, np.ndarray)
    assert bits.dtype == bool
    
    # 測試浮點數轉布林
    float_bits = np.array([0.1, 0.6, 0.3, 0.8])
    bool_bits = bits_to_boolean(float_bits)
    assert bool_bits.tolist() == [False, True, False, True]


def test_image_processor():
    """測試圖片處理器"""
    from app.core.blind_watermark.core.image_processor import ImageProcessor
    from app.core.blind_watermark.types import BlockShape
    
    processor = ImageProcessor(BlockShape())
    
    # 創建測試圖片
    img = np.random.randint(0, 256, (100, 100, 3), dtype=np.uint8)
    
    # 處理圖片
    processor.process_image(img)
    
    # 驗證處理結果
    assert processor.img_shape == (100, 100)
    assert processor.ca_shape is not None
    assert len(processor.ca) == 3  # YUV 3 個通道


def test_block_shape():
    """測試 BlockShape 資料類別"""
    from app.core.blind_watermark.types import BlockShape
    
    block = BlockShape()
    assert block.height == 4
    assert block.width == 4
    assert block.size() == 16
    assert block.to_array().tolist() == [4, 4]


def test_file_size_limits():
    """測試所有檔案都在 200 行以內"""
    import os
    import subprocess
    
    result = subprocess.run(
        ["find", "app/core/blind_watermark", "-type", "f", "-name", "*.py", "-exec", "wc", "-l", "{}", ";"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    
    lines = result.stdout.strip().split('\n')
    oversized = []
    for line in lines:
        parts = line.strip().split()
        if len(parts) == 2:
            count, path = int(parts[0]), parts[1]
            if count > 200:
                oversized.append((count, path))
    
    assert len(oversized) == 0, f"以下檔案超過 200 行: {oversized}"


def test_directory_file_limits():
    """測試所有目錄檔案數都在 8 個以內"""
    import os
    import subprocess
    
    result = subprocess.run(
        ["find", "app/core/blind_watermark", "-type", "d"],
        capture_output=True,
        text=True,
        cwd=os.path.dirname(os.path.dirname(__file__))
    )
    
    dirs = result.stdout.strip().split('\n')
    overcrowded = []
    for dir_path in dirs:
        result = subprocess.run(
            ["find", dir_path, "-maxdepth", "1", "-type", "f", "-name", "*.py"],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(os.path.dirname(__file__))
        )
        file_count = len([f for f in result.stdout.strip().split('\n') if f])
        if file_count > 8:
            overcrowded.append((file_count, dir_path))
    
    assert len(overcrowded) == 0, f"以下目錄檔案數超過 8: {overcrowded}"

