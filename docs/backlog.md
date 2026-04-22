# Backlog

**Active Phase:** 2 — Action & Expansion (v0.9.x)  
**Next Phase:** 3 — Security, Quality & ESG (v1.0.x)  
**Gate:** 0 lint errors | 95% test coverage | Build pass  
**Health:** Green | State: S4 GATED_RELEASE  
**Test suite:** 597 passed, 2 skipped, 0 failed (flake8: 0 errors)

> **Vision:** One tool — Environmental (energy/carbon) + Security (SAST/secrets/SCA) + Governance (quality/debt/license) + AI Fix. Single CLI, VS Code, CI/CD, and Dashboard. No other tool in the market combines all four dimensions.

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

---

---

# Phase 3 Epics — Security, Quality & ESG (v1.0.x)

> These epics implement the expanded vision. All are additive — they extend the existing scanner without replacing Phase 2 work.

---

## EPIC-19: SAST Security Expansion (OWASP Top 10)

**Goal:** Make Green-AI a credible SAST tool covering OWASP Top 10 across all 6 languages.  
**Market gap:** Current tool only catches `eval`, `innerHTML`, and `document.write`. SonarQube and Semgrep cover full OWASP/CWE. We need parity.

| Task | Spec | Lang | OWASP | Status |
|---|---|---|---|---|
| SEC-101 | Detect SQL injection: f-string/format in `cursor.execute()`, string concat in ORM queries. Rule `sql_injection`. | Python, Java | A03 | TODO |
| SEC-102 | Detect command injection: `subprocess.run(shell=True)` with variable input, `os.system()` with concatenation. Rule `command_injection`. | Python, Go | A03 | TODO |
| SEC-103 | Detect path traversal: user-controlled input in `open()`, `Path()`, `os.path.join()` without `.resolve()` guard. Rule `path_traversal`. | Python, JS, Java | A01 | TODO |
| SEC-104 | Detect SSRF: user-controlled URL in `requests.get()`, `urllib.request.urlopen()`, `http.get()`. Rule `ssrf_risk`. | Python, JS | A10 | TODO |
| SEC-105 | Detect insecure deserialization: `pickle.loads()`, `yaml.load()` without `Loader=`, `marshal.loads()`. Rule `insecure_deserialization`. | Python | A08 | TODO |
| SEC-106 | Detect XXE: XML parsing without `defusedxml`, `etree.fromstring()` without disable-entity flag. Rule `xxe_risk`. | Python, Java | A05 | TODO |
| SEC-107 | Detect broken auth patterns: hardcoded credentials in source, `JWT` decode without verification, weak algorithm (`HS256` with short key). Rule `broken_auth`. | Python, JS, Java | A07 | TODO |
| SEC-108 | Detect insecure cryptography: MD5/SHA1 for security hashing, `DES`/`RC4` cipher use, ECB mode. Rule `weak_crypto`. | Python, Java, Go, C# | A02 | TODO |
| SEC-109 | Detect insecure random: `random.random()` or `Math.random()` used for security tokens. Rule `insecure_random`. | Python, JS, TS | A02 | TODO |
| SEC-110 | Add CWE ID mapping to all security rules in YAML. Update `docs/api/swagger.yaml` with `cwe_id` field on Issue schema. | All | — | TODO |
| SEC-111 | Write `tests/security/test_sast_owasp.py` — one test per rule, using fixture files with known-vulnerable code patterns. | All | — | TODO |
| SEC-112 | Add `--checks security` CLI flag to run only security rules. Update `.green-ai.yaml` with `checks:` key (energy, security, quality, all). | CLI | — | TODO |

---

## EPIC-20: Secret Scanning v2

**Goal:** Replace weak entropy+keyword detection with a proven pattern library (GitLeaks-parity).  
**Market gap:** Current implementation: 13 keyword patterns + Shannon entropy threshold. GitLeaks has 100+ proven patterns. TruffleHog has entropy tuning. We need both.

