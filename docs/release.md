# Release Notes

## Health

| Metric | Target | Current |
|---|---|---|
| Version | — | v0.9.1 |
| Phase | — | 2 — Action & Expansion |
| State | — | S4 GATED_RELEASE |
| Buffer | — | Green |
| Cleanliness Score | ≥94% | 94% |
| Test Suite | 597 pass / 0 fail | 597 passed, 2 skipped |
| Lint (flake8) | 0 errors | 0 errors |
| API Parity | 100% | 100% |
| Mock Coverage | 100% | 100% |

### Installed Runtime Versions (locked)

| Package | Version |
|---|---|
| Python | 3.11.x |
| fastapi | 0.136.0 |
| starlette | 1.0.0 |
| uvicorn | 0.45.0 |
| python-socketio | 5.16.1 |
| pydantic | 2.12.5 |
| pydantic-core | 2.41.5 |
| tree-sitter | 0.25.2 |
| pygls | 2.0.1 |
| websockets | 16.0 |

---

## Bug Hunt Fixes (2026-04-22)

- **BUG-001 (CRITICAL):** Fixed `TemplateResponse` call signature broken by Starlette 1.0.0. `request` is now the first kwarg; removed from context dict. Restored 8 failing tests.
- **BUG-002 (HIGH):** Removed `pip==26.0.1` from `requirements.txt` — pip must not be application-pinned.
- **BUG-003 (HIGH):** Removed `flask` from `requirements.txt` — zero usages since FastAPI migration in v0.7.0.
- **BUG-004 (HIGH):** Pinned `fastapi==0.136.0`, `starlette==1.0.0`, `uvicorn==0.45.0`, `python-socketio==5.16.1` to prevent future silent upgrade breakage.
- **BUG-005 (HIGH):** Fixed path traversal in `GET /api/remediation/preview` — `file` query param now validated against project root via `Path.resolve()`.
- **BUG-006 (MEDIUM):** Updated CLAUDE.md and `docs/standards.md` to reflect correct `python-socketio==5.16.1` version.

---

## [v0.9.3] — Patch Release

- Go performance benchmarks (GO-009, GO-010)
- Dependency upgrades: bump all to latest stable (SEC-002)
- OWASP Top 10 mapping review (SEC-008)
- Kubernetes deployment manifests: Deployment, Service, Ingress, HPA, probes (CLD-002–004, CLD-007–010)
- Integration tests for Kubernetes deployment

---

## [v0.9.2] — Patch Release

- Parallel processing: multiprocessing pool tuning with spawn context (PERF-005)
- CI/CD pipeline for automated Docker image push (CLD-006)
- **EPIC-00 Stability Gate complete:**
  - Resolved FastAPI `on_event` deprecation (STAB-001)
  - Updated greenlet, lsprotocol, playwright, pydantic_core, pyee, pygls, pip (STAB-002–008)
- CI/CD marketplace documentation (CI-010)

---

## [v0.9.1] — Stability & Quality Pass

- Cleanliness Score: 94%
- Removed `on_event` FastAPI deprecation warning
- Removed unused attributes/variables from `src/core/config_models.py` via Vulture
- Toast notifications replacing native browser alerts (AUDIT-004)
- FastAPI exception handling hardened to prevent state leakage (AUDIT-001)
- XSS vulnerabilities fixed: `escapeHTML` enforced across all dashboard templates (AUDIT-002)
- VS Code extension foundation: TextMate grammar, quick fix provider, settings page, output channel (IDE-007–010)

---

## [v0.9.0] — Backlog Provisioning

- PDF chart rendering (REP-003)
- Go benchmarks (GO-009, GO-010)
- LSP CLI wrapper (IDE-006)
- Helm chart (CLD-001)
- Docker Compose local development (CLD-005)
- C# language support: tree-sitter, detector, 5 rules, tests (CS-001–006)

---

## [v0.8.0] — CI/CD, Telemetry & Performance

- **EPIC-03 LLM Integration:** Interface, OpenAI provider, rate limiting, cost tracking, `fix-ai` CLI, prompt engineering, security review (LLM-001–019)
- **EPIC-04 Reporting:** PDF (WeasyPrint), CSV improvements, HTML interactive charts, JSON schema (REP-001–015)
- **EPIC-05 CI/CD GitHub Action:** Docker action, `action.yml`, PR comment bot, fail-on threshold (CI-001–010)
- **EPIC-06 Performance:** cProfile, multiprocessing, chunk tuning, generator review, LRU + disk cache (PERF-001–010)
- **EPIC-07 Security:** pip-audit, input sanitization, secrets detection (entropy + hardcoded), security headers, rate limiting (SEC-001–010)
- **EPIC-08 Telemetry:** Data schema, local storage, opt-in CLI, metric collection, dashboard tab, anonymization (TEL-001–010)
- **EPIC-10 Config:** Remote config, severity overrides, JSON schema validation, deep merge, `init` command (CFG-001–010)
- FastAPI/Uvicorn migration complete (replacing Flask + eventlet)
- LibCST remediation engine: 4 transformers (loop, context manager, enumerate, comprehension)
- Scanner refactored to modular package (`scanner/main.py`, `worker.py`, `discovery.py`)

---

## [v0.7.0] — Consolidation & Quality

- **EPIC-01 Java:** AST parser, rule engine, 4 rules, test suite
- **EPIC-02 Go:** tree-sitter-go, detector, 3 rules (`formatted_print`, `empty_block`, `infinite_loop`, `string_concatenation_in_loop`), E2E tests
- TypeScript support with `any_type_usage` and `prefer_const_enum` rules
- 3 new Python rules: `unnecessary_comprehension`, `numpy_sum_vs_python_sum`, `subprocess_run_without_timeout`
- 2 new JS rules: `console_time`, `inner_html`
- Standards sync from remote GSF and ecoCode sources
- Pre-commit hooks enhanced
- Flask → FastAPI migration complete

---

## [v0.6.x] — Architecture & Security

- Modular detector package (`src/core/detectors/`)
- New Python rules: blocking I/O in async, SQL injection risk, requests timeout, empty blocks
- JS empty block detection
- GitHub Actions CI/CD workflow
- JavaScript AST engine replacing legacy regex (v0.6.1)
- 7 new Python rules including `string_concatenation_in_loop`, `inefficient_dictionary_iteration` (v0.6.0)
- Multiprocessing scanner (v0.6.0)

---

## [v0.5.0-beta]

- Dynamic YAML rule system
- Advanced AST detection (redundant computations in loops)
- Centralized logging to `output/logs/app.log`
- Self-scan bottleneck reduced ~85%

---

## [v0.4.0]

- Multi-project support
- CSV and HTML export
- Git URL scanning
- Web dashboard

---

## [v0.3.0]

- `.green-ai.yaml` configuration system
- Rule enable/disable via config or CLI
- Initial `scan` CLI command

---

## [v0.1.0]

- Core AST scanner: Python and JavaScript
- Basic CO2 impact estimation
