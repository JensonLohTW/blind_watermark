#!/bin/bash
# 執行測試

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "執行測試"
echo "========================================="

# 測試後端
echo ""
echo "執行後端測試..."
cd "$PROJECT_ROOT/backend"

if [ ! -d ".venv" ]; then
    echo "建立 Python 虛擬環境..."
    uv venv
    uv pip install -e ".[dev]"
fi

if [ -d "tests" ] && [ "$(ls -A tests)" ]; then
    echo "執行 pytest..."
    uv run pytest tests/ -v
else
    echo "未找到後端測試檔案"
fi

# 測試核心功能（使用原有的 examples）
echo ""
echo "執行核心功能測試..."
cd "$PROJECT_ROOT/examples"
if [ -f "example_no_writing.py" ]; then
    echo "執行 example_no_writing.py..."
    cd "$PROJECT_ROOT/backend"
    uv run python ../examples/example_no_writing.py
fi

echo ""
echo "========================================="
echo "測試完成"
echo "========================================="

