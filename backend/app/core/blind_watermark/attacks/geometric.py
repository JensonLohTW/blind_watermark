"""
幾何攻擊模組

包含裁剪、縮放、旋轉等幾何變換攻擊
"""
from typing import Optional, Tuple
import cv2
import numpy.typing as npt

from ..types import CropParameters, AttackResult
from ..utils import load_image, save_image


def crop_attack(
    input_filename: Optional[str] = None,
    input_img: Optional[npt.NDArray] = None,
    output_file_name: Optional[str] = None,
    loc_r: Optional[Tuple[Tuple[float, float], Tuple[float, float]]] = None,
    loc: Optional[Tuple[int, int, int, int]] = None,
    scale: float = 1.0
) -> AttackResult:
    """
    裁剪攻擊（可選縮放）
    
    Args:
        input_filename: 輸入圖片路徑
        input_img: 輸入圖片陣列
        output_file_name: 輸出檔案路徑
        loc_r: 相對位置 ((x1_ratio, y1_ratio), (x2_ratio, y2_ratio))
        loc: 絕對位置 (x1, y1, x2, y2)
        scale: 縮放比例
        
    Returns:
        AttackResult 包含攻擊後的圖片和參數
    """
    img = load_image(filename=input_filename, img=input_img)
    
    # 計算裁剪位置
    if loc is None:
        if loc_r is None:
            raise ValueError("必須提供 loc 或 loc_r 參數")
        h, w = img.shape[:2]
        x1 = int(w * loc_r[0][0])
        y1 = int(h * loc_r[0][1])
        x2 = int(w * loc_r[1][0])
        y2 = int(h * loc_r[1][1])
    else:
        x1, y1, x2, y2 = loc
    
    # 裁剪
    output_img = img[y1:y2, x1:x2].copy()
    
    # 縮放（如果需要）
    if scale != 1.0:
        h, w = output_img.shape[:2]
        output_img = cv2.resize(
            output_img,
            dsize=(round(w * scale), round(h * scale))
        )
    
    # 保存
    if output_file_name:
        save_image(output_file_name, output_img)
    
    crop_params = CropParameters(x1=x1, y1=y1, x2=x2, y2=y2)
    return AttackResult(image=output_img, parameters=crop_params, scale=scale)


def resize_attack(
    input_filename: Optional[str] = None,
    input_img: Optional[npt.NDArray] = None,
    output_file_name: Optional[str] = None,
    out_shape: Tuple[int, int] = (500, 500)
) -> AttackResult:
    """
    縮放攻擊
    
    Args:
        input_filename: 輸入圖片路徑
        input_img: 輸入圖片陣列
        output_file_name: 輸出檔案路徑
        out_shape: 輸出尺寸 (width, height)
        
    Returns:
        AttackResult 包含攻擊後的圖片
    """
    img = load_image(filename=input_filename, img=input_img)
    output_img = cv2.resize(img, dsize=out_shape)
    
    if output_file_name:
        save_image(output_file_name, output_img)
    
    return AttackResult(image=output_img)


def rotation_attack(
    input_filename: Optional[str] = None,
    input_img: Optional[npt.NDArray] = None,
    output_file_name: Optional[str] = None,
    angle: float = 45.0
) -> AttackResult:
    """
    旋轉攻擊
    
    Args:
        input_filename: 輸入圖片路徑
        input_img: 輸入圖片陣列
        output_file_name: 輸出檔案路徑
        angle: 旋轉角度（度）
        
    Returns:
        AttackResult 包含攻擊後的圖片
    """
    img = load_image(filename=input_filename, img=input_img)
    rows, cols = img.shape[:2]
    
    # 計算旋轉矩陣
    rotation_matrix = cv2.getRotationMatrix2D(
        center=(cols / 2, rows / 2),
        angle=angle,
        scale=1.0
    )
    
    # 執行旋轉
    output_img = cv2.warpAffine(img, rotation_matrix, (cols, rows))
    
    if output_file_name:
        save_image(output_file_name, output_img)
    
    return AttackResult(image=output_img)


# 向後相容的別名
cut_att3 = crop_attack
cut_att2 = crop_attack
resize_att = resize_attack
rot_att = rotation_attack

