# Architecture

## Vision

**One tool. Every dimension of code health.**

Green-AI is a code intelligence platform that covers the full ESG+S spectrum: Environmental (energy efficiency, carbon intensity), Security (SAST, secrets, dependencies), and Governance (code quality, technical debt, license compliance) — with AI-powered remediation and a single unified dashboard.

> Origin: Started as a Green Software Foundation energy scanner. Evolved to cover the complete ESG surface because no single market tool does it all. The AI-powered fix capability remains the core differentiator.

**Delivery modes (one install, all modes):**
- `green-ai scan` — CLI with `--checks energy|security|quality|dependencies|all`
- `green-ai dashboard` — web UI with ESG score and per-pillar drill-down
- VS Code extension — inline diagnostics and quick-fix for all check categories
- GitHub / GitLab / Jenkins Action — CI/CD gate with configurable thresholds per dimension
- REST API — integrate with any external system

---

## Core Principles

| Principle | Description |
|---|---|
| **Sustainability First** | Every feature is evaluated for its potential to reduce carbon emissions and energy consumption |
| **Developer-Centric** | Tools integrate into existing workflows (CLI, CI/CD, IDE) without friction |
| **Lightweight & Fast** | The tool itself must be efficient — O(n) scanning, multiprocessing, result caching |
| **Transparent & Measurable** | Quantifiable metrics (estimated CO2, energy cost) for every scan |

---

## Pipeline Laws

1. **Latest Stable Only** — All development targets the latest stable Python, dependencies, and toolchain.
2. **Zero Architectural Drift** — Deviations from the defined architecture require formal proposal and approval.
3. **Adversarial Triad Review** — Every task is reviewed for efficiency (OPTIMIZER), security (HARDENER), and atomicity (PRAGMATIST) before Done.
4. **Recursive Density** — Backlog maintains ≥100 Work Units of high-fidelity tasks at all times.

---

## Target System Layout (Phase 3 complete)

```
src/
├── cli/                    # Click CLI application
│   ├── main.py             # CLI group entry point (8 commands)
│   └── commands/           # scan, project, dashboard, standards, calibrate, fix_ai, init, ci, lsp
│
├── core/                   # Core analysis engine
│   ├── scanner/            # Multi-file scanner
│   │   ├── main.py         # ProcessPoolExecutor orchestration
│   │   ├── worker.py       # Isolated per-file scan worker
│   │   └── discovery.py    # File traversal and filtering
│   ├── detectors/          # Language-specific AST detectors
│   │   ├── base_detector.py          # BaseTreeSitterDetector (tree-sitter 0.24+)
│   │   ├── python_detector.py
│   │   ├── javascript_detector.py
│   │   ├── typescript_detector.py
│   │   ├── java_detector.py
│   │   ├── go_detector.py
│   │   └── csharp_detector.py
│   ├── rules.py            # YAML rule loader and registry
│   ├── domain.py           # Pydantic models (Violation, Project, ViolationSeverity)
│   ├── config.py           # Configuration management
│   ├── config_models.py    # Pydantic config schemas
│   ├── analyzer.py         # Complexity and emissions analysis
│   ├── export/             # Report generators (CSV, HTML, PDF, JSON)
│   ├── llm/                # LLM provider abstraction (OpenAI, Ollama, Mock)
│   ├── remediation/        # LibCST-based auto-fix transformers
│   ├── security/           # Rate limiting + security headers middleware
│   ├── telemetry/          # Usage metrics and emissions tracking
│   ├── ci/                 # CI/CD integration (PR comments, exit codes)
│   ├── cache.py            # LRU + disk cache for scan results
│   ├── history.py          # Scan history persistence
│   ├── sca/                # Dependency + license scanning
│   │   ├── manifest_parser.py
│   │   ├── osv_client.py   # OSV.dev CVE lookup
│   │   ├── version_checker.py
│   │   └── license_detector.py
│   ├── quality/            # Code quality + debt
│   │   ├── duplication.py  # Rabin-Karp clone detection
│   │   ├── dead_code.py    # Vulture integration
│   │   └── debt.py         # Remediation effort estimation
│   ├── esg/                # ESG scoring
│   │   └── score_engine.py
│   └── sbom/               # SBOM + SCI
│       └── generator.py
│
├── ui/                     # Web dashboard
│   ├── app_fastapi.py      # FastAPI application (primary entry)
│   ├── server.py           # Uvicorn ASGI server runner
│   ├── state.py            # Global application state
│   ├── schemas.py          # API Pydantic schemas
│   ├── charts.py           # Chart data generation
│   ├── templates/          # Jinja2 HTML templates
│   └── middleware/         # security.py, rate_limit.py
│   └── news/               # News Dashboard Integration
│
├── ide/                    # IDE integrations
│   ├── vscode/             # VS Code extension (TypeScript, v0.1.0)
│   └── lsp/                # pygls Language Server Protocol implementation
│
├── standards/              # Green software standards registry
│   ├── registry.py         # Standards registry
│   └── sources.py          # GSF and ecoCode standard sources
│
└── agents/                 # Autonomous runtime monitoring
    └── runtime_monitor/
```

