# Blind Watermark Backend API

盲浮水印後端 API 服務，使用 FastAPI 框架封裝核心浮水印功能。

## 技術棧

- **FastAPI**: 現代化高效能 Web 框架
- **Uvicorn**: ASGI 伺服器
- **Pydantic**: 資料驗證與設定管理
- **OpenCV**: 圖片處理
- **NumPy**: 數值運算
- **PyWavelets**: 小波轉換

## 專案結構

```
backend/
├── app/
│   ├── api/              # API 路由
│   │   └── watermark.py  # 浮水印端點
│   ├── core/             # 核心浮水印邏輯
│   │   └── blind_watermark/
│   ├── models/           # 資料模型
│   │   └── schemas.py    # Pydantic 模型
│   ├── services/         # 服務層
│   │   └── watermark_service.py
│   └── main.py           # 應用程式入口
├── tests/                # 測試檔案
├── pyproject.toml        # 專案設定與依賴
└── run.py                # 啟動腳本
```

## 安裝

使用 uv 安裝依賴：

```bash
cd backend
uv pip install -e .
```

## 執行

### 開發模式

```bash
python run.py
```

或使用 uvicorn：

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 生產模式

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API 文件

啟動服務後，可透過以下網址查看自動生成的 API 文件：

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API 端點

### 1. 嵌入浮水印

**POST** `/api/watermark/embed`

**參數**：
- `image`: 原始圖片檔案（必填）
- `mode`: 浮水印模式 - `str`/`img`/`bit`（必填）
- `password_img`: 圖片密碼（預設 1）
- `password_wm`: 浮水印密碼（預設 1）
- `watermark_text`: 文字浮水印內容（mode=str 時必填）
- `watermark_image`: 圖片浮水印檔案（mode=img 時必填）
- `watermark_length`: 位元浮水印長度（mode=bit 時必填）

**回應**：
```json
{
  "success": true,
  "message": "浮水印嵌入成功",
  "watermark_length": 888,
  "image_data": "base64_encoded_image..."
}
```

### 2. 提取浮水印

**POST** `/api/watermark/extract`

**參數**：
- `image`: 含浮水印的圖片檔案（必填）
- `mode`: 浮水印模式 - `str`/`img`/`bit`（必填）
- `password_img`: 圖片密碼（需與嵌入時相同）
- `password_wm`: 浮水印密碼（需與嵌入時相同）
- `watermark_length`: 浮水印位元長度（需與嵌入時相同）

**回應**（文字模式）：
```json
{
  "success": true,
  "message": "浮水印提取成功",
  "watermark_text": "extracted text"
}
```

**回應**（圖片模式）：
```json
{
  "success": true,
  "message": "浮水印提取成功",
  "watermark_data": "base64_encoded_image..."
}
```

### 3. 健康檢查

**GET** `/health`

**回應**：
```json
{
  "status": "healthy"
}
```

## 開發

### 型別檢查

```bash
uv run ruff check .
```

### 執行測試

```bash
uv run pytest
```

## 注意事項

1. **浮水印長度**：提取時必須提供與嵌入時相同的 `watermark_length`
2. **密碼一致性**：`password_img` 和 `password_wm` 必須與嵌入時完全相同
3. **圖片格式**：支援常見圖片格式（PNG、JPEG 等）
4. **CORS 設定**：預設允許 `http://localhost:3000` 跨域請求

