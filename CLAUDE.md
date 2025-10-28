# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

blind_watermark is a Python library for embedding and extracting invisible watermarks in images using DWT-DCT-SVD (Discrete Wavelet Transform, Discrete Cosine Transform, Singular Value Decomposition) algorithms. The library supports robust watermarking that survives various image attacks including rotation, cropping, scaling, brightness adjustments, and more.

**本專案已重構為前後端分離架構**，提供 Web 介面與 RESTful API，同時保留核心演算法函式庫功能。

## Project Architecture

### 目錄結構

```
blind_watermark/
├── backend/                    # 後端 API 服務
│   ├── app/
│   │   ├── api/               # API 路由層
│   │   ├── core/              # 核心演算法（原 blind_watermark）
│   │   │   └── blind_watermark/
│   │   ├── models/            # 資料模型（Pydantic）
│   │   ├── services/          # 服務層
│   │   └── main.py            # FastAPI 應用程式
│   ├── tests/                 # 測試
│   ├── pyproject.toml         # Python 專案設定（uv）
│   └── run.py                 # 啟動腳本
├── frontend/                   # 前端 Web 介面
│   ├── app/                   # Next.js App Router
│   ├── components/            # React 元件
│   ├── lib/                   # 工具函式與服務
│   └── package.json
├── scripts/                    # 統一管理腳本
│   ├── start.sh               # 啟動前後端
│   ├── stop.sh                # 停止服務
│   ├── build.sh               # 建置
│   ├── check.sh               # 程式碼檢查
│   ├── test.sh                # 執行測試
│   └── verify.sh              # 驗證專案結構
├── logs/                       # 執行日誌
├── examples/                   # 原有範例程式碼
├── docs/                       # 文件
└── README.md
```

### 技術棧

#### 後端
- **FastAPI** 0.119+：現代化高效能 Web 框架
- **Uvicorn** 0.38+：ASGI 伺服器
- **Pydantic** 2.12+：資料驗證與型別安全
- **Python** 3.10+
- **uv**：現代化 Python 套件管理器
- **OpenCV** 4.11+：圖片處理
- **NumPy** 2.3+：數值運算
- **PyWavelets** 1.9+：小波轉換

#### 前端
- **Next.js** 16.0：React 框架（App Router）
- **React** 19.2：UI 函式庫
- **TypeScript** 5+：型別系統
- **Tailwind CSS** 4：樣式框架
- **shadcn/ui**：UI 元件庫

## Development Commands

### 環境驗證
```bash
# 驗證專案結構與依賴
./scripts/verify.sh
```

### 啟動服務
```bash
# 一鍵啟動前後端服務
./scripts/start.sh

# 服務將在以下位址運行：
# - 前端介面：http://localhost:3000
# - 後端 API：http://localhost:8000
# - API 文件：http://localhost:8000/docs
# - 健康檢查：http://localhost:8000/health
```

### 停止服務
```bash
./scripts/stop.sh
```

### 建置專案
```bash
# 建置前後端（安裝依賴）
./scripts/build.sh
```

### 程式碼檢查
```bash
# 執行 Ruff (後端) + TypeScript + ESLint (前端)
./scripts/check.sh
```

### 執行測試
```bash
# 執行後端 pytest + 核心功能測試
./scripts/test.sh
```

### 手動安裝（開發用途）

#### 後端
```bash
cd backend

# 使用 uv 建立虛擬環境
uv venv

# 安裝依賴（從 pyproject.toml）
uv pip install -e .

# 安裝開發依賴
uv pip install -e ".[dev]"

# 手動啟動
python run.py
# 或
uv run uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

#### 前端
```bash
cd frontend

# 安裝依賴
npm install

# 開發模式
npm run dev

# 建置生產版本
npm run build
npm start
```

## Web API

### API 端點

#### 1. 嵌入浮水印
**POST** `/api/watermark/embed`

**參數**（multipart/form-data）：
- `image`: 原始圖片檔案（必填）
- `mode`: 浮水印模式 - `str` | `img` | `bit`（必填）
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
  "watermark_shape": [64, 64],
  "image_data": "base64_encoded_image..."
}
```

#### 2. 提取浮水印
**POST** `/api/watermark/extract`

