# 開始使用盲浮水印系統

## 🚀 快速啟動（3 步驟）

### 步驟 1：驗證環境

```bash
./scripts/verify.sh
```

確保所有檢查項目顯示 ✓

### 步驟 2：啟動服務

```bash
./scripts/start.sh
```

等待服務啟動完成（約 10-30 秒）

### 步驟 3：開啟瀏覽器

訪問 http://localhost:3000 開始使用

---

## 📚 重要文件

| 文件 | 說明 |
|------|------|
| [README_NEW.md](README_NEW.md) | 完整專案說明 |
| [docs/QUICKSTART.md](docs/QUICKSTART.md) | 快速開始指南 |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | 系統架構文件 |
| [docs/PROJECT_SUMMARY.md](docs/PROJECT_SUMMARY.md) | 重構總結 |
| [backend/README.md](backend/README.md) | 後端 API 文件 |

---

## 🔧 管理指令

```bash
# 啟動服務
./scripts/start.sh

# 停止服務
./scripts/stop.sh

# 建置專案
./scripts/build.sh

# 程式碼檢查
./scripts/check.sh

# 執行測試
./scripts/test.sh

# 驗證結構
./scripts/verify.sh
```

---

## 🌐 服務位址

- **前端介面**：http://localhost:3000
- **後端 API**：http://localhost:8000
- **API 文件**：http://localhost:8000/docs
- **健康檢查**：http://localhost:8000/health

---

## 💡 使用提示

### 嵌入浮水印
1. 選擇「嵌入浮水印」分頁
2. 選擇模式（文字/圖片/位元）
3. 上傳圖片並設定參數
4. **重要**：記錄顯示的「浮水印位元長度」
5. 下載結果

### 提取浮水印
1. 選擇「提取浮水印」分頁
2. 選擇相同的模式
3. 上傳含浮水印的圖片
4. 輸入嵌入時的「浮水印位元長度」
5. 輸入相同的密碼
6. 查看結果

---

## ⚠️ 注意事項

1. **浮水印位元長度**必須與嵌入時相同
2. **密碼**必須與嵌入時相同
3. 避免對嵌入後的圖片進行二次壓縮
4. 建議使用 PNG 格式以保持最佳品質

---

## 🆘 遇到問題？

### 常見問題

**Q: 腳本無法執行**
```bash
chmod +x scripts/*.sh
```

**Q: 埠號被佔用**
- 修改 `backend/run.py` 中的 `port=8000`
- 修改 `frontend/.env.local` 中的 `NEXT_PUBLIC_API_URL`

**Q: 提取失敗**
- 檢查浮水印位元長度是否正確
- 檢查密碼是否相同
- 確認圖片未經過二次處理

### 查看日誌

```bash
# 後端日誌
tail -f logs/backend.log

# 前端日誌
tail -f logs/frontend.log
```

---

## 📖 技術棧

### 後端
- FastAPI 0.119+
- Python 3.10+
- OpenCV、NumPy、PyWavelets

### 前端
- Next.js 16.0
- React 19.2
- TypeScript 5+
- Tailwind CSS 4
- shadcn/ui

---

## 🎯 下一步

1. 閱讀 [快速開始指南](docs/QUICKSTART.md)
2. 查看 [API 文件](http://localhost:8000/docs)
3. 探索 [系統架構](docs/ARCHITECTURE.md)
4. 嘗試不同的浮水印模式

---

**祝您使用愉快！**

如有問題，請查看文件或提交 Issue。

