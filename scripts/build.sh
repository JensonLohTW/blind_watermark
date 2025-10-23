#!/bin/bash
# 建置前後端專案

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
LOG_DIR="$PROJECT_ROOT/logs"

mkdir -p "$LOG_DIR"

echo "========================================="
echo "建置盲浮水印系統"
echo "========================================="

# 建置後端
echo ""
echo "建置後端..."
cd "$PROJECT_ROOT/backend"

if [ ! -d ".venv" ]; then
    echo "建立 Python 虛擬環境..."
    uv venv
fi

echo "安裝後端依賴..."
uv pip install -e . > "$LOG_DIR/backend-build.log" 2>&1
echo "後端建置完成"

# 建置前端
echo ""
echo "建置前端..."
cd "$PROJECT_ROOT/frontend"

echo "安裝前端依賴..."
npm install > "$LOG_DIR/frontend-install.log" 2>&1

echo "執行前端建置..."
npm run build > "$LOG_DIR/frontend-build.log" 2>&1
echo "前端建置完成"

echo ""
echo "========================================="
echo "建置完成！"
echo "========================================="
echo "建置日誌："
echo "  後端: $LOG_DIR/backend-build.log"
echo "  前端: $LOG_DIR/frontend-build.log"
echo "========================================="