| Task | Spec | Status |
|---|---|---|
| SEC-201 | Implement `src/core/detectors/secrets_detector.py` — dedicated secret scanner separate from language detectors. Operates on raw file text (not AST). | TODO |
| SEC-202 | Add 50+ regex patterns for: AWS keys/secrets, GCP service account JSON, Azure connection strings, GitHub/GitLab tokens, Stripe API keys, Twilio, SendGrid, Slack webhooks, Heroku, npm tokens, PyPI tokens. Store in `rules/secrets.yaml`. | TODO |
| SEC-203 | Add patterns for: RSA/PEM private keys, SSH private keys, JWT tokens (full `eyJ...` format), PKCS8 keys, PGP blocks. | TODO |
| SEC-204 | Tune entropy thresholds per secret type (high-entropy strings in base64 namespace get lower threshold than hex). Make configurable in `.green-ai.yaml`. | TODO |
| SEC-205 | Implement verification layer: before reporting, attempt lightweight validation (e.g. AWS key format check, not actual API call) to reduce false positives. | TODO |
| SEC-206 | Add git history scanning: `green-ai scan --git-history ./repo` walks all commits, applies secrets_detector to each diff. | TODO |
| SEC-207 | Add `--checks secrets` CLI flag. | TODO |
| SEC-208 | Write `tests/security/test_secrets_detector.py` with known-positive and known-negative fixtures for each pattern group. Coverage ≥95%. | TODO |

---

## EPIC-21: Dependency & SCA Scanning

**Goal:** Parse dependency manifests, detect known CVEs via OSV.dev (free, open API), flag outdated packages, detect license issues.  
**Market gap:** Snyk is paid and cloud-only. `pip-audit` is Python-only. We can offer multi-language SCA in one tool.

| Task | Spec | Status |
|---|---|---|
| SCA-001 | Implement `src/core/sca/manifest_parser.py` — parse `requirements.txt`, `Pipfile`, `pyproject.toml`, `package.json`, `package-lock.json`, `go.mod`, `go.sum`, `pom.xml`, `*.csproj`. Extract: package name, pinned version, language. | TODO |
| SCA-002 | Implement `src/core/sca/osv_client.py` — query `https://api.osv.dev/v1/query` for each dependency. Cache results (24h TTL). Map OSV response to `Violation` with CVE ID, CVSS score, severity, fix version. | TODO |
| SCA-003 | Implement `src/core/sca/version_checker.py` — compare pinned version against latest on PyPI/npm/pkg.go.dev. Flag packages >2 major versions behind as `outdated_dependency`. | TODO |
| SCA-004 | Implement `src/core/sca/license_detector.py` — detect package licenses from PyPI metadata / npm package.json `license` field. Flag copyleft licenses (GPL, AGPL, LGPL) that may conflict with commercial use. | TODO |
| SCA-005 | Integrate SCA results into `Violation` schema with new category field `category: dependency`. Wire into main scan flow and dashboard. | TODO |
| SCA-006 | Add `--checks dependencies` CLI flag. Add `sca:` section to `.green-ai.yaml` config (enable/disable, license-policy: allow/deny list). | TODO |
| SCA-007 | Add SCA results to all export formats (CSV column, JSON array, HTML table section, PDF section). | TODO |
| SCA-008 | Write `tests/sca/test_manifest_parser.py`, `test_osv_client.py` (mock API), `test_license_detector.py`. Coverage ≥95%. | TODO |

---

## EPIC-22: Code Quality & Technical Debt Engine

**Goal:** Add SonarQube-class code quality metrics: duplication, cognitive complexity, dead code, method/class size limits.  
**Market gap:** Current `analyzer.py` computes basic cyclomatic complexity and LOC. SonarQube measures cognitive complexity, duplication, class coupling, method length. CodeClimate estimates debt hours. We need depth.

| Task | Spec | Status |
|---|---|---|
| QUAL-001 | Implement cognitive complexity scoring in `src/core/analyzer.py`. Cognitive complexity differs from cyclomatic — it counts structural increments (nested loops add more than flat loops). Algorithm: Sonar cognitive complexity spec. | TODO |
| QUAL-002 | Implement duplicate code detection in `src/core/quality/duplication.py`. Tokenize files, use rolling hash (Rabin-Karp) to find Type-1 clones (exact) and Type-2 clones (renamed variables). Threshold: ≥6 lines duplicated. | TODO |
| QUAL-003 | Implement dead code detection by integrating `vulture` as a library call (not subprocess) in `src/core/quality/dead_code.py`. Report unused functions, classes, variables as `dead_code` violations. | TODO |
| QUAL-004 | Implement method length rule: functions > 50 lines → minor violation; > 100 lines → major. Class size: > 300 lines → major. Parameters: > 7 → minor. Add as YAML rules in `rules/quality.yaml`. | TODO |
| QUAL-005 | Implement technical debt scoring in `src/core/quality/debt.py`. Assign remediation minutes per violation category: security=30min, energy=15min, quality=10min, duplicate=5min/dup-block. Aggregate to `debt_hours` per file and project. | TODO |
| QUAL-006 | Add `--checks quality` CLI flag. Add `quality:` section to `.green-ai.yaml`. | TODO |
| QUAL-007 | Expose `GET /api/quality` endpoint returning per-file complexity, duplication, debt metrics. Update `docs/api/swagger.yaml`. | TODO |
| QUAL-008 | Write `tests/quality/test_duplication.py`, `test_dead_code.py`, `test_debt_scoring.py`. Coverage ≥95%. | TODO |

