#!/bin/bash
# 驗證專案結構與基本功能

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

echo "========================================="
echo "驗證專案結構"
echo "========================================="

# 檢查目錄結構
echo ""
echo "檢查目錄結構..."
REQUIRED_DIRS=(
    "backend"
    "backend/app"
    "backend/app/api"
    "backend/app/core"
    "backend/app/models"
    "backend/app/services"
    "frontend"
    "frontend/app"
    "frontend/components"
    "frontend/lib"
    "scripts"
)

for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$PROJECT_ROOT/$dir" ]; then
        echo "✓ $dir"
    else
        echo "✗ $dir (缺少)"
        exit 1
    fi
done

# 檢查關鍵檔案
echo ""
echo "檢查關鍵檔案..."
REQUIRED_FILES=(
    "backend/pyproject.toml"
    "backend/app/main.py"
    "backend/run.py"
    "frontend/package.json"
    "frontend/app/page.tsx"
    "scripts/start.sh"
    "scripts/stop.sh"
    "scripts/build.sh"
    "scripts/check.sh"
    "scripts/test.sh"
)

for file in "${REQUIRED_FILES[@]}"; do
    if [ -f "$PROJECT_ROOT/$file" ]; then
        echo "✓ $file"
    else
        echo "✗ $file (缺少)"
        exit 1
    fi
done

# 檢查後端
echo ""
echo "檢查後端..."
cd "$PROJECT_ROOT/backend"

if [ ! -d ".venv" ]; then
    echo "✗ 後端虛擬環境未建立"
    exit 1
fi

echo "✓ 後端虛擬環境存在"

# 測試後端匯入
if source .venv/bin/activate && python -c "from app.main import app" 2>/dev/null; then
    echo "✓ 後端模組可正常匯入"
else
    echo "✗ 後端模組匯入失敗"
    exit 1
fi

# 檢查前端
echo ""
echo "檢查前端..."
cd "$PROJECT_ROOT/frontend"

if [ ! -d "node_modules" ]; then
    echo "⚠ 前端依賴未安裝（執行 npm install）"
else
    echo "✓ 前端依賴已安裝"
fi

# 檢查腳本權限
echo ""
echo "檢查腳本執行權限..."
for script in start.sh stop.sh build.sh check.sh test.sh; do
    if [ -x "$PROJECT_ROOT/scripts/$script" ]; then
        echo "✓ scripts/$script"
    else
        echo "✗ scripts/$script (無執行權限)"
        exit 1
    fi
done

echo ""
echo "========================================="
echo "驗證完成！"
echo "========================================="
echo ""
echo "專案結構正確，可以執行："
echo "  ./scripts/start.sh  # 啟動服務"
echo "  ./scripts/build.sh  # 建置專案"
echo "  ./scripts/check.sh  # 程式碼檢查"
echo "  ./scripts/test.sh   # 執行測試"
echo "========================================="

