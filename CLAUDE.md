# CLAUDE.md — Green-AI Agent

## Project Context

Green-AI is an energy-efficiency code scanner that detects and remediates inefficient code patterns across Python, JavaScript, TypeScript, Java, Go, and C#. It uses AST-based analysis (tree-sitter), a YAML-driven rule engine, a FastAPI web dashboard, LLM-powered auto-fix, and CI/CD integrations.

**Current version:** v0.9.1  
**Current phase:** Phase 2 — Action & Expansion (ACTIVE)  
**Active milestone:** EPIC-00 STABILITY GATE (94% cleanliness score target)

## Key Entry Points

| Purpose | Path |
|---|---|
| CLI entry | `src/cli/main.py` |
| FastAPI dashboard | `src/ui/app_fastapi.py` |
| Scanner engine | `src/core/scanner/main.py` |
| Rule engine | `src/core/rules.py` |
| Domain models | `src/core/domain.py` |
| Config models | `src/core/config_models.py` |
| Detectors | `src/core/detectors/` |
| Rule definitions | `rules/*.yaml` |

## Development Commands

```bash
# Run all tests
python -m pytest tests/ -v

# Run tests with coverage
python -m pytest tests/ -v --cov=src --cov-report=term-missing

# Lint
flake8 src/ tests/

# Start dashboard
python -m src.cli dashboard --host 0.0.0.0 --port 5000

# Run a scan
python -m src.cli scan ./src

# Auto-fix with LLM
python -m src.cli fix_ai ./src

# Full sync via master controller
./run.sh sync
./run.sh test
./run.sh start
```

## Branch Strategy

- **Main branch:** `main` — stable, gated by CI
- **Feature branches:** `claude/<epic-id>-<slug>` or `feat/<slug>`
- **Never push directly to main**
- Always push with: `git push -u origin <branch-name>`
- Create a draft PR after every push

## File Creation Policy

**STRICT:** No new files or folders without explicit user approval.

- All generated output → `output/` (reports, logs, CSVs)
- Source code → `src/`
- Tests → `tests/`
- Rules → `rules/` (YAML, one file per language)
- Docs → `docs/` (only the 5 canonical files + `docs/api/`)
- No new markdown files unless explicitly requested

**Canonical docs (do not add subdirectories):**
- `docs/roadmap.md` — phased roadmap and milestones
- `docs/backlog.md` — active task list by epic
- `docs/standards.md` — coding standards, rules, and quality gates
- `docs/architecture.md` — vision, design decisions, deployment
- `docs/release.md` — release notes and metrics
- `docs/api/swagger.yaml` — OpenAPI schema
- `docs/api/mock_data.json` — mock response data

## Code Standards (summary)

Full detail in `docs/standards.md`. Key rules:

1. **Python imports:** Always absolute from `src` root — `from src.core.scanner import Scanner`
2. **Paths:** Always `pathlib.Path`, never string concatenation
3. **Type hints:** Required on all function signatures
4. **Logging:** Always to `output/logs/app.log` via `logging.FileHandler`
5. **Output files:** Always to `output/` directory
6. **Algorithms:** O(n) or better; no nested loops > 2 deep without justification
7. **No `var` in JS/TS;** use `const`, then `let`; always `async/await`
8. **Pydantic models** for all API request/response schemas

## Definition of Done

A task is complete only when all four gates pass:
- **Test:** ≥95% coverage on new code paths
- **Lint:** 0 flake8 errors in touched files
- **Opt:** Big-O analysis done; no O(n²) unless justified
- **Sec:** Input sanitization applied; no raw SQL, no shell injection

## Architecture Summary

```
src/
├── cli/          # Click CLI (8 commands: scan, project, dashboard, standards, calibrate, fix_ai, init, ci, lsp)
├── core/
│   ├── scanner/  # ProcessPoolExecutor-based multi-file scanner
│   ├── detectors/# tree-sitter AST detectors per language
│   ├── rules.py  # YAML rule loader and registry
│   ├── domain.py # Pydantic models (Violation, Project, ViolationSeverity)
│   ├── export/   # CSV, HTML, PDF, JSON exporters
│   ├── llm/      # OpenAI + Ollama provider abstraction
│   ├── remediation/ # LibCST-based auto-fix transformers
│   ├── security/ # Middleware: rate limiting, security headers
│   └── config.py # Configuration management
├── ui/           # FastAPI + Uvicorn dashboard with Socket.IO
├── ide/          # VS Code extension + pygls LSP server
├── standards/    # GSF + ecoCode standard registry
└── agents/       # Runtime monitoring agents
```

## Adversarial Triad Review

Before marking any task done, apply the triad:
- **OPTIMIZER:** Is this O(n) or better? No code bloat?
- **HARDENER:** Are there security risks? Is coverage ≥95%? 0 lint errors?
- **PRAGMATIST:** Can this be done in 1-2 hours? Does it meet the 99% utility rule?

## Dependency Constraints

- `pydantic-core==2.41.5` — pinned exactly (pydantic 2.12.5 requires this exact version)
- `fastapi==0.136.0` + `starlette==1.0.0` — pinned; Starlette 1.0 changed `TemplateResponse` signature
- `python-socketio==5.16.1` — ASGI mode for FastAPI; pinned to avoid silent API breakage
- `uvicorn[standard]==0.45.0` — pinned ASGI server
- No Flask, no eventlet (fully migrated to FastAPI/Uvicorn as of v0.7.0)
- tree-sitter bindings must match `tree-sitter>=0.24.0`

## Common Pitfalls

- Do not use `multiprocessing.fork` — scanner uses `spawn` context to avoid deadlocks with Uvicorn
- Do not write files to project root — all output goes to `output/`
- Do not add inline HTML into Jinja2 templates without `escapeHTML` — XSS risk
- Do not create `docs/` subdirectories — keep flat structure
- Do not import from relative paths — always absolute from `src`