**參數**（multipart/form-data）：
- `image`: 含浮水印的圖片檔案（必填）
- `mode`: 浮水印模式 - `str` | `img` | `bit`（必填）
- `password_img`: 圖片密碼（必須與嵌入時相同）
- `password_wm`: 浮水印密碼（必須與嵌入時相同）
- `watermark_length`: 浮水印位元長度（必須與嵌入時相同）
- `watermark_shape`: 浮水印圖片的長寬（圖片模式必填，格式為 JSON 陣列，例如 `[64, 64]`）

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

#### 3. 健康檢查
**GET** `/health`

**回應**：
```json
{
  "status": "healthy"
}
```

### API 文件

啟動服務後，可透過以下網址查看完整的互動式 API 文件：
- **Swagger UI**：http://localhost:8000/docs
- **ReDoc**：http://localhost:8000/redoc

### CLI 工具（次要功能）

核心函式庫仍可作為 CLI 工具使用（需安裝套件），但主要使用方式為 Web 介面：

```bash
# 使用腳本（推薦）
./scripts/watermark_cli.sh --embed --pwd 1234 examples/pic/ori_img.jpeg "watermark text" examples/output/embedded.png
./scripts/watermark_cli.sh --extract --pwd 1234 --wm_shape 64 64 examples/output/embedded.png

# 直接呼叫模組
python -m app.core.watermark.cli.entrypoint --embed --pwd 1234 examples/pic/ori_img.jpeg "watermark text" examples/output/embedded.png
python -m app.core.watermark.cli.entrypoint --extract --pwd 1234 --wm_shape 64 64 examples/output/embedded.png
```

## Core Algorithm Architecture

### 核心元件（位於 backend/app/core/watermark/）

**WaterMark (facade.py)**：新版高階介面
- 維持 `read_img()`、`read_wm()`、`embed()`、`extract()` 等常見操作
- 內部轉委至 `WatermarkPipeline`，提供與舊版類似的使用體驗
- 透過 `wm_bit`、`wm_size` 保存已載入浮水印的位元資訊

**WatermarkPipeline (runner/__init__.py)**：嵌入／提取流程核心
- 管理 `WatermarkEmbedder` 與 `WatermarkExtractor`
- 根據 `WatermarkConfig` 統一設定密碼、區塊大小、執行模式與演算法參數
- 直接對應服務層與 CLI 的主要呼叫點

**WatermarkAlgorithm (operations/algorithm.py)**：低階演算法實作
- 負責 DWT-DCT-SVD 頻域處理與 4×4 區塊運算
- 支援三通道處理與位元平均機制，維持演算法魯棒性
- `one_dim_kmeans`、`_average_payload` 等方法內聚於此

**AutoPool (runtime/pool.py)**：並行執行策略
- 封裝 `multithreading`、`multiprocessing` 與一般模式
- Windows 平台自動降級為多執行緒，避免相容性問題

**Attack & Recovery (att.py, recover.py)**：
- `att.py`：保留 `cut_att3`、`salt_pepper_att` 等相容函式，底層改用 `robustness.attacks`
- `recover.py`：提供 `estimate_crop_parameters`、`recover_crop` 等恢復工具
- 可對抗裁剪、縮放、亮度、遮擋等攻擊並還原圖片尺寸

### Data Flow

**Embedding**: Image (BGR) → YUV conversion → DWT on each channel → 4×4 block partition → DCT → SVD → modify singular values → inverse operations → watermarked image

**Extraction**: Watermarked image → same transformation pipeline → extract bits from singular values → average across blocks and channels → decrypt with password → output watermark

**Key Implementation Details**:
- Images are padded to even dimensions before processing
- Transparent images (4-channel) are supported - alpha channel is preserved separately
- Watermark bits are shuffled using `np.random.RandomState(password)` for encryption
- Block indices are shuffled with a different password for image-level security
- Extraction uses k-means clustering on extracted values to determine bit threshold

### Password System

Two passwords provide dual-layer security:
- `password_wm`: Shuffles watermark bits themselves (encryption at watermark level)
- `password_img`: Shuffles block embedding order (encryption at image level via `random_strategy1`)

### Watermark Capacity

The number of embeddable bits is constrained by:
```
block_num = (ca_shape[0] // 4) * (ca_shape[1] // 4)
```
where `ca_shape` is approximately half the original image dimensions after DWT. The watermark is embedded cyclically if `wm_size < block_num`.

## Important Notes

