#!/bin/bash
# Install pre-commit hooks for Green-AI Agent
# Run this script to set up your development environment.

set -e

HOOK_SOURCE=".git_hooks_pre-commit.sh"
HOOK_DEST=".git/hooks/pre-commit"

if [ ! -d ".git" ]; then
    echo "❌ Error: Not a git repository. Run this from the project root."
    exit 1
fi

if [ ! -f "$HOOK_SOURCE" ]; then
    echo "❌ Error: Hook source '$HOOK_SOURCE' not found."
    exit 1
fi

echo "Installing pre-commit hook..."
cp "$HOOK_SOURCE" "$HOOK_DEST"
chmod +x "$HOOK_DEST"

echo "✅ Pre-commit hook installed successfully!"
echo "   Location: $HOOK_DEST"
exit 0
