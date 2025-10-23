#!/bin/bash
# 啟動前後端服務

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"

mkdir -p "$LOG_DIR"

echo "========================================="
echo "啟動盲浮水印系統"
echo "========================================="

# 啟動後端
echo ""
echo "正在啟動後端服務..."
cd "$PROJECT_ROOT/backend"

# 檢查虛擬環境
if [ ! -d ".venv" ]; then
    echo "建立 Python 虛擬環境..."
    uv venv
fi

# 安裝依賴
echo "安裝後端依賴..."
uv pip install -e . > "$LOG_DIR/backend-install.log" 2>&1

# 啟動後端（背景執行）
echo "啟動後端 API 服務（埠號 8000）..."
uv run python run.py > "$LOG_DIR/backend.log" 2>&1 &
BACKEND_PID=$!
echo $BACKEND_PID > "$LOG_DIR/backend.pid"
echo "後端 PID: $BACKEND_PID"

# 等待後端啟動
echo "等待後端服務啟動..."
sleep 3

# 啟動前端
echo ""
echo "正在啟動前端服務..."
cd "$PROJECT_ROOT/frontend"

# 安裝依賴（如果需要）
if [ ! -d "node_modules" ]; then
    echo "安裝前端依賴..."
    npm install > "$LOG_DIR/frontend-install.log" 2>&1
fi

# 啟動前端（背景執行）
echo "啟動前端開發伺服器（埠號 3000）..."
npm run dev > "$LOG_DIR/frontend.log" 2>&1 &
FRONTEND_PID=$!
echo $FRONTEND_PID > "$LOG_DIR/frontend.pid"
echo "前端 PID: $FRONTEND_PID"

echo ""
echo "========================================="
echo "服務啟動完成！"
echo "========================================="
echo "後端 API: http://localhost:8000"
echo "前端介面: http://localhost:3000"
echo "API 文件: http://localhost:8000/docs"
echo ""
echo "日誌檔案位置："
echo "  後端: $LOG_DIR/backend.log"
echo "  前端: $LOG_DIR/frontend.log"
echo ""
echo "使用 scripts/stop.sh 停止服務"
echo "========================================="