- **wm_shape requirement**: When extracting, you MUST know the watermark shape/length used during embedding. For string watermarks, the Web API returns `watermark_length` after embedding - save this value.
- **Password consistency**: Both `password_img` and `password_wm` must match between embedding and extraction.
- **Attack recovery**: For crop/scale attacks where parameters are unknown, use `estimate_crop_parameters()` followed by `recover_crop()` before extraction (available in core library).
- **YUV color space**: All processing happens in YUV to separate luminance from chrominance - watermark survives better this way.
- **Robustness vs quality tradeoff**: Modify `self.d1` and `self.d2` in WaterMarkCore to adjust this tradeoff.

## Backend Architecture Layers

### API 層 (backend/app/api/)
- 處理 HTTP 請求與回應
- 驗證請求參數（透過 Pydantic）
- 錯誤處理與狀態碼管理
- 檔案上傳處理

### 服務層 (backend/app/services/)
- 業務邏輯封裝
- 檔案格式轉換（bytes ↔ Base64）
- 臨時檔案管理
- 呼叫核心邏輯

### 模型層 (backend/app/models/)
- Pydantic 模型定義
- 請求與回應的資料結構
- 型別驗證

### 核心層 (backend/app/core/)
- 原有的浮水印演算法實作
- DWT-DCT-SVD 處理
- 不直接暴露給 API，透過服務層呼叫

## Testing

### 執行測試
```bash
# 使用管理腳本（推薦）
./scripts/test.sh

# 腳本內部執行：
# 1. 後端 pytest 測試（若存在）
# 2. 核心功能測試（examples/example_no_writing.py）
```

### 手動測試
```bash
# 後端測試
cd backend
uv run pytest tests/ -v

# 核心功能測試
cd backend
uv run python ../examples/example_no_writing.py
```

### 原有測試檔案（位於 examples/）
```bash
cd examples
python example_str.py      # 測試文字浮水印
python example_img.py      # 測試圖片浮水印
python example_bit.py      # 測試位元陣列浮水印
python example_no_writing.py  # 測試（不寫入檔案）
```

注意：.travis.yml 設定已過時（引用不存在的 setup.py），實際測試請使用 `./scripts/test.sh`。

## Related Code Patterns

When implementing attack recovery workflows in core library, follow this pattern from example_str.py:
```python
# 1. Apply attack
att.cut_att3(input_filename='embedded.png', output_file_name='attacked.png', ...)

# 2. Estimate attack parameters (if unknown)
(x1, y1, x2, y2), shape, score, scale = estimate_crop_parameters(
    original_file='embedded.png', template_file='attacked.png', ...)

# 3. Recover to original dimensions
recover_crop(template_file='attacked.png', output_file_name='recovered.png',
             loc=(x1, y1, x2, y2), image_o_shape=shape)

# 4. Extract watermark
wm_extract = bwm.extract('recovered.png', wm_shape=len_wm, mode='str')
```

## Deployment Considerations

### 開發環境
- 後端：uvicorn 開發模式（自動重載）
- 前端：next dev 開發伺服器
- 使用 `./scripts/start.sh` 一鍵啟動

### 生產環境
- 後端：uvicorn 多 worker 模式
- 前端：next build + next start 或靜態匯出
- 建議使用 Nginx 作為反向代理
- 可使用 Docker + Docker Compose 容器化部署

## Security & Best Practices

### 後端
- CORS 設定限制來源（預設允許 localhost:3000）
- 檔案大小限制
- 臨時檔案自動清理
- 輸入驗證（Pydantic）

### 前端
- 環境變數管理（.env.local）
- API URL 設定
- 檔案類型驗證
- 錯誤訊息處理

## Additional Documentation

詳細文件請參閱：
- **快速開始**：`START_HERE.md`
- **專案說明**：`README.md`
- **架構文件**：`docs/ARCHITECTURE.md`
- **快速指南**：`docs/QUICKSTART.md`
- **重構總結**：`docs/PROJECT_SUMMARY.md`
- **後端文件**：`backend/README.md`

---

# 專案執行與工程治理準則

> 目的：以高內聚、低耦合的方式統一**溝通規範、工程規範、流程治理、決策方法**與**工具鏈**；確保從需求到交付全鏈路可追溯、可稽核、可持續。

---

## 0. 使用方式

- 本文件為**唯一準則**。若各節衝突，優先順序為：**1) 原則層 → 2) 治理層 → 3) 流程 → 4) 工程細則 → 5) 工具**。
- 所有工作輸出必須以**繁體中文**撰寫；全程**禁止使用 emoji**。

---

## 1. 原則層（不可違反的底線）

1. **語言與溝通**

