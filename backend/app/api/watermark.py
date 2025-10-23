"""
浮水印 API 路由
"""
from typing import Optional

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from app.models import (
    EmbedResponse,
    ErrorResponse,
    ExtractResponse,
    WatermarkMode,
)
from app.services import WatermarkService

router = APIRouter()
watermark_service = WatermarkService()


@router.post("/embed", response_model=EmbedResponse)
async def embed_watermark(
    image: UploadFile = File(..., description="原始圖片檔案"),
    mode: WatermarkMode = Form(..., description="浮水印模式"),
    password_img: int = Form(1, description="圖片密碼"),
    password_wm: int = Form(1, description="浮水印密碼"),
    watermark_text: Optional[str] = Form(None, description="文字浮水印內容"),
    watermark_image: Optional[UploadFile] = File(None, description="圖片浮水印檔案"),
    watermark_length: Optional[int] = Form(None, description="位元浮水印長度"),
):
    """
    嵌入浮水印端點
    
    - **mode**: str（文字）、img（圖片）、bit（位元陣列）
    - **password_img**: 圖片層級密碼
    - **password_wm**: 浮水印層級密碼
    - **watermark_text**: mode=str 時必填
    - **watermark_image**: mode=img 時必填
    - **watermark_length**: mode=bit 時必填
    """
    try:
        # 讀取原始圖片
        image_bytes = await image.read()

        # 讀取浮水印圖片（如果有）
        watermark_image_bytes = None
        if watermark_image:
            watermark_image_bytes = await watermark_image.read()

        # 呼叫服務層嵌入浮水印
        output_bytes, wm_length = watermark_service.embed_watermark(
            image_bytes=image_bytes,
            mode=mode.value,
            password_img=password_img,
            password_wm=password_wm,
            watermark_text=watermark_text,
            watermark_image_bytes=watermark_image_bytes,
            watermark_length=watermark_length,
        )

        # 轉換為 Base64
        image_base64 = watermark_service.bytes_to_base64(output_bytes)

        return EmbedResponse(
            success=True,
            message="浮水印嵌入成功",
            watermark_length=wm_length,
            image_data=image_base64,
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"嵌入浮水印時發生錯誤: {str(e)}")


@router.post("/extract", response_model=ExtractResponse)
async def extract_watermark(
    image: UploadFile = File(..., description="含浮水印的圖片檔案"),
    mode: WatermarkMode = Form(..., description="浮水印模式"),
    password_img: int = Form(1, description="圖片密碼"),
    password_wm: int = Form(1, description="浮水印密碼"),
    watermark_length: int = Form(..., description="浮水印位元長度"),
):
    """
    提取浮水印端點
    
    - **mode**: str（文字）、img（圖片）、bit（位元陣列）
    - **password_img**: 圖片層級密碼（需與嵌入時相同）
    - **password_wm**: 浮水印層級密碼（需與嵌入時相同）
    - **watermark_length**: 浮水印位元長度（需與嵌入時相同）
    """
    try:
        # 讀取圖片
        image_bytes = await image.read()

        # 呼叫服務層提取浮水印
        text_result, image_result = watermark_service.extract_watermark(
            image_bytes=image_bytes,
            mode=mode.value,
            password_img=password_img,
            password_wm=password_wm,
            watermark_length=watermark_length,
        )

        # 準備回應
        response_data = {
            "success": True,
            "message": "浮水印提取成功",
        }

        if text_result:
            response_data["watermark_text"] = text_result
        if image_result:
            response_data["watermark_data"] = watermark_service.bytes_to_base64(image_result)

        return ExtractResponse(**response_data)

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"提取浮水印時發生錯誤: {str(e)}")


@router.get("/health")
async def health_check():
    """浮水印服務健康檢查"""
    return {"status": "healthy", "service": "watermark"}

