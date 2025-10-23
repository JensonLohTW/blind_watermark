# Task Completion Checklist

## 任務完成時必須執行的檢查清單

### 1. 使用統一腳本進行驗證
**重要**: 所有檢查必須透過 `scripts/*.sh` 執行

```bash
# 驗證專案結構
./scripts/verify.sh

# 程式碼檢查（型別、Lint、靜態分析）
./scripts/check.sh

# 執行測試
./scripts/test.sh

# 建置專案
./scripts/build.sh
```

### 2. 後端測試
如果修改了後端核心程式碼，執行相關範例腳本：
```bash
cd examples

# 如果影響字串浮水印
python example_str.py

# 如果影響圖片浮水印
python example_img.py

# 如果影響位元陣列浮水印
python example_bit.py

# 一般功能測試
python example_no_writing.py
```

### 3. 前端測試
如果修改了前端程式碼：
```bash
# 透過統一腳本啟動
./scripts/start.sh

# 手動測試 UI 功能
# - 上傳圖片
# - 嵌入浮水印
# - 提取浮水印
# - 下載結果
```

### 4. 程式碼品質檢查

#### 必須檢查項目
- ✓ 檔案尺寸：動態語言 ≤ 200 行，靜態語言 ≤ 250 行
- ✓ 目錄檔案數：每層 ≤ 8 個檔案
- ✓ 命名規範：Python 使用 snake_case，TypeScript 使用 camelCase/PascalCase
- ✓ 型別安全：TypeScript 避免使用 `any`，Python 使用強型別資料結構
- ✓ 註解與文件：使用繁體中文
- ✓ 無 emoji

#### Linus 的三問（自檢）
1. 這是**真問題**嗎？
2. 有**更簡單**的方法嗎？
3. 會**破壞**什麼嗎（相容性）？

### 5. 文件更新

#### 必須更新的文件
- `docs/ARCHITECTURE.md`：如果架構變更
- `README.md`：如果使用者介面 API 變更
- `docs/PROJECT_SUMMARY.md`：如果專案摘要需更新
- `.serena/memories/`：如果有重要資訊需記錄

#### 程式碼註解
- 為複雜演算法修改新增註解
- 使用繁體中文撰寫
- 說明「為什麼」而非「是什麼」

### 6. 功能驗證

#### 浮水印功能變更
- ✓ 嵌入成功且無錯誤
- ✓ 提取正確恢復浮水印
- ✓ 圖片品質可接受（視覺檢查）
- ✓ 對攻擊的強健性（如適用）

#### 前端功能變更
- ✓ UI 美觀且易用
- ✓ 符合 a11y 標準（ARIA、鍵盤操作、焦點管理）
- ✓ 效能指標達標（LCP ≤ 2.5s、TTI ≤ 3.5s、CLS ≤ 0.1）
- ✓ 互動流暢，微互動合理

### 7. 邊界情況考量

#### 浮水印演算法
- 圖片維度（填充後必須為偶數）
- 浮水印容量限制（block_num vs wm_size）
- 密碼一致性（嵌入/提取之間）
- 透明圖片（4 通道支援）
- 攻擊恢復場景

#### 前端應用
- 檔案大小限制
- 支援的圖片格式
- 錯誤處理與使用者回饋
- 載入狀態與進度指示

### 8. Git 提交

#### 提交前檢查
- ✓ 所有測試通過
- ✓ 程式碼檢查通過
- ✓ 文件已更新
- ✓ 無未追蹤的重要檔案

#### 提交規範
- 使用繁體中文
- 格式：`[類型] 簡短描述`
- 類型：新增、修改、修正、重構、文件、測試等
- 頻繁提交，每個里程碑完成後立即提交

#### 提交指令
```bash
git status
git add .
git commit -m "[類型] 描述變更內容"
git push
```

### 9. DoD（Definition of Done）檢查清單

#### 必須通過
- ✓ 型別檢查通過
- ✓ 靜態掃描通過
- ✓ 單元/整合/關鍵流程測試通過
- ✓ 日誌與監控點已設置
- ✓ 文件已同步更新
- ✓ 尺寸/目錄上限校驗通過
- ✓ CI 全綠（透過 `scripts/` 執行）

#### 可選檢查
- 覆蓋率：單元 ≥ 80%，關鍵模組 ≥ 90%
- 效能指標達標
- 版本相容性確認

### 10. 專案結構驗證

#### 根目錄整潔度
```bash
ls -1
# 應該只看到 12 個項目：
# AGENTS.md, CLAUDE.md, LICENSE, README.md, START_HERE.md,
# archive/, backend/, docs/, examples/, frontend/, logs/, scripts/
```

#### 虛擬環境位置
```bash
# 確認 backend/.venv/ 存在
ls -la backend/ | grep .venv

# 確認根目錄沒有 .venv/
ls -la | grep .venv  # 應該沒有輸出
```

#### 歸檔目錄完整性
```bash
# 查看歸檔結構
tree archive/ -L 2
# 應該包含：original_code/, old_docs/, old_config/
```

## 自動化 CI/CD（未來）

### 目前狀態
- 專案使用 Travis CI（見 .travis.yml）但手動執行
- 無 pre-commit hooks 設定
- 無自動格式化（black/autopep8）設定
- 主要驗證方法為手動測試

### 建議改進
- 設置 pre-commit hooks
- 整合自動格式化工具
- 設置 GitHub Actions 或其他 CI/CD
- 自動執行 `scripts/check.sh` 和 `scripts/test.sh`