---

## Scanner Architecture

The scanner uses `ProcessPoolExecutor` with the `spawn` multiprocessing context:

```
scan_files()
  └── ProcessPoolExecutor(max_workers=cpu_count, mp_context=spawn)
        └── executor.map(scan_file_worker, files, chunksize=max(1, n//(cpus*4)))
              └── scan_file_worker() in worker.py
                    ├── Load language detector
                    ├── Run AST queries (tree-sitter 0.25.2)
                    ├── Apply YAML rules
                    └── Return [Violation, ...]
```

**Key decisions:**
- `spawn` context: avoids fork issues with Uvicorn/FastAPI in the parent process
- `max_tasks_per_child=50` (Python ≥3.11): limits memory accumulation per worker
- Chunksize `max(1, total_files // (cpus * 4))`: balances IPC overhead vs. worker starvation
- Result cache: disk-backed LRU prevents re-scanning unchanged files
- Each worker process has its own independent module globals (no shared global state)

---

## Database Architecture

Green-AI has been expanded to support a relational database schema using SQLAlchemy and Alembic. This is currently used for managing logic related to Teams, Users, and Projects.

**Core Entities**:
- `User`: Represents a dashboard user.
- `Team`: Represents an organization or group of users.
- `ProjectDB`: Links a project run configuration directly to a `Team`.
- `TeamMembership`: Manages the many-to-many relationship and roles between `User` and `Team`.

---

## Web Dashboard Architecture

```
Browser (WebSocket + REST)
  └── FastAPI 0.136.0 + Starlette 1.0.0 (app_fastapi.py)
        ├── HTTP Routes: /api/scan, /api/projects, /api/results, /api/charts, /api/calibrate
        ├── WebSocket (python-socketio 5.16.1 ASGI): real-time scan progress
        ├── Jinja2 Templates: dashboard HTML
        └── Middleware: SecurityHeadersMiddleware, RateLimitMiddleware
              └── Served by Uvicorn 0.45.0 (ASGI)
```

**Stack:** FastAPI + Uvicorn (ASGI) + python-socketio 5.16.1  
**Replaced:** Flask + eventlet (fully migrated in v0.7.0)

### Starlette 1.0 Template API

`TemplateResponse` signature changed in Starlette 1.0.0. Always use keyword args:

```python
# Starlette 1.0+ (correct)
templates.TemplateResponse(request=request, name="page.html", context={"key": value})

# Pre-1.0 (broken — causes TypeError: unhashable type: 'dict')
templates.TemplateResponse("page.html", {"request": request, "key": value})
```

---

## LLM Integration

```
fix_ai command
  └── RemediationEngine
        ├── Scan violations → [Violation, ...]
        ├── Select LLMProvider (OpenAI | Ollama | Mock)
        ├── TokenBucketRateLimiter (TPM + RPM enforcement)
        ├── Send prompt → receive fix suggestion
        ├── Apply via LibCST transformer
        └── Show colored diff for user approval
```

Provider abstraction allows switching between OpenAI, self-hosted Ollama, or mock (for tests) via `.green-ai.yaml`.

---

## Security Architecture

All API endpoints that accept user-controlled file paths must validate against the project root:

```python
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent.parent
resolved = Path(user_file_param).resolve()

if not str(resolved).startswith(str(project_root)):
    raise HTTPException(status_code=400, detail="File path outside project root")
```

Additional layers:
- `SecurityHeadersMiddleware`: CSP, HSTS, X-Frame-Options, X-Content-Type-Options
- `RateLimitMiddleware`: 100 requests/60s per IP
- Pydantic validators on all API request bodies
- `escapeHTML` enforced in all Jinja2 templates for user-provided content

---

## Deployment

### Docker

```bash
docker build -t green-ai:latest .
docker-compose up   # http://localhost:5000
```

Multi-stage build: `python:3.12-slim` → minimal runtime image.

### Kubernetes

```bash
kubectl apply -f deploy/kubernetes/deployment.yaml
kubectl apply -f deploy/kubernetes/service.yaml
kubectl apply -f deploy/kubernetes/ingress.yaml
kubectl apply -f deploy/kubernetes/hpa.yaml
```

