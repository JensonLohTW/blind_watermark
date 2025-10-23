# Code Style and Conventions

## 專案規範（必須遵守）

### 語言與溝通
- **文件語言**: 繁體中文
- **程式碼註解**: 繁體中文優先
- **禁止**: emoji 的使用

### 檔案尺寸限制
- **動態語言**（Python/JS/TS）: 單檔 ≤ 200 行
- **靜態語言**（Java/Go/Rust）: 單檔 ≤ 250 行
- **目錄檔案數**: 每層 ≤ 8 個檔案

### 程式碼品質原則
- **可讀性第一**: 程式碼被讀取的次數遠高於被撰寫
- **零容忍壞味道**: 僵化、冗餘、循環依賴、脆弱、晦澀、資料泥團、不必要複雜性
- **Linus 方法論**: 
  - 好品味（Good Taste）：消除特殊情況
  - Never break userspace：向後相容
  - 實用主義：解決真實問題
  - 簡潔執念：超過 3 層縮排即是設計異味

### 技術棧要求
- **Next.js**: v15.4（嚴格）
- **React**: v19（嚴格）
- **Tailwind CSS**: v4（嚴格）
- **禁止**: CommonJS
- **預設**: TypeScript
- **Python**: 強型別資料結構，避免未結構化 dict

## Python 程式碼風格（blind_watermark 核心）

### 命名慣例
- **函式/方法**: snake_case（例如：`read_img`, `block_add_wm`）
- **類別**: PascalCase（例如：`WaterMark`, `WaterMarkCore`, `AutoPool`）
- **變數**: snake_case（例如：`wm_bit`, `password_img`, `block_shape`）
- **私有方法**: 使用前導底線（例如：`_method_name`）

### 程式碼特性
- **型別提示**: 舊程式碼未使用，新程式碼應使用
- **文件字串**: 應補充完整的 docstrings
- **註解**: 使用繁體中文，提供功能性說明
- **行長度**: 遵循 PEP8，建議 ≤ 88 字元
- **縮排**: 4 個空格（標準 Python）

### 程式碼組織
- **類別結構**:
  - `__init__` 中初始化實例變數
  - 公開 API 方法在前
  - 輔助/內部方法在後
- **模組結構**:
  - 匯入在最上方
  - 輔助函式（例如：`one_dim_kmeans`, `random_strategy1`）
  - 主要類別定義

### 匯入風格
```python
import numpy as np
import cv2
import pywt
from .module import Class
```

### 參數模式
- 廣泛使用預設值（例如：`password_wm=1`, `password_img=1`）
- 形狀參數使用元組：`block_shape=(4, 4)`
- 字串模式參數：`mode='common'`，浮水印模式在 `{'img', 'str', 'bit'}`

### 錯誤處理
- 應使用明確的錯誤處理
- 不僅依賴 NumPy/OpenCV 例外
- 使用斷言進行維度檢查（例如：偶數圖片維度）

## TypeScript/React 程式碼風格（前端）

### 命名慣例
- **元件**: PascalCase（例如：`WatermarkUpload`, `ImagePreview`）
- **函式**: camelCase（例如：`handleUpload`, `processImage`）
- **常數**: UPPER_SNAKE_CASE（例如：`MAX_FILE_SIZE`）
- **介面/型別**: PascalCase，以 `I` 或 `T` 開頭（例如：`IWatermarkConfig`, `TImageData`）

### 程式碼組織
- **元件結構**:
  - 匯入
  - 型別定義
  - 元件定義
  - 輔助函式
  - 匯出
- **檔案組織**:
  - 一個元件一個檔案
  - 相關元件放在同一目錄
  - 共用型別放在 `types/` 或 `lib/`

### TypeScript 要求
- **禁止 `any`**: 除非徵得同意
- **使用介面**: 定義資料結構
- **型別安全**: 所有函式參數和回傳值都應有型別

### React 最佳實務
- **使用 Hooks**: 優先使用函式元件
- **狀態管理**: 使用 `useState`, `useReducer`
- **副作用**: 使用 `useEffect`
- **效能優化**: 使用 `useMemo`, `useCallback`

## Git 提交規範

### 提交頻率
- **頻繁提交**: 大型任務切分為里程碑
- **每一里程碑完成並確認後立即提交**
- 避免大規模一次性提交

### 提交訊息
- 使用繁體中文
- 清晰描述變更內容
- 格式：`[類型] 簡短描述`
  - 類型：新增、修改、修正、重構、文件、測試等

## 檔案與目錄組織

### 文件位置
- **正式文件**: `docs/`
- **討論/審查/方案**: `discuss/`（如需要）
- **歸檔**: `archive/`

### 程式碼位置
- **後端核心**: `backend/app/core/`
- **後端 API**: `backend/app/api/`
- **前端元件**: `frontend/components/`
- **前端頁面**: `frontend/app/`

### 執行腳本
- **統一腳本**: `scripts/*.sh`
- **禁止直接呼叫**: `npm`, `pnpm`, `uv`, `python` 等
