# 盲浮水印系統

基於 DWT-DCT-SVD 演算法的圖片盲浮水印嵌入與提取系統，採用前後端分離架構。

## 專案簡介

本專案提供完整的圖片浮水印解決方案，支援三種浮水印模式：

- **文字模式（str）**：將文字資訊嵌入圖片中
- **圖片模式（img）**：將圖片作為浮水印嵌入另一張圖片
- **位元模式（bit）**：嵌入自訂位元陣列

浮水印具有高度魯棒性，能抵抗多種攻擊：旋轉、裁剪、縮放、亮度調整、椒鹽雜訊等。

## 架構說明

### 前後端分離架構

```
blind_watermark/
├── backend/              # 後端 API 服務
│   ├── app/
│   │   ├── api/         # API 路由
│   │   ├── core/        # 核心浮水印邏輯
│   │   ├── models/      # 資料模型
│   │   ├── services/    # 服務層
│   │   └── main.py      # FastAPI 應用程式入口
│   ├── pyproject.toml   # Python 專案設定
│   └── run.py           # 啟動腳本
│
├── frontend/            # 前端 Web 介面
│   ├── app/            # Next.js App Router
│   ├── components/     # React 元件
│   ├── lib/            # 工具函式與服務
│   └── package.json    # Node.js 專案設定
│
├── scripts/            # 管理腳本
│   ├── start.sh       # 啟動服務
│   ├── stop.sh        # 停止服務
│   ├── build.sh       # 建置專案
│   ├── check.sh       # 程式碼檢查
│   └── test.sh        # 執行測試
│
├── logs/              # 執行日誌
└── examples/          # 範例程式碼
```

## 技術棧

### 後端
- **FastAPI** 0.115+：現代化高效能 Web 框架
- **Uvicorn**：ASGI 伺服器
- **Pydantic** 2.9+：資料驗證與設定管理
- **OpenCV**：圖片處理
- **NumPy**：數值運算
- **PyWavelets**：小波轉換

### 前端
- **Next.js** 16.0：React 框架（超過 15.4 要求）
- **React** 19.2：使用者介面函式庫
- **TypeScript** 5+：型別安全
- **Tailwind CSS** 4：樣式框架
- **shadcn/ui**：UI 元件庫

## 安裝與執行

### 前置需求

- **Python** 3.10+
- **Node.js** 20+
- **uv**：Python 套件管理工具
- **npm**：Node.js 套件管理工具

### 快速開始

#### 1. 一鍵啟動（推薦）

```bash
# 啟動前後端服務
./scripts/start.sh
```

服務啟動後：
- 前端介面：http://localhost:3000
- 後端 API：http://localhost:8000
- API 文件：http://localhost:8000/docs

#### 2. 停止服務

```bash
./scripts/stop.sh
```

### 手動安裝與執行

#### 後端

```bash
cd backend

# 建立虛擬環境
uv venv

# 安裝依賴
uv pip install -e .

# 啟動服務
uv run python run.py
```

#### 前端

```bash
cd frontend

# 安裝依賴
npm install

# 啟動開發伺服器
npm run dev
```

## 使用方式

### Web 介面

1. 開啟瀏覽器訪問 http://localhost:3000
2. 選擇「嵌入浮水印」或「提取浮水印」分頁
3. 上傳圖片並設定參數
4. 下載處理後的結果

### API 呼叫

#### 嵌入浮水印

```bash
curl -X POST "http://localhost:8000/api/watermark/embed" \
  -F "image=@original.jpg" \
  -F "mode=str" \
  -F "watermark_text=Hello World" \
  -F "password_img=1" \
  -F "password_wm=1"
```

#### 提取浮水印

```bash
curl -X POST "http://localhost:8000/api/watermark/extract" \
  -F "image=@watermarked.png" \
  -F "mode=str" \
  -F "watermark_length=888" \
  -F "password_img=1" \
  -F "password_wm=1"
```

## API 文件

啟動後端服務後，可透過以下網址查看完整 API 文件：

- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

### 主要端點

#### POST `/api/watermark/embed`
嵌入浮水印

**參數**：
- `image`：原始圖片檔案
- `mode`：浮水印模式（str/img/bit）
- `password_img`：圖片密碼（預設 1）
- `password_wm`：浮水印密碼（預設 1）
- `watermark_text`：文字浮水印（mode=str 時必填）
- `watermark_image`：圖片浮水印（mode=img 時必填）
- `watermark_length`：位元長度（mode=bit 時必填）

**回應**：
```json
{
  "success": true,
  "message": "浮水印嵌入成功",
  "watermark_length": 888,
  "image_data": "base64_encoded_image..."
}
```

#### POST `/api/watermark/extract`
提取浮水印

**參數**：
- `image`：含浮水印的圖片檔案
- `mode`：浮水印模式（str/img/bit）
- `password_img`：圖片密碼（需與嵌入時相同）
- `password_wm`：浮水印密碼（需與嵌入時相同）
- `watermark_length`：浮水印位元長度（需與嵌入時相同）

**回應**：
```json
{
  "success": true,
  "message": "浮水印提取成功",
  "watermark_text": "Hello World"
}
```

## 開發

### 建置專案

```bash
./scripts/build.sh
```

### 程式碼檢查

```bash
./scripts/check.sh
```

執行內容：
- 後端：Ruff lint 檢查
- 前端：TypeScript 型別檢查、ESLint

### 執行測試

```bash
./scripts/test.sh
```

## 重要注意事項

1. **浮水印長度**：提取時必須提供與嵌入時相同的 `watermark_length`，建議在嵌入後記錄此值
2. **密碼一致性**：`password_img` 和 `password_wm` 必須與嵌入時完全相同
3. **圖片格式**：支援常見圖片格式（PNG、JPEG、BMP 等）
4. **魯棒性參數**：核心演算法使用 `d1=36`、`d2=20`，可在 `backend/app/core/blind_watermark/bwm_core.py` 調整

## 核心演算法

本專案使用 **DWT-DCT-SVD** 頻域浮水印演算法：

1. **DWT（離散小波轉換）**：將圖片分解為低頻與高頻分量
2. **DCT（離散餘弦轉換）**：對 4×4 區塊進行頻域轉換
3. **SVD（奇異值分解）**：修改奇異值嵌入浮水印位元
4. **YUV 色彩空間**：在 YUV 三通道分別嵌入，提升魯棒性

## 授權

MIT License

## 貢獻

歡迎提交 Issue 或 Pull Request。

## 聯絡方式

如有問題或建議，請透過 GitHub Issues 聯繫。