HPA scales on CPU utilization. Liveness and readiness probes configured.

### Helm

```bash
helm install green-ai ./deploy/helm/green-ai -f custom-values.yaml
```

---

## Architectural Decisions

### ADR-001: Pydantic-Core Version Pin (2024-05-24)

**Decision:** Pin `pydantic-core==2.41.5` exactly.  
**Reason:** `pydantic 2.12.5` (highest available) requires exactly `pydantic-core==2.41.5`. Upgrading to `2.42.0` causes unresolvable pip conflicts.  
**Status:** Active. Monitor pydantic releases for resolution.

### ADR-002: Multiprocessing Spawn Context (PERF-005)

**Decision:** Use `mp_context='spawn'` for `ProcessPoolExecutor` in the scanner.  
**Reason:** `fork` inherits Uvicorn's file descriptors and thread state, causing deadlocks. `spawn` starts a clean process. Validated on Python 3.11+.  
**Status:** Implemented in `src/core/scanner/main.py`.

### ADR-003: FastAPI over Flask (v0.7.0)

**Decision:** Fully replace Flask + eventlet with FastAPI + Uvicorn + python-socketio ASGI.  
**Reason:** eventlet monkey-patches stdlib, conflicting with multiprocessing. FastAPI is type-safe, async-native, and better maintained.  
**Status:** Complete. Flask removed from requirements.txt.

### ADR-004: LibCST for Code Remediation

**Decision:** Use LibCST (not standard `ast`) for Python auto-fix transformers.  
**Reason:** LibCST preserves whitespace, comments, and formatting — producing diffs safe to apply without destroying code style.  
**Status:** Implemented in `src/core/remediation/`.

### ADR-005: Pin Web Framework Versions (2026-04-22)

**Decision:** Pin `fastapi==0.136.0`, `starlette==1.0.1`, `uvicorn==0.45.0`, `python-socketio==5.16.1`.
**Reason:** Starlette 1.0.0 changed `TemplateResponse` signature, silently breaking 8 tests on fresh install. Unpinned framework deps are a reliability risk. Updated to `1.0.1` to fix URL spoofing vulnerability.
**Status:** Added to `requirements.txt`. See BUG-004 and BUG-022 in backlog.

### ADR-006: Security Enforcements (2026-06-08)

**Decision:** Enforce security configurations universally.
**Reason:** Several configurations defaulted to insecure options (Bandit B501, B701, B324). `requests.get` now enforces `verify=True`, `Jinja2` environments use `autoescape=select_autoescape`, and MD5 hashes used for non-security caches explicitly specify `usedforsecurity=False` for FIPS-compliance.
**Status:** Implemented across `src/standards`, `src/core/export`, and cache implementations. See BUG-024, BUG-025, BUG-026 in backlog.

### ADR-007: LLM Auto-Fix Context Architecture (ANALYSIS-001a)

**Decision:** Use `tree-sitter` to extract pruned AST scope snippets before sending to LLM. Provide byte-slice surgical replacement for non-Python languages and use `LibCST` for Python.
**Reason:** Passing raw source files exceeds token limits and context windows. `LibCST` ensures 100% safe replacements without breaking styles but only supports Python, thus a hybrid approach is necessary.
**Status:** Feasibility verified. Pending implementation.

### ADR-008: Dynamic External Rule Syncing (ANALYSIS-002a, 002b)

**Decision:** Download bulk OSV data dumps via cron job and sync GSF/ecoCode rules using authenticated GitHub APIs, caching them in a relational DB (`standard_sources`, `rules`, `rule_overrides`).
**Reason:** Avoids rate limits during scans and allows local caching. Database schema supports multi-tenant organization customizations.
**Status:** Feasibility verified. Pending implementation.

### ADR-009: Organization-Level Rule Hierarchy (ANALYSIS-003a)

**Decision:** Implement a deep-merge configuration resolver with precedence: Local (`.green-ai/suppress.yaml`) > Project (DB/yaml) > Organization (DB) > Global (Engine DB).
**Reason:** Fulfills the "truly customizable product" requirement, allowing admins and users to tailor standard rules without modifying the global cached source.
**Status:** Feasibility verified. Pending implementation.

### ADR-010: Git Blame Dashboard Integration (ANALYSIS-004a)

**Decision:** Use in-process `pygit2` to perform file-level batch blame lookups at the end of AST scans, attaching `author`, `author_email`, and `commit_date` to `Violation` models.
**Reason:** Shelling out to `git blame` per violation is too slow. `pygit2` enables fast in-memory execution, allowing the SonarQube-style dashboard to filter by Git metadata efficiently.
**Status:** Feasibility verified. Pending implementation.
