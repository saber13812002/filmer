#!/usr/bin/env bash
# نصب آفلاین از wheelهای داخل offline-wheels/
# اجرا از ریشه پروژه:
#   bash scripts/install_offline_wheels.sh

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
WHEELS_DIR="$PROJECT_ROOT/offline-wheels"
VENV_DIR="$PROJECT_ROOT/.venv"
REQ_FILE="$PROJECT_ROOT/requirements.txt"

echo "=== Filmer: Install from offline wheels ==="
echo "Project: $PROJECT_ROOT"
echo "Wheels:  $WHEELS_DIR"
echo ""

if [[ ! -d "$WHEELS_DIR" ]]; then
    echo "Error: offline-wheels/ not found. Run download_offline_wheels.ps1 on Windows first." >&2
    exit 1
fi

WHEEL_COUNT=$(find "$WHEELS_DIR" -maxdepth 1 \( -name '*.whl' -o -name '*.tar.gz' \) 2>/dev/null | wc -l)
if [[ "$WHEEL_COUNT" -eq 0 ]]; then
    echo "Error: no .whl or .tar.gz files in offline-wheels/" >&2
    echo "Push wheels from Windows first (scripts/download_offline_wheels.ps1)." >&2
    exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
    echo "Creating venv ..."
    python3 -m venv "$VENV_DIR"
fi

PIP="$VENV_DIR/bin/pip"
PYTHON="$VENV_DIR/bin/python"

echo "Wheels found: $WHEEL_COUNT"
if [[ -f "$WHEELS_DIR/MANIFEST.txt" ]]; then
    echo "--- MANIFEST ---"
    cat "$WHEELS_DIR/MANIFEST.txt"
    echo "----------------"
fi

echo ""
echo "Installing from local wheels (no internet) ..."
"$PIP" install --upgrade pip wheel setuptools 2>/dev/null || true

"$PIP" install \
    --no-index \
    --find-links="$WHEELS_DIR" \
    -r "$REQ_FILE"

echo ""
echo "Verifying imports ..."
"$PYTHON" -c "
import pydantic, chromadb, numpy
import sentence_transformers
print('pydantic', pydantic.__version__)
print('chromadb', chromadb.__version__)
print('numpy', numpy.__version__)
print('sentence_transformers', sentence_transformers.__version__)
print('[OK] All core packages import successfully')
"

echo ""
echo "=== Done ==="
echo "Activate: source .venv/bin/activate"
