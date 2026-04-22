# Standards

## File & Folder Policy

```
green-ai-agent/
├── src/          # All source code
├── tests/        # pytest test suite
├── rules/        # YAML rule definitions (one file per language)
├── docs/         # Documentation (5 canonical files + docs/api/)
├── output/       # ALL generated reports, logs, CSVs
├── deploy/       # Kubernetes + Helm manifests
├── prompts/      # AI agent prompt templates
└── [root]        # README.md, CLAUDE.md, requirements.txt, config files only
```

**No new files or folders without explicit user approval.**  
All generated output goes to `output/`. No exceptions.  
No new `docs/` subdirectories — the flat structure is canonical.

---

## Dependency Management

Pin all runtime dependencies that have proven to cause breaking changes on silent upgrades:

```
# Exact pins (breaking-change history)
pydantic-core==2.41.5     # pydantic 2.12.5 requires exactly this
fastapi==0.136.0           # Starlette 1.0 TemplateResponse API broke on upgrade
starlette==1.0.0           # Listed explicitly to prevent transitive upgrades
uvicorn[standard]==0.45.0  # Pinned to match fastapi/starlette tested set
python-socketio==5.16.1    # ASGI mode; interface stable across 5.x
pygls==2.0.1               # LSP server; 3.x has breaking protocol changes
greenlet==3.3.2            # Required by asyncio bridge
lsprotocol==2025.0.0       # LSP protocol definitions
playwright==1.58.0         # Browser automation; test fixtures depend on exact version
pyee==13.0.1               # Event emitter pinned with socketio

# Never pin these in requirements.txt
# pip — managed by the OS/virtualenv, not application deps
# setuptools, wheel — managed by pip itself
```

**Rule:** If a dep has no pin and its upgrade breaks the test suite, add an exact pin to `requirements.txt` and log a backlog item.

---

## Coding Conventions

### Python

- **Imports:** Absolute from `src` root.
  ```python
  from src.core.scanner import Scanner          # correct
  from src.core.export import CSVExporter       # correct
  from export import CSVExporter                # wrong
  ```

- **Paths:** Always `pathlib.Path`.
  ```python
  from pathlib import Path
  output_dir = Path(__file__).parent.parent / "output"   # correct
  output_dir = "output\\"                                 # wrong
  ```

- **Type hints:** Required on all function signatures.
  ```python
  def analyze(code: str) -> dict[str, int]: ...   # correct
  def analyze(code): ...                           # wrong
  ```

- **Logging:** Always to `output/logs/app.log`.
  ```python
  logs_dir = Path(__file__).parent.parent.parent / "output" / "logs"
  logs_dir.mkdir(parents=True, exist_ok=True)
  handler = logging.FileHandler(logs_dir / "app.log")
  ```

- **Style:** PEP 8. flake8 enforced. Ignored: E501, W291, W293, W504.

- **Data models:** Pydantic v2 for all structured data.

### JavaScript / TypeScript

- Always `"use strict"`.
- `const` over `let`; never `var`.
- `async/await` over callbacks or raw `.then()`.
- No `innerHTML` without `escapeHTML` sanitization.

### Algorithms

- O(n) or O(1) preferred. O(n log n) acceptable with justification.
- O(n²) or worse: must be documented with a task to fix.
- Nesting depth > 2: refactor or document why.
- No unbounded loops without explicit termination conditions.

---

## Rule Definitions

Rules live in `rules/<language>.yaml`. Each rule must have all fields:

```yaml
- id: no_infinite_loops              # unique, snake_case
  name: No Infinite Loops            # human-readable
  description: |                     # full description
    Infinite loops consume continuous CPU cycles...
  severity: critical                 # critical | high | major | medium | minor | low | info
  languages: [python]                # list of applicable languages
  pattern: |                         # regex or AST query
    while\s*True\s*:
  remediation: |                     # how to fix it
    Add a break condition or use a bounded loop.
  source: GSF                        # GSF | ecoCode | custom
  tags: [performance, energy]        # categorization
```

