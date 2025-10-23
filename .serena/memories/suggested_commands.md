# Suggested Commands for Development

## 重要原則
**所有啟動、建置、檢查操作必須透過 `scripts/*.sh` 執行**
**禁止直接呼叫 `npm`、`pnpm`、`uv`、`python` 等指令**

## 統一執行腳本（必須使用）

### 啟動服務
```bash
./scripts/start.sh
# 同時啟動後端（FastAPI）和前端（Next.js）服務
```

### 停止服務
```bash
./scripts/stop.sh
# 停止所有運行中的服務
```

### 建置專案
```bash
./scripts/build.sh
# 建置後端和前端專案
```

### 程式碼檢查
```bash
./scripts/check.sh
# 執行型別檢查、Lint、靜態分析
```

### 執行測試
```bash
./scripts/test.sh
# 執行單元測試、整合測試
```

### 驗證專案結構
```bash
./scripts/verify.sh
# 驗證專案目錄結構、關鍵檔案、虛擬環境等
```

## 後端開發（在 backend/ 目錄下）

### 虛擬環境管理
```bash
cd backend

# 啟用虛擬環境（如需手動操作）
source .venv/bin/activate

# 使用 uv 安裝依賴
uv pip install -r requirements.txt

# 離開虛擬環境
deactivate
```

### 直接執行後端（僅限開發除錯）
```bash
cd backend
python run.py
# 或
uvicorn app.main:app --reload
```

## 前端開發（在 frontend/ 目錄下）

### 依賴管理
```bash
cd frontend

# 安裝依賴
npm install
# 或
pnpm install
```

### 直接執行前端（僅限開發除錯）
```bash
cd frontend
npm run dev
# 或
pnpm dev
```

## 範例與測試（原始演算法測試）

### 執行個別範例（從 examples/ 目錄）
```bash
cd examples

# 測試字串浮水印嵌入/提取
python example_str.py

# 測試圖片浮水印嵌入/提取
python example_img.py

# 測試位元陣列浮水印
python example_bit.py

# 測試不寫入檔案
python example_no_writing.py
```

### 測試覆蓋率（Travis CI 方式）
```bash
cd examples
coverage run -p example_no_writing.py
coverage run -p example_bit.py
coverage run -p example_str.py
coverage run -p example_img.py
cd ..
coverage combine
```

## CLI 使用（原始套件 CLI）

### 嵌入浮水印
```bash
blind_watermark --embed --pwd 1234 examples/pic/ori_img.jpeg "watermark text" examples/output/embedded.png
```

### 提取浮水印
```bash
blind_watermark --extract --pwd 1234 --wm_shape 111 examples/output/embedded.png
```

## Git 操作

### 標準 Git 指令
```bash
# 檢查狀態
git status

# 新增檔案
git add .

# 提交變更（頻繁提交原則）
git commit -m "描述變更內容"

# 推送至遠端
git push
```

## 專案結構檢查

### 檢查根目錄整潔度
```bash
ls -1
# 應該只看到：AGENTS.md, CLAUDE.md, LICENSE, README.md, START_HERE.md,
# archive/, backend/, docs/, examples/, frontend/, logs/, scripts/
```

### 檢查虛擬環境位置
```bash
# 確認 backend/.venv/ 存在
ls -la backend/ | grep .venv

# 確認根目錄沒有 .venv/
ls -la | grep .venv
```

### 檢查歸檔目錄
```bash
# 查看歸檔結構
tree archive/ -L 2
# 或
find archive -type d
```

## 系統特定資訊
- **平台**: Darwin (macOS)
- **Shell**: bash
- **Python 版本**: 3.13+
- **Node.js**: 支援 Next.js 15.4
- **標準 Unix 指令可用**: ls, cd, grep, find, cat, tree 等
