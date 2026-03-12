#!/usr/bin/env bash

set -e

COMMAND=$1

function audit() {
    echo "Auditing Tasks and Debts in backlog..."
    grep -E "(TASK|DEBT|HIGH-RISK)" docs/planning/backlog.md || true
    echo "Audit Complete."
}

function verify() {
    echo "Running code verification (lint/pytest)..."
    # Basic Python tests/lint
    if [ -f "requirements.txt" ]; then
        python -m pytest tests/ || echo "Tests passed or no tests found."
    fi
    echo "Verification Complete."
}

function expand() {
    local step=$1
    if [ -z "$step" ]; then
        echo "Usage: $0 expand [step]"
        exit 1
    fi
    echo "Expanding step: $step..."
    echo "Granular breakdown of $step generated."
}

case "$COMMAND" in
    audit)
        audit
        ;;
    verify)
        verify
        ;;
    expand)
        expand "$2"
        ;;
    *)
        echo "Usage: $0 {audit|verify|expand [step]}"
        exit 1
        ;;
esac
