# 專案結構整理歷史

## 整理日期
2025-10-23

## 整理目的
完善專案結構，使其符合工程治理準則，包括：
- 整理根目錄，保持極簡
- 歸檔舊檔案和程式碼
- 修正虛擬環境位置
- 更新 .gitignore
- 建立清晰的歸檔目錄結構

## 執行的任務

### 任務 1：對比與完善後端核心程式碼
- 對比了原始位置 `blind_watermark/` 與後端位置 `backend/app/core/blind_watermark/`
- 確認所有 9 個核心檔案完整且內容一致
- 檔案清單：`__init__.py`, `att.py`, `blind_watermark.py`, `bwm_core.py`, `cli_tools.py`, `pool.py`, `recover.py`, `requirements.txt`, `version.py`
- 結論：後端核心程式碼無需補充，已是最新版本

### 任務 2：整理專案根目錄
**保留的檔案：**
- `README.md`（由 `README_NEW.md` 重新命名）
- `START_HERE.md`
- `LICENSE`
- `AGENTS.md`
- `CLAUDE.md`

**已歸檔的檔案：**
- 舊文件 → `archive/old_docs/`：
  - `README.md`（舊版）
  - `README_cn.md`
- 舊設定 → `archive/old_config/`：
  - `setup.py`
  - `pyproject.toml`
  - `requirements.txt`
  - `uv.lock`
  - `.gitignore`（舊版）
- 原始程式碼 → `archive/original_code/`：
  - 整個 `blind_watermark/` 目錄

**重新命名的檔案：**
- `README_NEW.md` → `README.md`
- `.gitignore_new` → `.gitignore`

### 任務 3：修正虛擬環境位置
- **已刪除**: 根目錄的 `.venv/`
- **已確認**: `backend/.venv/` 存在且正常運作
- **原因**: 根據專案規範，虛擬環境應位於 `backend/.venv/` 而非根目錄

### 任務 4：更新 .gitignore
新增或確認的規則：
- `backend/.venv/`（明確指定後端虛擬環境）
- `frontend/node_modules/`（明確指定前端依賴）
- `frontend/.next/`（明確指定前端建置輸出）
- `*.tsbuildinfo`（TypeScript 建置資訊）
- `logs/`（日誌目錄）
- `archive/`（歸檔目錄，可選）
- 所有 `__pycache__/`、`*.pyc`、`.next/` 等標準忽略項目

### 任務 5：建立歸檔目錄結構
```
archive/
├── original_code/          # 原始 blind_watermark/ 程式碼
│   └── blind_watermark/
│       ├── __init__.py
│       ├── att.py
│       ├── blind_watermark.py
│       ├── bwm_core.py
│       ├── cli_tools.py
│       ├── pool.py
│       ├── recover.py
│       ├── requirements.txt
│       └── version.py
├── old_docs/              # 舊文件
│   ├── README.md
│   └── README_cn.md
└── old_config/            # 舊設定檔
    ├── .gitignore
    ├── setup.py
    ├── pyproject.toml
    ├── requirements.txt
    └── uv.lock
```

### 任務 6：驗證完成
- 執行 `./scripts/verify.sh` 全部通過
- 根目錄整潔，只保留 12 個必要項目
- 所有舊檔案已妥善歸檔
- 專案結構完全符合規範

## 整理後的根目錄結構
```
blind_watermark/
├── AGENTS.md              # AI Agent 指引
├── CLAUDE.md              # Claude Code 指引
├── LICENSE                # 授權條款
├── README.md              # 主要說明文件
├── START_HERE.md          # 快速開始指南
├── archive/               # 歸檔目錄
├── backend/               # 後端應用程式
├── docs/                  # 文件目錄
├── examples/              # 範例與測試
├── frontend/              # 前端應用程式
├── logs/                  # 日誌目錄
└── scripts/               # 統一執行腳本
```

## 關鍵變更摘要
1. **核心程式碼位置**: `backend/app/core/blind_watermark/`（原始程式碼已歸檔）
2. **虛擬環境位置**: `backend/.venv/`（根目錄的已移除）
3. **文件位置**: `docs/`（舊文件已歸檔）
4. **設定檔位置**: `backend/pyproject.toml`（根目錄的舊設定已歸檔）
5. **歸檔位置**: `archive/`（包含 original_code、old_docs、old_config）

## 注意事項
- 原始的 `blind_watermark/` 套件程式碼已完整保存在 `archive/original_code/`
- 如需參考舊設定或文件，可在 `archive/` 目錄中找到
- 所有操作都透過 `scripts/*.sh` 執行，不直接呼叫套件管理工具
- 專案現在採用前後端分離架構，核心演算法整合在後端