---

## EPIC-23: ESG Score Engine

**Goal:** Compute a single, explainable ESG score (0–100) from scan results. This is the headline metric — what a CTO or sustainability lead wants to see.

**Score formula (proposed):**
```
E-score = 100 − (energy_violations_weighted / files * 100)  [max penalty 40pts]
S-score = 100 − (security_score_weighted)                   [max penalty 40pts]
G-score = 100 − (debt_hours_normalized + dup_pct)          [max penalty 20pts]
ESG = 0.4×E + 0.4×S + 0.2×G  (weights configurable)
```

| Task | Spec | Status |
|---|---|---|
| ESG-001 | Implement `src/core/esg/scorer.py` — `ESGScorer.compute(scan_results) → ESGScore`. `ESGScore` Pydantic model: `e_score`, `s_score`, `g_score`, `total`, `grade` (A–F), `breakdown` dict. | TODO |
| ESG-002 | Calibrate weights against 10 real open-source repos. Document methodology in `docs/architecture.md`. Weights configurable via `.green-ai.yaml` `esg.weights:` key. | TODO |
| ESG-003 | Add `GET /api/esg` endpoint returning ESGScore for current project. | TODO |
| ESG-004 | Add ESG score to all export formats (CSV column, JSON top-level, HTML header badge, PDF cover page). | TODO |
| ESG-005 | Write `tests/esg/test_scorer.py`. Coverage ≥95%. | TODO |

---

## EPIC-24: Unified Dashboard Redesign

**Goal:** Redesign the dashboard from a single-category energy view to a 4-pillar ESG+AI view. This is the product's face — what users and managers see.

| Task | Spec | Status |
|---|---|---|
| DASH-001 | New landing page layout: ESG score badge (large, centre), 4 drill-down cards (Energy, Security, Quality, AI Fix queue), recent scans timeline, project switcher. | TODO |
| DASH-002 | Energy pillar view: current rules violations, carbon score, SCI value, per-file emissions heatmap, trend chart. | TODO |
| DASH-003 | Security pillar view: OWASP coverage heatmap (A01–A10), secret findings (masked), dependency CVE table (sortable by CVSS), critical/high count badge. | TODO |
| DASH-004 | Quality pillar view: cognitive complexity per file (sortable), duplication map, technical debt (hours), dead code list. | TODO |
| DASH-005 | AI Fix queue: list of all violations with available LLM fix. One-click apply. Show diff in modal. Status: pending / applied / rejected. | TODO |
| DASH-006 | Policy gate panel: show which CI checks would pass/fail at current state. Threshold sliders for each dimension. | TODO |
| DASH-007 | Update `docs/api/swagger.yaml` with all new endpoints from EPIC-19–24. Update `docs/api/mock_data.json`. | TODO |
| DASH-008 | Write E2E tests in `tests/e2e/` using Playwright for all new dashboard views. | TODO |

---

## EPIC-25: Custom Rules Engine

**Goal:** Let users define their own rules in YAML without touching source code. This directly competes with Semgrep's community rules model.

| Task | Spec | Status |
|---|---|---|
| RULE-001 | Extend YAML rule schema to support: `pattern_type: regex \| ast_query \| semgrep_compat`. Add `test_cases:` field with positive/negative examples. | TODO |
| RULE-002 | Implement `src/core/rules/validator.py` — validate user-provided rule YAML against schema before loading. Report schema errors with line numbers. | TODO |
| RULE-003 | Implement `src/core/rules/user_rules_loader.py` — load rules from `.green-ai/rules/*.yaml` in project directory. Merge with built-in rules, user rules take precedence. | TODO |
| RULE-004 | Add `green-ai rules test <rule.yaml>` CLI command — runs rule against its `test_cases` and reports pass/fail. | TODO |
| RULE-005 | Add `green-ai rules publish` CLI command — validate, package, and POST to rule registry API (future). Stub for now. | TODO |
| RULE-006 | Write `tests/rules/test_custom_rules.py`. Coverage ≥95%. | TODO |

---

## EPIC-26: Baseline & Suppression

**Goal:** Let teams accept existing violations as baseline (technical debt acknowledged) and suppress false positives. Prerequisite for adoption in brownfield codebases.

