#!/bin/bash
# Wrapper for Watermark CLI

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT/backend"
uv run python -m app.core.watermark.cli.entrypoint "$@"

