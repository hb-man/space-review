#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
OUTPUT_DIR="${PROJECT_DIR}/dist"
OUTPUT_FILE="${OUTPUT_DIR}/space-review"

cd "$PROJECT_DIR"

if ! command -v shiv &> /dev/null; then
    echo "Installing shiv..."
    uv tool install shiv
fi

mkdir -p "$OUTPUT_DIR"

echo "Building standalone executable..."
shiv -c space-review -o "$OUTPUT_FILE" .

chmod +x "$OUTPUT_FILE"

echo ""
echo "Built: $OUTPUT_FILE"
echo "Copy it anywhere in your PATH to use globally."
