# Backlog

**Phase:** 2 — Action & Expansion  
**Milestone:** M1 — Stability Gate  
**Gate:** 0 lint errors | 95% test coverage | Build pass  
**Health:** Green | State: S4 GATED_RELEASE  
**Test suite:** 597 passed, 2 skipped, 0 failed (flake8: 0 errors)

---

## Bug Hunt — HIGH PRIORITY

Findings from automated audit against the live codebase (2026-04-22).

| ID | Severity | File | Description | Status |
|---|---|---|---|---|
| BUG-001 | CRITICAL | `src/ui/app_fastapi.py:142,159` | Starlette 1.0.0 broke `TemplateResponse` — `request` must be first kwarg, not inside context dict. Caused 8 test failures. | **FIXED** |
| BUG-002 | HIGH | `requirements.txt` | `pip==26.0.1` pinned — causes hard failure on fresh `pip install` ("Cannot uninstall pip, RECORD file not found"). Pip should never be pinned in requirements.txt. | **FIXED** |
| BUG-003 | HIGH | `requirements.txt` | `flask` listed as dependency but has zero imports in `src/` (migration to FastAPI complete in v0.7.0). Dead dependency risks transitive conflicts. | **FIXED** |
| BUG-004 | HIGH | `requirements.txt` | `fastapi`, `starlette`, `uvicorn`, `python-socketio` all unpinned. Root cause of BUG-001 — silent upgrades break the API. | **FIXED** — pinned to `fastapi==0.136.0`, `starlette==1.0.0`, `uvicorn==0.45.0`, `python-socketio==5.16.1` |
| BUG-005 | HIGH | `src/ui/app_fastapi.py:501` | `api_remediation_preview` accepts a `file` query param and opens it directly with no path validation — path traversal vulnerability (e.g. `file=../../etc/passwd`). | **FIXED** — resolved path validated against project root |
| BUG-006 | MEDIUM | `CLAUDE.md`, `docs/standards.md` | Documents stated `python-socketio==2.0.1` but 5.16.1 is installed. Stale constraint misled dependency management. | **FIXED** — updated to 5.16.1 |
| BUG-007 | LOW | `tests/` warnings | `websockets.legacy` deprecation warnings from uvicorn's websocket implementation appear in test output. Upstream issue; track uvicorn releases for fix. | OPEN |

### False Positives (investigated and dismissed)

| Claim | Reason Dismissed |
|---|---|
| "Missing None check on rule in worker.py" | `if rule:` guard on line 69 covers this |
| "Race condition on `_disk_cache_instance`" | `spawn` context gives each worker its own module globals |
| "Unsafe access to `choices[0]`" | Caught by `except (KeyError, IndexError)` at line 104 |
| "Tree-sitter API incompatibility" | base_detector.py handles all init patterns for 0.24+ |
| "Asyncio thread bug in lifespan" | `run_coroutine_threadsafe` pattern is correct and safe |

---

## Active Epics

### EPIC-09: IDE Plugins

**Goal:** Full VS Code extension with LSP diagnostics and quick fixes.

| Task | Spec | Status |
|---|---|---|
| IDE-001 | Initialize VS Code extension scaffold in `src/ide/vscode/` using `yo code`. Configure `package.json` with the `green-ai` command. | TODO |
| IDE-002 | Implement base `pygls` `LanguageServer` instance in `src/ide/lsp/server.py` supporting stdio communication. | DONE |
| IDE-003 | Implement `initialize` request handler in `LanguageServer` defining `TextDocumentSyncKind.Incremental` capabilities. | DONE |
| IDE-004 | Implement `didOpen`, `didChange`, `didSave` handlers bridging LSP events to the internal scanner API. | DONE |
| IDE-005 | Map scanner `Violation` objects to LSP `Diagnostic` objects and publish via `LanguageServer.publish_diagnostics`. | DONE |
| IDE-006 | Connect scanner CLI as a wrapper for the LSP server. | DONE |
| IDE-007 | Define TextMate grammar for `.gairule` files in `src/ide/vscode/syntaxes/`. | DONE |
| IDE-008 | Implement `textDocument/codeAction` handler providing quick fixes for detected violations. | DONE |
| IDE-009 | Add `green-ai.scanner` configuration section in `package.json` (LSP server path, strictness level). | DONE |
| IDE-010 | Implement `window/logMessage` reporting scan progress to an output channel. | DONE |

