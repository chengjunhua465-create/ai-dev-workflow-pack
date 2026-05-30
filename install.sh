#!/usr/bin/env bash
set -euo pipefail

# AI Developer Workflow Pack - Installer
# Usage: bash install.sh [target-directory]

TARGET="${1:-$PWD}"
PACK_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "Installing AI Developer Workflow Pack to: $TARGET"
echo ""

# Copy templates
if [ -d "$PACK_DIR/templates" ]; then
    mkdir -p "$TARGET/templates"
    cp -r "$PACK_DIR/templates/"* "$TARGET/templates/"
    echo "Templates copied"
fi

# Copy MCP configs  
if [ -d "$PACK_DIR/mcp-configs" ]; then
    mkdir -p "$TARGET/.claude"
    echo "MCP configs available at $PACK_DIR/mcp-configs/"
    echo "  cp mcp-configs/*.json .claude/mcp.json"
fi

# Copy commands
if [ -d "$PACK_DIR/commands" ]; then
    mkdir -p "$TARGET/scripts"
    cp "$PACK_DIR/commands/"*.py "$TARGET/scripts/"
    chmod +x "$TARGET/scripts/"*.py
    echo "Commands copied to scripts/"
fi

echo ""
echo "Installation complete!"
echo ""
echo "Next: cp templates/[framework]/CLAUDE.md ./CLAUDE.md"
