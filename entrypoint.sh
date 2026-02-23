#!/bin/bash
set -e

# Green-AI GitHub Action Entrypoint

# Map Inputs to Variables
TARGET=${INPUT_TARGET:-"."}
OUTPUT=${INPUT_OUTPUT:-""}
FORMAT=${INPUT_FORMAT:-""}
CONFIG=${INPUT_CONFIG:-""}
FAIL_ON=${INPUT_FAIL_ON:-""}
GIT_URL=${INPUT_GIT_URL:-""}
BRANCH=${INPUT_BRANCH:-""}

echo "Starting Green-AI Scan..."

# Build Command using Array to prevent injection
ARGS=("python" "-m" "src.cli" "scan")

# Logic: If GIT_URL is present, use it. Otherwise use TARGET path.
if [ -n "$GIT_URL" ]; then
    ARGS+=("--git-url" "$GIT_URL")
    if [ -n "$BRANCH" ]; then
        ARGS+=("--branch" "$BRANCH")
    fi
else
    # Split TARGET by space to handle multiple paths
    read -ra TARGETS <<< "$TARGET"
    ARGS+=("${TARGETS[@]}")
fi

# Export logic
if [ -n "$OUTPUT" ]; then
    if [ -n "$FORMAT" ]; then
        # Format: path
        ARGS+=("--export" "$FORMAT:$OUTPUT")
    else
        echo "::error::Output path provided but no format specified. Please use 'format' input."
        exit 1
    fi
elif [ -n "$FORMAT" ]; then
    # Format only (auto-named)
    ARGS+=("--export" "$FORMAT")
fi

# Config logic
if [ -n "$CONFIG" ]; then
    ARGS+=("--config" "$CONFIG")
fi

# Print and Run
echo "Executing: ${ARGS[*]}"
"${ARGS[@]}"

# TODO: Implement FAIL_ON logic by parsing results or adding CLI flag