**Remaining:** IDE-001 (VS Code scaffold)

---

### EPIC-12: Team Collaboration Dashboard

**Goal:** Multi-user team management with RBAC, aggregated metrics, and email summaries.

| Task | Spec | Status |
|---|---|---|
| TEAM-001a | Create SQLAlchemy `Base` and `Engine` setup in `src/core/telemetry/database.py`. | TODO |
| TEAM-001b | Create SQLAlchemy `Team` and `TeamMember` models in `src/core/telemetry/models.py`. | TODO |
| TEAM-002 | Add `POST /api/teams` and `GET /api/teams` endpoints in `app_fastapi.py` using Pydantic schemas. | TODO |
| TEAM-003 | Implement `Role` dependency in `src/ui/middleware/auth.py` mapping Viewer/Editor roles to endpoints. | TODO |
| TEAM-004 | Create `src/ui/templates/team_dashboard.html` rendering team-specific charts via Chart.js. | TODO |
| TEAM-005 | Add `TelemetryService.get_team_metrics(team_id)` aggregating `ScanMetrics` across team projects. | TODO |
| TEAM-006 | Add `GET /api/teams/{id}/history` returning time-series violation counts for trend charts. | TODO |
| TEAM-007 | Add OAuth2 password flow to authenticate users and attach `team_id` to requests. | TODO |
| TEAM-008 | Create weekly CRON script generating PDF reports and sending via `smtplib`. | TODO |
| TEAM-009 | Add `tests/api/test_teams.py` using `TestClient` verifying CRUD and RBAC enforcement. | TODO |
| TEAM-010 | Update `docs/architecture.md` with team features and metric aggregation behavior. | TODO |

**Risk:** TEAM-001 and TEAM-007 are HIGH-RISK — requires DB schema migration design review before starting.

---

### EPIC-13: Machine Learning Pattern Recognition

**Goal:** ONNX-based ML detector for code inefficiency with regex fallback.

| Task | Spec | Status |
|---|---|---|
| ML-001 | Create `src/scripts/scrape_dataset.py` extracting commits labeled `refactor(perf)` as training data. | TODO |
| ML-002 | Define PyTorch Transformer model in `src/ml/model.py` mapping tokenized ASTs to efficiency labels. | TODO |
| ML-003 | Create `src/ml/train.py` handling batching, loss calculation, and epoch tracking. | TODO |
| ML-004 | Implement cross-validation in `src/ml/eval.py` reporting F1-score on test split. | TODO |
| ML-005 | Add `src/ml/export.py` calling `torch.onnx.export` to convert trained model. | TODO |
| ML-006 | Add `onnxruntime` dependency and implement `MLDetector` in `src/core/detectors/ml.py`. | TODO |
| ML-007 | Wrap `MLDetector.scan()` with exception handler falling back to `RegexDetector` on inference failure. | TODO |
| ML-008 | Add `--enable-ml` flag to `src/cli/commands/scan.py` passing option to `GreenAIConfig`. | TODO |
| ML-009 | Add `tests/ml/test_inference.py` verifying ONNX model outputs deterministic labels for known patterns. | TODO |
| ML-010 | Update `docs/architecture.md` with ML training pipeline and ONNX integration section. | TODO |

---

### EPIC-14: Rust Language Support

**Goal:** Full Rust scanning via tree-sitter with 3 core efficiency rules.

