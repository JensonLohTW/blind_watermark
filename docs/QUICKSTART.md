# 快速開始指南

本指南將協助您在 5 分鐘內啟動並執行盲浮水印系統。

## 前置需求

確保您的系統已安裝以下工具：

- **Python** 3.10 或更高版本
- **Node.js** 20 或更高版本
- **uv**（Python 套件管理工具）
- **npm**（Node.js 套件管理工具）

### 安裝 uv（如果尚未安裝）

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# 或使用 pip
pip install uv
```

## 一鍵啟動

### 步驟 1：驗證專案結構

```bash
./scripts/verify.sh
```

您應該看到所有檢查項目都顯示 ✓。

### 步驟 2：啟動服務

```bash
./scripts/start.sh
```

此腳本會自動：
1. 建立 Python 虛擬環境
2. 安裝後端依賴
3. 啟動後端 API 服務（埠號 8000）
4. 安裝前端依賴（如需要）
5. 啟動前端開發伺服器（埠號 3000）

### 步驟 3：開啟瀏覽器

服務啟動後，開啟瀏覽器訪問：

- **前端介面**：http://localhost:3000
- **後端 API 文件**：http://localhost:8000/docs

### 步驟 4：使用系統

#### 嵌入浮水印

1. 點選「嵌入浮水印」分頁
2. 選擇浮水印模式（文字/圖片/位元）
3. 上傳原始圖片
4. 輸入浮水印內容（文字模式）或上傳浮水印圖片（圖片模式）
5. 設定密碼（可選，預設為 1）
6. 點選「嵌入浮水印」
7. 等待處理完成
8. 記錄顯示的「浮水印位元長度」（提取時需要）
9. 下載嵌入浮水印後的圖片

#### 提取浮水印

1. 點選「提取浮水印」分頁
2. 選擇浮水印模式（需與嵌入時相同）
3. 上傳含浮水印的圖片
4. 輸入浮水印位元長度（嵌入時記錄的數值）
5. 輸入密碼（需與嵌入時相同）
6. 點選「提取浮水印」
7. 查看提取結果

### 步驟 5：停止服務

```bash
./scripts/stop.sh
```

## 手動啟動（進階）

如果您想分別啟動前後端：

### 啟動後端

```bash
cd backend
uv venv
uv pip install -e .
uv run python run.py
```

後端將在 http://localhost:8000 啟動。

### 啟動前端

開啟新終端機：

```bash
cd frontend
npm install
npm run dev
```

前端將在 http://localhost:3000 啟動。

## 常見問題

### Q1: 啟動腳本顯示「權限被拒絕」

**解決方法**：
```bash
chmod +x scripts/*.sh
```

### Q2: 後端啟動失敗，顯示「模組未找到」

**解決方法**：
```bash
cd backend
uv pip install -e .
```

### Q3: 前端啟動失敗，顯示「找不到模組」

**解決方法**：
```bash
cd frontend
npm install
```

### Q4: 埠號 8000 或 3000 已被佔用

**解決方法**：

修改埠號：

**後端**：編輯 `backend/run.py`，修改 `port=8000` 為其他埠號

**前端**：執行時指定埠號
```bash
PORT=3001 npm run dev
```

並更新 `frontend/.env.local` 中的 `NEXT_PUBLIC_API_URL`。

### Q5: 提取浮水印失敗

**可能原因**：
1. 浮水印位元長度不正確（必須與嵌入時相同）
2. 密碼不正確（必須與嵌入時相同）
3. 圖片經過了不支援的處理（如重新壓縮）

**解決方法**：
- 確認使用嵌入時記錄的浮水印位元長度
- 確認密碼與嵌入時相同
- 使用原始嵌入後的圖片，避免二次處理

## 進階使用

### 使用 API 直接呼叫

#### 嵌入浮水印（文字模式）

```bash
curl -X POST "http://localhost:8000/api/watermark/embed" \
  -F "image=@/path/to/image.jpg" \
  -F "mode=str" \
  -F "watermark_text=Hello World" \
  -F "password_img=1234" \
  -F "password_wm=5678"
```

#### 提取浮水印

```bash
curl -X POST "http://localhost:8000/api/watermark/extract" \
  -F "image=@/path/to/watermarked.png" \
  -F "mode=str" \
  -F "watermark_length=888" \
  -F "password_img=1234" \
  -F "password_wm=5678"
```

### 查看 API 文件

訪問 http://localhost:8000/docs 可查看完整的 Swagger UI 文件，包含：
- 所有端點說明
- 請求參數詳情
- 回應格式範例
- 互動式 API 測試

## 開發工作流程

### 建置專案

```bash
./scripts/build.sh
```

### 程式碼檢查

```bash
./scripts/check.sh
```

執行：
- 後端 Ruff lint
- 前端 TypeScript 型別檢查
- 前端 ESLint

### 執行測試

```bash
./scripts/test.sh
```

## 下一步

- 閱讀 [README.md](../README_NEW.md) 了解完整功能
- 查看 [ARCHITECTURE.md](./ARCHITECTURE.md) 了解系統架構
- 探索 `examples/` 目錄中的範例程式碼
- 查看後端 API 文件：http://localhost:8000/docs

## 需要協助？

如遇到問題，請：
1. 檢查日誌檔案：`logs/backend.log` 和 `logs/frontend.log`
2. 執行驗證腳本：`./scripts/verify.sh`
3. 查看 GitHub Issues
4. 參考完整文件

祝您使用愉快！

