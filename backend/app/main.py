"""
Blind Watermark Backend API 主程式入口
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api import watermark

app = FastAPI(
    title="Blind Watermark API",
    description="圖片盲浮水印嵌入與提取 API",
    version="0.1.0",
)

# CORS 設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 註冊路由
app.include_router(watermark.router, prefix="/api/watermark", tags=["watermark"])


@app.get("/")
async def root():
    """根路徑健康檢查"""
    return {"status": "ok", "message": "Blind Watermark API is running"}


@app.get("/health")
async def health():
    """健康檢查端點"""
    return {"status": "healthy"}