- 交流與文件一律使用繁體中文；嚴禁 emoji。
- **完整閱讀**相關檔案，避免因缺乏上下文導致重複實作或誤解架構。

2. **文件與目錄**

- `.md` 一律用中文撰寫；**正式文件**置於 `docs/`，**討論／審查／方案**置於 `discuss/`。
- 專案根目錄保持極簡；推薦結構見第 8 節。

3. **Run & Debug**

- 啟停、建置、檢查一律透過 `scripts/*.sh` 執行；**禁止直接**呼叫 `npm`、`pnpm`、`uv`、`python` 等指令。
- 腳本若失敗，**先修復腳本**再重試；執行日誌統一輸出 `logs/`。

4. **程式碼尺寸與結構**

- 動態語言（Python/JS/TS）**單檔 ≤ 200 行**；靜態語言（Java/Go/Rust）**單檔 ≤ 250 行**。
- 每層資料夾**檔案數 ≤ 8**；超過需拆分子目錄。
- 程式碼以**可讀性第一**為目標（被讀取次數遠高於被撰寫）。

5. **技術棧與模組化**

- Next.js **v15.4**、React **v19**、Tailwind CSS **v4**（嚴禁更低版本）。
- 嚴禁 **CommonJS**；預設使用 **TypeScript**。使用 `any`／非結構化 JSON 前須徵求同意。

6. **Python 規範**

- 資料結構採**強型別**；不得不使用未結構化 `dict` 前須徵求同意。
- 依賴與建置**一律使用 **``（由 `scripts/` 包裝呼叫）；虛擬環境目錄名統一 `.venv`。
- `main.py` 僅保留核心啟動邏輯。

7. **壞味道零容忍**

- 僵化、冗餘、循環依賴、脆弱、晦澀、資料泥團、不必要複雜性——**一經發現立即提出優化方案**。

8. **提交與變更管理**

- **頻繁提交**：大型任務切分為里程碑；每一里程碑完成並確認後立即提交。
- **除非明確指示，不做大規模重構**。

9. **實作與可運行性**

- **禁止虛擬實作**（除非明確要求）；交付須可運行、可驗證。

10. **UI/UX 基準**

- 設計需同時**美觀且易用**，遵循 a11y（ARIA、鍵盤操作、焦點管理）與最佳實務；重視互動與微互動。

11. **問題處理**

- 面對重複故障，追查**根因**而非僅嘗試不同方法或隨意改用他庫。

---

## 2. 角色與哲學（Linus 方法論）

> 以 **Linus Torvalds** 的思維框架審視品質與風險：

- **好品味（Good Taste）**：重寫問題以**消除特殊情況**。例如將 10 行含多個 `if` 的鏈結串列刪除，重構為 **4 行無條件分支**。
- **Never break userspace**：任何導致現有程式崩潰或行為變動的修改皆屬 **bug**；向後相容神聖不可侵犯。
- **實用主義**：解決真實問題，拒絕為理論完美犧牲工程可行性。
- **簡潔執念**：超過**3 層縮排**即是設計異味；函數短小、單一職責、命名克制。

**Linus 的三問（在任何實作前自檢）**

1. 這是**真問題**嗎？
2. 有**更簡單**的方法嗎？
3. 會**破壞**什麼嗎（相容性）？

---

## 3. 治理層（把規範「跑起來」）

1. **ADR / Waiver**

- 重大架構或技術決策以 **ADR** 存檔於 `docs/adr/`。
- 對「原則層」的例外需提交 **Waiver** 至 `discuss/waivers/`（含到期日與回復計畫）。

2. **DoR（Definition of Ready）**

- 必備：問題陳述、業務目標、範疇邊界、功能/非功能需求、驗收標準、風險與依賴、成功指標。
- **未達 DoR 不得進入開發**。

3. **DoD（Definition of Done）**

- 需通過：型別檢查、靜態掃描、單元/整合/關鍵流程測試、日誌與監控點、文件同步、尺寸/目錄上限校驗。
- CI 必須透過 `scripts/` 跑等價檢查。

4. **Code Review Rubric**

- 檢查：API 清晰、無循環依賴、命名語義、錯誤處理一致、日誌層級合理、文件同步、變更最小可回滾。
- **拒絕條件**：違反原則層／缺 DoR/DoD 證據／缺 ADR。

5. **分支與釋出**

- 建議 Trunk-Based：短生命週期 feature 分支；合併需綠燈 CI + 審核。
- 版本遵循 SemVer；釋出說明存 `docs/releases/`。

