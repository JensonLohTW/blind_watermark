#!/bin/bash
# 停止前後端服務

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"

echo "========================================="
echo "停止盲浮水印系統"
echo "========================================="

# 停止後端
if [ -f "$LOG_DIR/backend.pid" ]; then
    BACKEND_PID=$(cat "$LOG_DIR/backend.pid")
    echo "停止後端服務 (PID: $BACKEND_PID)..."
    kill $BACKEND_PID 2>/dev/null || echo "後端服務已停止"
    rm -f "$LOG_DIR/backend.pid"
else
    echo "未找到後端 PID 檔案"
fi

# 停止前端
if [ -f "$LOG_DIR/frontend.pid" ]; then
    FRONTEND_PID=$(cat "$LOG_DIR/frontend.pid")
    echo "停止前端服務 (PID: $FRONTEND_PID)..."
    kill $FRONTEND_PID 2>/dev/null || echo "前端服務已停止"
    rm -f "$LOG_DIR/frontend.pid"
else
    echo "未找到前端 PID 檔案"
fi

# 清理可能殘留的 Node.js 和 Python 進程
echo ""
echo "清理殘留進程..."
pkill -f "uvicorn app.main:app" 2>/dev/null || true
pkill -f "next dev" 2>/dev/null || true

echo ""
echo "========================================="
echo "服務已停止"
echo "========================================="

