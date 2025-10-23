# 專案架構文件

## 概述

本專案採用前後端分離架構，將原有的 Python 函式庫封裝為 RESTful API，並提供現代化的 Web 介面。

## 技術棧

### 後端
- **FastAPI** 0.119+：高效能 Web 框架
- **Uvicorn** 0.38+：ASGI 伺服器
- **Pydantic** 2.12+：資料驗證
- **OpenCV** 4.11+：圖片處理
- **NumPy** 2.3+：數值運算
- **PyWavelets** 1.9+：小波轉換

### 前端
- **Next.js** 16.0：React 框架
- **React** 19.2：UI 函式庫
- **TypeScript** 5+：型別系統
- **Tailwind CSS** 4：樣式框架
- **shadcn/ui**：UI 元件庫

## 目錄結構

```
blind_watermark/
├── backend/                    # 後端 API 服務
│   ├── app/
│   │   ├── api/               # API 路由層
│   │   │   ├── __init__.py
│   │   │   └── watermark.py   # 浮水印端點
│   │   ├── core/              # 核心邏輯（原 blind_watermark）
│   │   │   └── blind_watermark/
│   │   ├── models/            # 資料模型層
│   │   │   ├── __init__.py
│   │   │   └── schemas.py     # Pydantic 模型
│   │   ├── services/          # 服務層
│   │   │   ├── __init__.py
│   │   │   └── watermark_service.py
│   │   ├── __init__.py
│   │   └── main.py            # FastAPI 應用程式入口
│   ├── tests/                 # 測試檔案
│   ├── pyproject.toml         # Python 專案設定
│   ├── run.py                 # 啟動腳本
│   └── README.md              # 後端文件
│
├── frontend/                   # 前端 Web 介面
│   ├── app/                   # Next.js App Router
│   │   ├── globals.css        # 全域樣式
│   │   ├── layout.tsx         # 根佈局
│   │   └── page.tsx           # 首頁
│   ├── components/            # React 元件
│   │   ├── ui/                # shadcn/ui 元件
│   │   ├── embed-form.tsx     # 嵌入表單
│   │   └── extract-form.tsx   # 提取表單
│   ├── lib/                   # 工具函式
│   │   ├── types/             # TypeScript 型別定義
│   │   │   └── watermark.ts
│   │   ├── services/          # API 服務層
│   │   │   └── watermark-api.ts
│   │   └── utils.ts           # 工具函式
│   ├── package.json           # Node.js 專案設定
│   ├── tsconfig.json          # TypeScript 設定
│   └── .env.local             # 環境變數
│
├── scripts/                    # 管理腳本
│   ├── start.sh               # 啟動前後端
│   ├── stop.sh                # 停止服務
│   ├── build.sh               # 建置專案
│   ├── check.sh               # 程式碼檢查
│   ├── test.sh                # 執行測試
│   └── verify.sh              # 驗證專案結構
│
├── logs/                       # 執行日誌
│   ├── backend.log
│   ├── frontend.log
│   ├── backend.pid
│   └── frontend.pid
│
├── examples/                   # 原有範例程式碼
├── docs/                       # 文件
└── README.md                   # 專案說明
```

## 資料流

### 嵌入浮水印流程

```
使用者上傳圖片
    ↓
前端 (EmbedForm)
    ↓
API 請求 (POST /api/watermark/embed)
    ↓
後端路由 (watermark.py)
    ↓
服務層 (WatermarkService.embed_watermark)
    ↓
核心邏輯 (WaterMark.embed)
    ↓
DWT-DCT-SVD 演算法處理
    ↓
回傳 Base64 編碼圖片
    ↓
前端顯示與下載
```

### 提取浮水印流程

```
使用者上傳含浮水印圖片
    ↓
前端 (ExtractForm)
    ↓
API 請求 (POST /api/watermark/extract)
    ↓
後端路由 (watermark.py)
    ↓
服務層 (WatermarkService.extract_watermark)
    ↓
核心邏輯 (WaterMark.extract)
    ↓
DWT-DCT-SVD 演算法處理
    ↓
回傳提取結果（文字或圖片）
    ↓
前端顯示結果
```

## 層級職責

### 後端

#### API 層 (`app/api/`)
- 處理 HTTP 請求與回應
- 驗證請求參數
- 錯誤處理與狀態碼管理
- 檔案上傳處理

#### 服務層 (`app/services/`)
- 業務邏輯封裝
- 檔案格式轉換（bytes ↔ Base64）
- 臨時檔案管理
- 呼叫核心邏輯

#### 模型層 (`app/models/`)
- 定義請求與回應的資料結構
- Pydantic 模型驗證
- 型別定義

#### 核心層 (`app/core/`)
- 原有的浮水印演算法實作
- DWT-DCT-SVD 處理
- 不直接暴露給 API

### 前端

#### 頁面層 (`app/`)
- Next.js 路由與頁面
- 整體佈局與樣式

#### 元件層 (`components/`)
- 可重用的 React 元件
- UI 互動邏輯
- 表單處理

#### 服務層 (`lib/services/`)
- API 呼叫封裝
- 錯誤處理
- 資料轉換

#### 型別層 (`lib/types/`)
- TypeScript 介面定義
- 與後端 API 對應的型別

## API 設計

### 端點列表

| 方法 | 路徑 | 說明 |
|------|------|------|
| GET | `/` | 根路徑健康檢查 |
| GET | `/health` | 健康檢查 |
| POST | `/api/watermark/embed` | 嵌入浮水印 |
| POST | `/api/watermark/extract` | 提取浮水印 |
| GET | `/api/watermark/health` | 浮水印服務健康檢查 |

### 資料模型

#### EmbedRequest
```typescript
{
  mode: "str" | "img" | "bit",
  password_img: number,
  password_wm: number,
  watermark_text?: string,
  watermark_length?: number
}
```

#### EmbedResponse
```typescript
{
  success: boolean,
  message: string,
  watermark_length?: number,
  image_data?: string  // Base64
}
```

#### ExtractRequest
```typescript
{
  mode: "str" | "img" | "bit",
  password_img: number,
  password_wm: number,
  watermark_length: number
}
```

#### ExtractResponse
```typescript
{
  success: boolean,
  message: string,
  watermark_text?: string,
  watermark_data?: string  // Base64
}
```

## 部署考量

### 開發環境
- 後端：`uvicorn` 開發模式（自動重載）
- 前端：`next dev` 開發伺服器

### 生產環境
- 後端：`uvicorn` 多 worker 模式
- 前端：`next build` + `next start` 或靜態匯出
- 反向代理：Nginx
- 容器化：Docker + Docker Compose

## 擴展性

### 後端擴展
- 新增端點：在 `app/api/` 建立新路由檔案
- 新增服務：在 `app/services/` 建立新服務類別
- 新增模型：在 `app/models/schemas.py` 定義

### 前端擴展
- 新增頁面：在 `app/` 建立新路由資料夾
- 新增元件：在 `components/` 建立新元件檔案
- 新增 API：在 `lib/services/` 擴展 API 類別

## 安全性

### 後端
- CORS 設定限制來源
- 檔案大小限制
- 臨時檔案自動清理
- 輸入驗證（Pydantic）

### 前端
- 環境變數管理
- API URL 設定
- 檔案類型驗證
- 錯誤訊息處理

## 效能優化

### 後端
- 非同步處理（FastAPI async）
- 臨時檔案管理
- 可選的多進程處理（AutoPool）

### 前端
- Next.js 自動程式碼分割
- 圖片延遲載入
- API 請求快取
- 元件懶載入