6. **CI/CD Gate（量化門檻）（可忽略）**

- 檔案行數：動態 ≤200、靜態 ≤250（Hard Fail）。
- 目錄檔案數：每層 ≤8（Hard Fail）。
- 覆蓋率：單元 ≥80%，關鍵模組 ≥90%。
- 型別檢查：零錯誤（Hard Fail）。
- 前端效能：LCP ≤2.5s、TTI ≤3.5s、CLS ≤0.1；後端 P95 延遲達標。
- 版本矩陣：Next 15.4 / React 19 / Tailwind 4；**禁止 CommonJS**（Hard Fail）。

---

## 4. 任務工作流（從需求到合併）

**0) 齊一思考框架**：套用「Linus 的三問」。

**1) 需求確認（模板）**

> 我理解的需求是：**[以工程語言重述、列出邊界與成功指標]**。請確認是否正確？

**2) 啟動前（Pre-Dev）**

- 完整閱讀相關檔案與現有架構。
- 任務過大或模糊：先**分解子任務**並與用戶對齊。
- 產出**變更計畫**（涉及檔案、資料流、邊界條件、回退策略）→ **獲得批准**。
- 準備 Schema/型別與監控點；落位於 `docs/`/`discuss/`。

**3) 開發中（In-Dev）**

- 依里程碑**頻繁提交**；每步可運行、可驗證。
- 引入或大改時**先跑語法與靜態檢查**。
- 使用外部函式庫前**查新**（見第 5 節）。
- 遇到重複問題：進行**根因分析**。

**4) 合併前（Pre-Merge / DoD）**

- CI 全綠：型別、Lint、測試、尺寸/目錄上限、效能與相容性檢查。
- 文件同步（`docs/`、`discuss/`、ADR/Release Notes）。
- Code Review 依 Rubric 通過；若有例外，附 Waiver。

---

## 5. 函式庫與知識更新

- 內部知識庫**可能過時**。使用外部函式庫前，**優先**透過 **Perplexity** 查詢最新**介面／語法／用法**；若不可用，再以一般網路搜尋替代。
- **不得**以「函式庫無法運作」為由跳過；多半是**語法或模式誤用**。若用戶指定某庫，**需在該庫內解決**。
- 重大變更後**必跑語法檢查與靜態分析**，避免破壞檔案或 API 調用方式。

---

## 6. 程式碼審查輸出模板（Linus 風格）

- **品味評分**：優／中／劣。
- **致命問題**：直指最糟糕之設計或邏輯。
- **改進方向（示例）**：\
  • 「把這個**特殊情況消除**掉。」\
  • 「這 **10 行**可以變成 **3 行**。」\
  • 「**資料結構**選錯了，應該是……」。

---

## 7. 工具鏈與文檔工作流

> 以下工具僅為**環境可用時**之建議使用，與本準則不衝突：

- **官方文檔查詢**：`resolve-library-id`、`get-library-docs`（Context7 MCP）。
- **MCP 原則**：當需程式碼生成、設定或查詢函式庫/API 文檔時，**優先**使用 Context7 以獲得最新權威資訊。

---

## 8. 推薦目錄與腳本

```
project-root/
  docs/
    adr/
    releases/
  discuss/
    waivers/
  scripts/
    check.sh      # 型別+lint+規格檢查（內部呼叫 uv/前端工具）
    test.sh       # 單元/整合/E2E
    build.sh      # 建置（由腳本統一封裝）
    start.sh      # 啟動服務（含必要參數）
    stop.sh       # 關閉/清理
  logs/
  src/
  .venv/
```

---

## 9. 稽核清單（可直接貼進 PR 描述）

**DoR（進開發前）**

-

**Pre-Dev**

-

**DoD（合併前）**

-

---

### 附錄 A：決策輸出（Linus 式）

**核心判斷**：值得做：**[原因]**／不值得做：**[原因]**\
**關鍵洞察**：資料結構／複雜度／破壞性風險\
**行動方案**（若值得做）：1) 先簡化資料結構 2) 消除特殊情況 3) 以最清晰方式實作 4) 確保零破壞（含遷移與回退）\
**若不值得**：「這是在解決不存在的問題，真正的問題是 **[XXX]**。」

### 附錄 B：UI/UX 交付要點

- 信息架構清晰、可預期的互動、合理的微互動與動線
- a11y：ARIA、對比度、鍵盤操作、焦點管理
- 前端效能指標達標（LCP/TTI/CLS）
