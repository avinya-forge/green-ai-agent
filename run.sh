#!/bin/bash
# Master Controller [sync | test | start | backlog | skills]
# Aligned with the flat docs/ structure documented in CLAUDE.md.

set -u
MODE="IDEMPOTENT | TERSE | 100%-INTEGRITY"

BACKLOG="docs/backlog.md"

log_blocker() {
    mkdir -p output/logs
    echo "- [RESOLVE] Blocker encountered: $1" >> output/logs/blockers.log
}

# Accept both 'sync' and '--sync' for backward compatibility.
SUBCOMMAND="${1:-}"
SUBCOMMAND="${SUBCOMMAND#--}"

case "$SUBCOMMAND" in
    sync)
        echo "[PHASE: 1-Strategy] | [STATUS: verifying flat docs/ tree]"
        if [ ! -f "$BACKLOG" ]; then
            log_blocker "Missing $BACKLOG"
        fi
        for canonical in docs/roadmap.md docs/standards.md docs/architecture.md docs/release.md; do
            [ -f "$canonical" ] || log_blocker "Missing $canonical"
        done
        ;;
    test)
        echo "[PHASE: 1-Strategy] | [STATUS: running tests]"
        pytest --cov=src || log_blocker "pytest failed"
        flake8 src || log_blocker "flake8 failed"
        ;;
    backlog)
        echo "[PHASE: 1-Strategy] | [STATUS: parsing backlog]"
        grep -E "^\| (BUG|EPIC|TASK|AUDIT|SEC|SCA|QUAL|ESG|DASH|RULE|BASE|SBOM|AI|STD|IDE|TEAM|ML|RUST)-" "$BACKLOG" \
            || log_blocker "no backlog rows matched"
        ;;
    start)
        echo "[PHASE: 1-Strategy] | [STATUS: env initialization]"
        echo "Environment initialized. Use: python -m src.cli dashboard"
        ;;
    skills)
        echo "[PHASE: 1-Strategy] | [STATUS: refreshing skills patterns]"
        mkdir -p output
        curl -fsS https://skills.sh/ \
            | grep -o '"skillId":"[^"]*"' \
            | cut -d '"' -f 4 > output/skills-patterns.txt \
            || log_blocker "skills fetch failed"
        ;;
    *)
        echo "Usage: $0 {sync|test|backlog|start|skills}"
        exit 1
        ;;
esac
