"""
API 請求與回應的資料模型
"""
from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field


class WatermarkMode(str, Enum):
    """浮水印模式"""
    TEXT = "str"
    IMAGE = "img"
    BITS = "bit"


class EmbedRequest(BaseModel):
    """嵌入浮水印請求"""
    mode: WatermarkMode = Field(..., description="浮水印模式：str/img/bit")
    password_img: int = Field(1, description="圖片密碼")
    password_wm: int = Field(1, description="浮水印密碼")
    watermark_text: Optional[str] = Field(None, description="文字浮水印內容（mode=str 時必填）")
    watermark_length: Optional[int] = Field(None, description="浮水印位元長度（mode=bit 時必填）")


class EmbedResponse(BaseModel):
    """嵌入浮水印回應"""
    success: bool
    message: str
    watermark_length: Optional[int] = Field(None, description="實際嵌入的浮水印位元長度")
    image_data: Optional[str] = Field(None, description="Base64 編碼的嵌入後圖片")


class ExtractRequest(BaseModel):
    """提取浮水印請求"""
    mode: WatermarkMode = Field(..., description="浮水印模式：str/img/bit")
    password_img: int = Field(1, description="圖片密碼")
    password_wm: int = Field(1, description="浮水印密碼")
    watermark_length: int = Field(..., description="浮水印位元長度")


class ExtractResponse(BaseModel):
    """提取浮水印回應"""
    success: bool
    message: str
    watermark_text: Optional[str] = Field(None, description="提取的文字浮水印")
    watermark_data: Optional[str] = Field(None, description="Base64 編碼的提取圖片浮水印")


class ErrorResponse(BaseModel):
    """錯誤回應"""
    success: bool = False
    error: str
    detail: Optional[str] = None

