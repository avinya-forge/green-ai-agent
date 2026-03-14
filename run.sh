#!/bin/bash
# Master Controller [Sync | Test | Backlog | Start]

MODE="IDEMPOTENT | TERSE | 100%-INTEGRITY"

log_blocker() {
    echo "- [RESOLVE] Blocker encountered: $1" >> docs/planning/backlog.md
}

case "$1" in
    --sync)
        echo "[PHASE: 1-Strategy] | [SCENARIO: S1-S5] | [STATUS: syncing file-tree]"
        mkdir -p docs/planning docs/architecture docs/engineering || log_blocker "Failed to create dirs"
        touch docs/planning/backlog.md || log_blocker "Failed to touch backlog"
        if [ ! -f docs/planning/roadmap.md ]; then
            echo "# Roadmap" > docs/planning/roadmap.md
        fi
        if [ ! -f docs/architecture/system-design.md ]; then
            echo "# System Design" > docs/architecture/system-design.md
        fi
        if [ ! -f docs/engineering/conventions.md ]; then
            echo "# Engineering Conventions" > docs/engineering/conventions.md
        fi
        ;;
    --test)
        echo "[PHASE: 1-Strategy] | [SCENARIO: S1-S5] | [STATUS: running tests]"
        pytest --cov=src || log_blocker "pytest failed"
        flake8 src || log_blocker "flake8 failed"
        ;;
    --backlog)
        echo "[PHASE: 1-Strategy] | [SCENARIO: S1-S5] | [STATUS: parsing backlog]"
        grep -r -E "\[EPIC|DEBT\]" docs/planning/ || log_blocker "grep backlog failed"
        # Recursive expansion of backlog items
        while IFS= read -r epic; do
            echo "Expanding: $epic"
            grep -r -E "TASK" docs/planning/ | grep -v "\[x\]" || true
        done < <(grep -r -E "\[EPIC|DEBT\]" docs/planning/)
        if [ -f docs/engineering/skills-patterns.txt ]; then
            echo "Applying skills patterns to backlog..."
            grep -f docs/engineering/skills-patterns.txt docs/planning/backlog.md || true
        fi
        ;;
    --start)
        echo "[PHASE: 1-Strategy] | [SCENARIO: S1-S5] | [STATUS: env initialization]"
        echo "Environment initialized."
        ;;
    --skills)
        echo "[PHASE: 1-Strategy] | [SCENARIO: S1-S5] | [STATUS: injecting patterns]"
        curl -s https://skills.sh/ | grep -o '"skillId":"[^"]*"' | cut -d '"' -f 4 > docs/engineering/skills-patterns.txt || log_blocker "skills fetch failed"
        ;;
    *)
        echo "Usage: \$0 {--sync|--test|--backlog|--start|--skills}"
        ;;
esac