| Task | Spec | Status |
|---|---|---|
| BASE-001 | Implement `green-ai baseline create` — scan, write current violations to `.green-ai/baseline.json` (violation fingerprint: file hash + rule_id + line). | TODO |
| BASE-002 | Implement baseline comparison in scanner: new scans skip violations present in baseline; report only delta (new violations since baseline). | TODO |
| BASE-003 | Implement `# green-ai: ignore next-line <rule_id> reason="..."` inline suppression comment in Python/JS/TS. | TODO |
| BASE-004 | Implement `.green-ai/suppress.yaml` for file-level or project-level suppressions with mandatory reason and optional expiry date. Auto-expire: suppressions older than expiry re-surface as violations. | TODO |
| BASE-005 | Add `green-ai baseline update` — re-scan and update baseline with current state. | TODO |
| BASE-006 | Dashboard: show baseline delta prominently ("+3 new, -1 fixed since baseline"). | TODO |
| BASE-007 | Write `tests/baseline/test_baseline.py`. Coverage ≥95%. | TODO |

---

## EPIC-27: SBOM & Compliance Reporting

**Goal:** Generate Software Bill of Materials for compliance (SOC2, CSRD, ISO 14001). Compute Software Carbon Intensity per GSF spec.

| Task | Spec | Status |
|---|---|---|
| SBOM-001 | Implement `src/core/sbom/generator.py` — generate CycloneDX 1.5 JSON SBOM from SCA manifest data. Fields: component name, version, purl, licenses, vulnerabilities. | TODO |
| SBOM-002 | Add SPDX 2.3 format output option alongside CycloneDX. | TODO |
| SBOM-003 | Add `green-ai sbom ./repo --format cyclonedx` CLI command. Output to `output/sbom-<project>.json`. | TODO |
| SBOM-004 | Implement GSF Software Carbon Intensity (SCI) calculation: `SCI = (E * I + M) / R`. E=energy, I=carbon intensity, M=embodied, R=functional unit. Expose `GET /api/sci`. | TODO |
| SBOM-005 | Generate ESG compliance summary PDF: covers E (SCI + energy violations), S (CVE count + CVSS summary + secret findings), G (debt hours + license issues). Export as audit-ready document. | TODO |
| SBOM-006 | Write `tests/sbom/test_generator.py`. Coverage ≥95%. | TODO |

---

## EPIC-28: Sustainable AI Usage Analyzer (v1.0.4)

**Goal:** Detect AI/LLM SDK usage across all major providers and flag 12 unsustainable patterns — overkill model selection, missing token budgets, no prompt caching, API calls in loops, PII leakage, prompt injection, unvalidated output, and more. Estimate CO2 per detected call by model tier.

**Market gap:** No static analysis tool currently scans for unsustainable AI usage. As LLM calls become ubiquitous, this is the next frontier of energy-aware code review.

**Providers supported:** Anthropic, OpenAI, LangChain, Ollama, AWS Bedrock, Vertex AI, Groq, Mistral, Cohere, LlamaIndex, LiteLLM, Google Gemini.

| Task | Spec | Status |
|---|---|---|
| AI-001 | `src/core/detectors/ai_usage_detector.py` — text/regex detector for AI SDK imports and 12 unsustainable patterns. `AIUsageDetector.detect_all()` returns `AIViolation` list. CO2 tier estimate per model class. | **DONE** |
| AI-002 | `rules/ai_usage.yaml` — 12 YAML rule definitions (ai_call_in_loop, ai_missing_max_tokens, ai_no_prompt_caching, ai_pii_in_prompt, ai_prompt_injection_risk, ai_sync_client_in_async, ai_unvalidated_output, ai_overkill_model_in_loop, ai_overkill_model_classification, ai_redundant_system_prompt_in_loop, ai_no_retry_handling, ai_streaming_disabled_large_output). Source tags: GSF-AI, OWASP-LLM01/02. | **DONE** |
| AI-003 | Tests: `tests/test_ai_usage_detector.py` — 33 tests covering provider detection (Python + JS/TS), all 12 patterns, violation metadata, file scanning. 0 lint errors. | **DONE** |
| AI-004 | Wire `AIUsageDetector` into the main scan flow via `scan_file_worker`. Add `category: ai_sustainability` to violations so they appear in dashboard and exports. | **DONE** |
| AI-005 | Add `--checks ai` CLI flag to `src/cli/commands/scan.py`. Comma-separated: `energy,ai,security,quality,all`. Injected into scanner config for worker access. | **DONE** |
| AI-006 | Add `GET /api/ai` endpoint returning AI violation summary (total violations, CO2 estimate, by-rule breakdown, detected providers). | **DONE** |
| AI-007 | AI sustainability fields (category, provider, model_tier, estimated_co2_g, co2_note) preserved in JSON export via schema update. CSV export adds 5 AI columns + AI CO2 total in summary row. | **DONE** |
| AI-008 | JS/TS provider detection: `require()`/`import` patterns for `@anthropic-ai/sdk`, `openai`, `groq-sdk`, `@google/generative-ai`, `@langchain/*`, `@mistralai/mistralai`, `cohere-ai`, `llamaindex`, `litellm`. | **DONE** |

