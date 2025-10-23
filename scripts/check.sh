#!/bin/bash
# 執行型別檢查與 Lint

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "執行程式碼檢查"
echo "========================================="

# 檢查後端
echo ""
echo "檢查後端程式碼..."
cd "$PROJECT_ROOT/backend"

if [ ! -d ".venv" ]; then
    echo "建立 Python 虛擬環境..."
    uv venv
    uv pip install -e ".[dev]"
fi

echo "執行 Ruff 檢查..."
uv run ruff check app/ || echo "發現 Lint 問題"

# 檢查前端
echo ""
echo "檢查前端程式碼..."
cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo "安裝前端依賴..."
    npm install
fi

echo "執行 TypeScript 型別檢查..."
npx tsc --noEmit || echo "發現型別錯誤"

echo "執行 ESLint 檢查..."
npm run lint || echo "發現 Lint 問題"

echo ""
echo "========================================="
echo "檢查完成"
echo "========================================="

