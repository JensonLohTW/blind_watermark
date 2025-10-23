# Codebase Structure

## 專案根目錄結構（已整理）
```
blind_watermark/
├── README.md                 # 主要說明文件
├── START_HERE.md            # 快速開始指南
├── LICENSE                  # 授權條款
├── AGENTS.md               # AI Agent 指引
├── CLAUDE.md               # Claude Code 指引
├── backend/                # 後端應用程式
│   ├── app/
│   │   ├── main.py        # FastAPI 主程式
│   │   ├── api/           # API 路由
│   │   ├── core/          # 核心功能
│   │   │   └── blind_watermark/  # 浮水印核心程式碼
│   │   ├── models/        # 資料模型
│   │   └── services/      # 業務邏輯
│   ├── .venv/             # Python 虛擬環境（重要：在 backend/ 下）
│   ├── pyproject.toml     # 後端專案設定
│   └── run.py             # 後端啟動腳本
├── frontend/              # 前端應用程式
│   ├── app/               # Next.js 15.4 應用程式
│   ├── components/        # React 19 元件
│   ├── lib/               # 工具函式
│   ├── node_modules/      # Node.js 依賴
│   ├── .next/             # Next.js 建置輸出
│   └── package.json       # 前端專案設定
├── scripts/               # 統一執行腳本
│   ├── start.sh           # 啟動服務
│   ├── stop.sh            # 停止服務
│   ├── build.sh           # 建置專案
│   ├── check.sh           # 程式碼檢查
│   ├── test.sh            # 執行測試
│   └── verify.sh          # 驗證專案結構
├── docs/                  # 文件目錄
│   ├── ARCHITECTURE.md    # 架構說明
│   ├── PROJECT_SUMMARY.md # 專案摘要
│   └── QUICKSTART.md      # 快速開始
├── examples/              # 範例與測試
│   ├── example_str.py     # 字串浮水印範例
│   ├── example_img.py     # 圖片浮水印範例
│   ├── example_bit.py     # 位元陣列浮水印範例
│   ├── pic/               # 測試圖片
│   └── output/            # 輸出目錄
├── logs/                  # 日誌目錄
└── archive/               # 歸檔目錄
    ├── original_code/     # 原始 blind_watermark/ 程式碼
    │   └── blind_watermark/
    ├── old_docs/          # 舊文件
    │   ├── README.md
    │   └── README_cn.md
    └── old_config/        # 舊設定檔
        ├── setup.py
        ├── pyproject.toml
        ├── requirements.txt
        ├── uv.lock
        └── .gitignore
```

## 核心元件位置

### 浮水印核心程式碼（backend/app/core/blind_watermark/）
- **blind_watermark.py**: 高階 WaterMark API
- **bwm_core.py**: 低階 WaterMarkCore 演算法
- **pool.py**: AutoPool 並行處理抽象層
- **att.py**: 攻擊模擬函式
- **recover.py**: 攻擊恢復函式
- **cli_tools.py**: CLI 進入點
- **version.py**: 版本資訊
- **__init__.py**: 套件初始化

### WaterMark (blind_watermark.py)
- **用途**: 高階使用者 API
- **職責**:
  - 處理三種浮水印模式：'img'、'str'、'bit'
  - 基於密碼的加密/解密
  - 工作流程編排
- **關鍵方法**: `read_img()`, `read_wm()`, `embed()`, `extract()`

### WaterMarkCore (bwm_core.py)
- **用途**: 低階浮水印演算法實作
- **職責**:
  - DWT-DCT-SVD 頻域操作
  - YUV 色彩空間上的 4x4 區塊處理
  - 多處理支援
- **關鍵參數**: `d1=36`（主要強度）、`d2=20`（次要強度）
- **方法**: `embed()`, `extract()`, `extract_with_kmeans()`

### AutoPool (pool.py)
- **用途**: 並行處理抽象層
- **模式**: 'common'（序列）、'multithreading'、'multiprocessing'、'vectorization'、'cached'
- **平台處理**: Windows 上自動降級為多執行緒

### Attack & Recovery (att.py, recover.py)
- **att.py**: 模擬攻擊（裁切、縮放、旋轉、亮度、雜訊、遮蔽）
- **recover.py**: 範本比對用於攻擊參數估計與圖片恢復
- **關鍵函式**: `estimate_crop_parameters()`, `recover_crop()`

## 重要注意事項

### 虛擬環境位置
- **正確位置**: `backend/.venv/`
- **錯誤位置**: 根目錄的 `.venv/`（已移除）
- 所有 Python 相關操作應在 backend/ 目錄下進行

### 歸檔目錄
- 原始的 `blind_watermark/` 套件程式碼已移至 `archive/original_code/`
- 舊的設定檔（setup.py、pyproject.toml 等）已移至 `archive/old_config/`
- 舊的文件已移至 `archive/old_docs/`

### 執行腳本
- 所有啟動、建置、檢查操作必須透過 `scripts/*.sh` 執行
- 禁止直接呼叫 `npm`、`pnpm`、`uv`、`python` 等指令