---

## EPIC-29: Standards Sync Engine (v1.0.4)

**Goal:** Automated fetch-validate-store pipeline for 5 live standards sources. Version manifest with SHA-256 hash verification, configurable sync interval, offline fallback, and a `fail_on_stale` CI gate. Like an antivirus database updater, but for code health standards.

**Standards sources:**
- `gsf` — Green Software Foundation Patterns
- `ecocode` — ecoCode Rules (green-code-initiative)
- `owasp` — OWASP Top 10 (2021, live)
- `cwe` — CWE/MITRE Top 25 Most Dangerous Weaknesses
- `epss` — FIRST.org EPSS Exploit Probability Scores (top 100)

| Task | Spec | Status |
|---|---|---|
| STD-001 | `src/standards/sync_engine.py` — `StandardsSyncEngine` with version manifest (`manifest.json`), SHA-256 hash verification per source, configurable `sync_interval_hours`, offline fallback to cached content, `check_stale()` / `any_stale()` for CI gate. | **DONE** |
| STD-002 | `src/standards/sources.py` — Extended with `OWASPTop10Source` (10 rules + embedded fallback), `CWESource` (25 CWE Top 25 rules + embedded fallback), `EPSSSource` (FIRST.org API, top 100 CVEs by exploit probability). | **DONE** |
| STD-003 | `src/cli/commands/standards.py` — New commands: `green-ai standards sync [--source X] [--force] [--interval N]`, `green-ai standards versions` (manifest table), `green-ai standards check [--max-age-days N] [--fail-on-stale]`. | **DONE** |
| STD-004 | Tests: `tests/test_standards_sync_engine.py` — 37 tests covering source registry, manifest persistence, hash verification, sync behaviour, offline fallback, stale check, versions output, OWASP/CWE/EPSS sources. All passing. | **DONE** |
| STD-005 | `_run_standards_sync()` in `scan.py` — auto-syncs on scan start when `standards_sync.auto_sync: true`. Reads `sync_interval_hours`. Logs sync status. Uses distinct `standards_sync` key to avoid clash with existing `standards: List[str]` config. | **DONE** |
| STD-006 | `green-ai scan --fail-on-stale-standards [--standards-max-age N]` exits code 2 on stale sources. `green-ai ci check-standards --fail-on-stale` standalone CI gate command. | **DONE** |
| STD-007 | `GET /api/standards/versions` — manifest JSON with any_stale flag. `POST /api/standards/sync?force=true` — trigger sync from dashboard. | **DONE** |
| STD-008 | `CWESource._fetch_from_zip()` — downloads MITRE CWE JSON zip, parses Weakness entries via `zipfile`+`io.BytesIO`, maps Likelihood_Of_Exploit to severity, caps at 200 entries. Falls back to embedded Top 25 on failure. | **DONE** |
| STD-009 | `green-ai standards diff <source>` — fetches live remote, computes SHA-256, compares to manifest hash, reports size delta and hash diff. | **DONE** |

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
| BLOCK-003 | OSV.dev API rate limits for SCA-002 | Cache responses 24h, batch queries |
| BLOCK-004 | BUG-007: websockets.legacy deprecation in test output | Upstream uvicorn issue; track release |
| BLOCK-005 | ESG weight calibration needs real repo data | Sample 10 OSS repos before finalising ESG-002 |

---

## Work Units Available

| Phase | State | Count |
|---|---|---|
| Phase 2 | Active TODO tasks | 32 |
| Phase 2 | Bug fixes TODO | 2 (AUDIT-005, AUDIT-006) |
| Phase 3 | New epics (EPIC-19–27) | 9 epics / 90 tasks |
| Phase 3+ | EPIC-28 AI Usage Analyzer (AI-004–008) | 5 tasks |
| Phase 3+ | EPIC-29 Standards Sync Engine (STD-005–009) | 5 tasks |
| All | Done (this milestone) | 14 (EPIC-28 AI-001–003, EPIC-29 STD-001–004, BUG-001–006, AUDIT-004) |

**Total available WU: 134** — above the 100 WU minimum threshold.
