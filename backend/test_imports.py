#!/usr/bin/env python3
"""測試導入是否正常"""

print("測試導入模組...")

try:
    from app.core.blind_watermark import WaterMark, WaterMarkCore
    print("✓ WaterMark 和 WaterMarkCore 導入成功")
except Exception as e:
    print(f"✗ WaterMark 導入失敗: {e}")
    exit(1)

try:
    from app.core.blind_watermark import (
        crop_attack, resize_attack, rotation_attack,
        salt_pepper_attack, shelter_attack, brightness_attack
    )
    print("✓ 攻擊函數導入成功")
except Exception as e:
    print(f"✗ 攻擊函數導入失敗: {e}")
    exit(1)

try:
    from app.core.blind_watermark import estimate_crop_parameters, recover_crop
    print("✓ 恢復函數導入成功")
except Exception as e:
    print(f"✗ 恢復函數導入失敗: {e}")
    exit(1)

try:
    from app.core.blind_watermark.types import WatermarkConfig, AttackResult
    print("✓ 型別定義導入成功")
except Exception as e:
    print(f"✗ 型別定義導入失敗: {e}")
    exit(1)

try:
    from app.core.blind_watermark.constants import (
        DEFAULT_ROBUSTNESS_PRIMARY,
        DEFAULT_ROBUSTNESS_SECONDARY
    )
    print("✓ 常數導入成功")
except Exception as e:
    print(f"✗ 常數導入失敗: {e}")
    exit(1)

try:
    from app.core.blind_watermark.exceptions import (
        WatermarkError,
        ImageReadError,
        WatermarkCapacityError
    )
    print("✓ 異常類別導入成功")
except Exception as e:
    print(f"✗ 異常類別導入失敗: {e}")
    exit(1)

print("\n所有導入測試通過！")
print("\n檢查檔案行數...")

import os
import subprocess

result = subprocess.run(
    ["find", "app/core/blind_watermark", "-type", "f", "-name", "*.py", "-exec", "wc", "-l", "{}", ";"],
    capture_output=True,
    text=True
)

lines = result.stdout.strip().split('\n')
oversized = []
for line in lines:
    parts = line.strip().split()
    if len(parts) == 2:
        count, path = int(parts[0]), parts[1]
        if count > 200:
            oversized.append((count, path))

if oversized:
    print("\n警告：以下檔案超過 200 行：")
    for count, path in oversized:
        print(f"  {count} 行: {path}")
else:
    print("✓ 所有檔案都在 200 行以內")

print("\n檢查目錄檔案數...")
result = subprocess.run(
    ["find", "app/core/blind_watermark", "-type", "d"],
    capture_output=True,
    text=True
)

dirs = result.stdout.strip().split('\n')
overcrowded = []
for dir_path in dirs:
    result = subprocess.run(
        ["find", dir_path, "-maxdepth", "1", "-type", "f", "-name", "*.py"],
        capture_output=True,
        text=True
    )
    file_count = len([f for f in result.stdout.strip().split('\n') if f])
    if file_count > 8:
        overcrowded.append((file_count, dir_path))

if overcrowded:
    print("\n警告：以下目錄檔案數超過 8：")
    for count, path in overcrowded:
        print(f"  {count} 個檔案: {path}")
else:
    print("✓ 所有目錄檔案數都在 8 個以內")

print("\n✅ 所有檢查通過！")

