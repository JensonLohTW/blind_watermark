"""
裁剪恢復模組

將被裁剪的圖片恢復到原始尺寸
"""
from typing import Optional, Tuple
import numpy as np
import numpy.typing as npt

from ..types import CropParameters, ImageShape
from ..utils import load_image, save_image


def recover_crop(
    template_file: Optional[str] = None,
    tem_img: Optional[npt.NDArray] = None,
    output_file_name: Optional[str] = None,
    loc: Optional[Tuple[int, int, int, int]] = None,
    crop_params: Optional[CropParameters] = None,
    image_o_shape: Optional[Tuple[int, int]] = None,
    original_shape: Optional[ImageShape] = None
) -> npt.NDArray:
    """
    恢復被裁剪的圖片
    
    將裁剪後的圖片放回原始位置，其餘部分填充為 0
    
    Args:
        template_file: 裁剪後的圖片路徑
        tem_img: 裁剪後的圖片陣列
        output_file_name: 輸出檔案路徑
        loc: 裁剪位置 (x1, y1, x2, y2)
        crop_params: 裁剪參數物件
        image_o_shape: 原始圖片尺寸 (height, width)
        original_shape: 原始圖片形狀物件
        
    Returns:
        恢復後的圖片陣列
    """
    # 載入圖片
    tem_img = load_image(filename=template_file, img=tem_img)
    
    # 解析裁剪參數
    if crop_params is not None:
        x1, y1, x2, y2 = crop_params.to_tuple()
    elif loc is not None:
        x1, y1, x2, y2 = loc
    else:
        raise ValueError("必須提供 crop_params 或 loc 參數")
    
    # 解析原始尺寸
    if original_shape is not None:
        height, width = original_shape.to_tuple()
    elif image_o_shape is not None:
        height, width = image_o_shape
    else:
        raise ValueError("必須提供 original_shape 或 image_o_shape 參數")
    
    # 創建空白圖片
    if len(tem_img.shape) == 3:
        img_recovered = np.zeros((height, width, tem_img.shape[2]))
    else:
        img_recovered = np.zeros((height, width))
    
    # 將裁剪的圖片縮放並放回原位置
    import cv2
    resized = cv2.resize(tem_img, dsize=(x2 - x1, y2 - y1))
    img_recovered[y1:y2, x1:x2] = resized
    
    # 保存
    if output_file_name:
        save_image(output_file_name, img_recovered)
    
    return img_recovered

