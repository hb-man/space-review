#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
TOOL_NAME="space-review"

usage() {
    echo "Usage: $0 [install|uninstall|update]"
    echo ""
    echo "Commands:"
    echo "  install    Install space-review (default)"
    echo "  uninstall  Remove space-review"
    echo "  update     Update to latest version (clears cache)"
    exit 1
}

ensure_uv() {
    if ! command -v uv &> /dev/null; then
        echo "Installing uv..."
        curl -LsSf https://astral.sh/uv/install.sh | sh
        export PATH="$HOME/.local/bin:$PATH"

        if ! command -v uv &> /dev/null; then
            echo "Error: uv installation failed or not in PATH"
            echo "Please restart your shell and run this script again"
            exit 1
        fi
    fi
}

check_path() {
    UV_BIN_DIR="$HOME/.local/bin"
    if [[ ":$PATH:" != *":$UV_BIN_DIR:"* ]]; then
        echo ""
        echo "Warning: $UV_BIN_DIR is not in your PATH"
        echo ""
        echo "Add this to your shell config (~/.bashrc, ~/.zshrc, etc.):"
        echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
        echo ""
        echo "Then restart your shell or run:"
        echo "  source ~/.bashrc  # or ~/.zshrc"
    fi
}

do_install() {
    ensure_uv
    echo "Installing $TOOL_NAME..."
    uv tool install --force "$PROJECT_DIR"
    check_path
    echo ""
    echo "Installed! Run '$TOOL_NAME --help' to get started."
}

do_uninstall() {
    ensure_uv
    if uv tool list | grep -q "^$TOOL_NAME"; then
        echo "Uninstalling $TOOL_NAME..."
        uv tool uninstall "$TOOL_NAME"
        echo "Uninstalled."
    else
        echo "$TOOL_NAME is not installed."
    fi
}

do_update() {
    ensure_uv
    echo "Updating $TOOL_NAME..."
    uv cache clean "$TOOL_NAME" 2>/dev/null || true
    if uv tool list | grep -q "^$TOOL_NAME"; then
        uv tool uninstall "$TOOL_NAME"
    fi
    uv tool install "$PROJECT_DIR"
    echo ""
    echo "Updated! Run '$TOOL_NAME --help' to get started."
}

cd "$PROJECT_DIR"

COMMAND="${1:-install}"

case "$COMMAND" in
    install)
        do_install
        ;;
    uninstall)
        do_uninstall
        ;;
    update)
        do_update
        ;;
    -h|--help|help)
        usage
        ;;
    *)
        echo "Unknown command: $COMMAND"
        usage
        ;;
esac
