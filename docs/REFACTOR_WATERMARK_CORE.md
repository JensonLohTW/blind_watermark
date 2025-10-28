# 浮水印核心重構說明

## 1. 現況分析摘要
- `blind_watermark` 目錄平鋪 9 個檔案，演算法、CLI、攻擊模擬混在一起，缺乏明確分層。
- `WaterMark` 同時負責檔案 I/O、密碼處理與演算法調度，屬於低內聚高耦合。
- `WaterMarkCore` 內部充斥可變狀態 (`self.ca_block`、`self.idx_shuffle`)，不易測試與擴充。
- 攻擊/恢復模組包含檔案讀寫與陣列操作混雜的實作，無型別註記。
- CLI 使用舊式 `optparse`，與核心程式碼相互依賴，難以重用。

## 2. 新目錄結構
```
backend/app/core/watermark/
├── __init__.py
├── cli/
│   ├── __init__.py
│   └── entrypoint.py          # argparse CLI
├── config.py                  # dataclass 型態安全設定
├── operations/
│   ├── __init__.py
│   ├── algorithm.py           # DWT-DCT-SVD 核心
│   ├── blocks.py              # 區塊視圖與洗牌工具
│   └── transforms.py          # 色彩與 padding 轉換
├── robustness/
│   ├── __init__.py
│   ├── attacks.py             # 攻擊模擬純函式化
│   └── recovery.py            # 範本匹配與恢復
├── runner/
│   ├── __init__.py            # WatermarkPipeline 與高階 API
│   ├── encoder.py             # 水印載入/加密
│   └── extractor.py           # 水印提取/解密
└── runtime/
    ├── __init__.py
    └── pool.py                # AutoPool context manager
```
- 每層檔案數 ≤ 4，單檔 < 200 行。
- 相容介面整合至上述結構，原 `blind_watermark` 目錄已移除。

## 3. 模組職責與依賴
- `config.py`：封裝密碼、區塊、運行模式設定，提供 `validate()` 保障輸入。
- `operations.algorithm`：專責演算法計算，拆出 `_embed_task`、`_extract_task` 供平行化安全使用。
- `runner.encoder / extractor`：處理水印載入、加密、解密與資料格式轉換。
- `runner.WatermarkPipeline`：提供高階流程 (`read_img`,`read_wm`,`embed`,`extract`)，亦供後端服務直接使用。
- `robustness.attacks / recovery`：改以純 numpy / OpenCV 操作，並保留檔案 I/O 選項。
- `runtime.pool.AutoPool`：context manager 化，避免舊版全域 `set_start_method` 副作用。
- 相依關係：`config → operations → runner`，`runtime`、`robustness` 為邊緣模組；無循環依賴。

## 4. 演算法優化
- 區塊處理改用 `BlockSequence` 與 `reshape + swapaxes`，取代 `np.lib.stride_tricks` 手工計算，減少錯位風險。
- `AutoPool` 允許以 multiprocessing/threading/common 模式執行，且 map 任務使用頂層函式，確保可序列化。
- 嵌入/提取流程避免多餘拷貝，僅於必要處複製；K-means 分類保留原邏輯並加入輸入退化處理。
- 攻擊與恢復函式提供純陣列介面，減少 I/O 開銷並便於測試。

## 5. 受影響呼叫點
- 後端服務 `backend/app/services/watermark_service.py` 現已改用 `app.core.watermark.WaterMark`。
- CLI 直接透過 `app.core.watermark.cli.entrypoint` 執行，原 `blind_watermark.cli_tools` 已下線。
- 範例程式、文件需改為匯入 `from app.core.watermark import WaterMark` 與對應模組。
- 仍可透過 `from app.core.watermark import WatermarkPipeline` 取得更彈性的流程控制。

## 6. 遷移指南
1. 若現有程式使用 `WaterMark`：
   - 介面維持 `read_img` / `read_wm` / `embed` / `extract`，但已不再暴露 `WaterMarkCore`。
   - 建議逐步改以 `WatermarkPipeline` 或 `WatermarkAlgorithm` 取得更細粒度控制。
2. 若需要直接呼叫攻擊/恢復工具：改用 `from app.core.watermark import att` 或 `from app.core.watermark import recover`。
3. CLI 需改為執行 `python -m app.core.watermark.cli.entrypoint --help` 取得最新命令。
4. 推薦後端服務改為直接處理記憶體陣列，避免臨時檔案：
   ```python
   from app.core.watermark import WatermarkConfig, WatermarkPipeline
   pipeline = WatermarkPipeline(WatermarkConfig())
   pipeline.read_img(img=image_array)
   pipeline.read_wm(text, mode="str")
   watermarked = pipeline.embed()
   ```

## 7. 驗證建議
- 需安裝 OpenCV 後執行 `./scripts/test.sh`，確保後端 pytest 與範例可運行。
- 針對常見攻擊流程（裁剪、旋轉、亮度）執行 `robustness.attacks` 函式，確認輸出型態與過往一致。
- 對照重構前後的水印提取結果，確保 `password_img`、`password_wm` 組合相同時輸出不變。