| Task | Spec | Status |
|---|---|---|
| RUST-001 | Add `tree-sitter-rust` to `requirements.txt` and `Language.build_library` in `src/core/scanner/parser.py`. | TODO |
| RUST-002 | Implement `RustASTDetector` inheriting `BaseTreeSitterDetector` with Rust node type mapping. | TODO |
| RUST-003 | Write tree-sitter query matching explicit `.clone()` calls within loop bodies. | TODO |
| RUST-004 | Write tree-sitter query detecting `String::new()` or `vec![]` inside `for`/`while` loops. | TODO |
| RUST-005 | Write tree-sitter query finding `.unwrap()` calls directly enclosed by loop constructs. | TODO |
| RUST-006 | Add `tests/detectors/test_rust.py` executing AST queries against mock inefficient Rust source strings. | TODO |
| RUST-007 | Update `src/core/scanner/discovery.py` to include `.rs` file extensions during traversal. | TODO |
| RUST-008 | Create sample Cargo project in `tests/fixtures/rust_app` and run E2E scan. | TODO |
| RUST-009 | Update README and `docs/roadmap.md` to reflect Rust support availability. | TODO |
| RUST-010 | Bump minor version and generate release note for Rust Beta. | TODO |

---

### EPIC-18: System Audit & Hardening

**Goal:** Close remaining security gaps and expand automated security testing.

| Task | Spec | Status |
|---|---|---|
| AUDIT-001 | Improve exception handling in `/api/scan` and global handlers to prevent state leakage. | DONE |
| AUDIT-002 | Ensure all `innerHTML` usages use `escapeHTML` across dashboard templates. | DONE |
| AUDIT-003 | Create security tests in `tests/security/` covering all dynamic fields that render user-provided content (XSS, injection). | TODO |
| AUDIT-004 | Replace native browser `alert()` with toast notifications in the dashboard. | DONE |
| AUDIT-005 | Add path traversal tests for `GET /api/remediation/preview` (verifies `file` param restricted to project root). | TODO |
| AUDIT-006 | Audit all remaining `Query(...)` file/path parameters across API endpoints for path traversal. | TODO |

---

## Completed Epics (Vaulted)

| Epic | Completion |
|---|---|
| EPIC-00: Stability Gate (deps, deprecations) | v0.9.2 |
| EPIC-01: Java Language Support | v0.7.0 |
| EPIC-02: Go Language Support | v0.7.0 |
| EPIC-03: LLM Integration (autonomous fixer) | v0.8.0 |
| EPIC-04: Advanced Reporting (HTML, CSV, PDF, JSON) | v0.8.0 |
| EPIC-05: CI/CD GitHub Action V2 | v0.8.0 |
| EPIC-06: Performance Optimization (multiprocessing) | v0.8.0 |
| EPIC-07: Security Hardening (OWASP, entropy, headers) | v0.8.0 |
| EPIC-08: Telemetry & Metrics | v0.8.0 |
| EPIC-10: Configuration Management | v0.8.0 |
| EPIC-11: Cloud-Native Deployment (K8s, Helm) | v0.9.3 |
| EPIC-15: C# Language Support | v0.9.0 |
| EPIC-15: Autonomous Architecture & Doc Engine | Done |
| EPIC-16: Technical Debt (PERF-005 resolution) | Done |
| EPIC-17: PERF-005 Architecture Verification | Done |

---

## Blockers

| ID | Description | Resolution |
|---|---|---|
| BLOCK-001 | AUDIT-003/005/006 security tests not yet written | Start with remediation_preview path traversal test |
| BLOCK-002 | TEAM-001 needs DB migration design review | Requires schema review before any TEAM-* work starts |
| BLOCK-003 | OWASP gaps: A01, A02, A07, A08, A10 | Addressed in Phase 3 roadmap |
| BLOCK-004 | BUG-007: websockets.legacy deprecation in test output | Upstream uvicorn issue; track release |

---

## Work Units Available

| State | Count |
|---|---|
| Bug fixes TODO | 2 (AUDIT-005, AUDIT-006) |
| Active TODO tasks | 32 |
| In progress | 0 |
| Done (this milestone) | 7 (BUG-001–006 + AUDIT-004) |

Minimum 100 WU must be available per session. Expand epics when density drops below threshold.