**Severity levels (in order):** `critical` → `high` → `major` → `medium` → `minor` → `low` → `info`

---

## Security Rules

These apply to all code at all times:

1. **No path traversal:** Any API endpoint that accepts a file path parameter must resolve and validate it against the project root before opening. Use `Path(file).resolve()` and check `str(resolved).startswith(str(project_root))`.
2. **No shell injection:** Never pass user input to `subprocess.run(shell=True)` or `os.system()`.
3. **No raw SQL:** All DB queries via SQLAlchemy ORM or parameterized statements only.
4. **No unescaped HTML:** All user-facing content rendered via Jinja2 must use autoescaping. Never use `innerHTML` without `escapeHTML`.
5. **Input validation:** All API query/body params validated via Pydantic models before use.

---

## Quality Gates

All tasks must pass every gate before being marked done:

| Gate | Requirement |
|---|---|
| **Test** | ≥95% coverage on new code paths (verified via `pytest --cov`) |
| **Lint** | 0 flake8 errors in touched files |
| **Opt** | Big-O analysis completed; no O(n²) without written justification |
| **Sec** | Input sanitized; no raw SQL, no shell injection, no unescaped HTML, no path traversal |

State-sync: a task is **not done** unless the document accurately reflects the live code state.

---

## Testing

- **Framework:** pytest
- **Location:** `tests/` directory mirroring `src/` structure
- **Coverage target:** ≥95%
- **Mocking:** `unittest.mock` or `pytest-mock` for external dependencies
- **Fixtures:** `tests/conftest.py` for shared setup
- **Rule tests:** New rules must have tests in `tests/test_rules.py` or detector-specific test files
- **Security tests:** `tests/security/` for OWASP and injection scenarios
- **E2E tests:** `tests/e2e/` using Playwright for dashboard flows

```bash
python3 -m pytest tests/ -v --cov=src --cov-report=term-missing
```

Current baseline: **597 passed, 2 skipped, 0 failed.**

---

## API Schema Rule

No API endpoint goes to production without:
1. A verified entry in `docs/api/swagger.yaml`
2. A corresponding mock response in `docs/api/mock_data.json`

---

## Workflow

1. **Branch:** `feat/<slug>` or `claude/<epic-id>-<slug>` off `main`
2. **Commit:** Atomic, 1-2 hour scope per commit
3. **PR:** Draft PR after every push; full PR for review when task complete
4. **Review:** Adversarial triad check before merge
5. **Merge:** Only when all 4 gates pass and CI is green
6. **Release:** Update `docs/release.md` with user-facing changes

---

## Pre-commit Hooks

Installed via `./scripts/install_hooks.sh`. Checks on every commit:

1. **File placement:** No CSV/HTML in root (must be in `output/`)
2. **Docs allowlist:** Only canonical files permitted in `docs/`
3. **Imports:** Correct absolute imports from `src`
4. **Auto-scan:** Staged Python files scanned for green software violations

Bypass (not recommended): `git commit --no-verify`

---

## Adversarial Triad

Apply before marking any task done or raising a PR:

| Role | Checks |
|---|---|
| **OPTIMIZER** | O(n) efficiency; no dead code; no bloat; use caching where applicable |
| **HARDENER** | Security sanitization; ≥95% test coverage; 0 lint errors; OWASP compliance |
| **PRAGMATIST** | 1-2hr atomicity per task; 99% utility rule (strip edge-case bloat) |

---

## Action Registry

| Action | Meaning |
|---|---|
| `[action: complete]` | Task fully done, all gates passed |
| `[action: bump]` | Increment version after milestone |
| `[action: drill]` | Break an epic into sub-tasks |
| `[action: refresh]` | Re-sync backlog against live code |
| `[action: audit]` | Cross-check backlog for drift from live code state |

---

## Pruning Mandate

Every session must run `vulture src/` to identify dead code. Remove:
- Unused imports
- Unused variables and arguments
- Unreachable functions and classes

This maintains the Cleanliness Score target of ≥94%.
