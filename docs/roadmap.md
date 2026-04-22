# Roadmap

## Vision
Empower every developer to write energy-efficient code by default — making software sustainability as fundamental as performance and security.

---

## Phase 1: Awareness (MVP) — COMPLETE
**Versions:** v0.1 – v0.6  
**Goal:** Detect basic inefficiencies in Python and JavaScript.

| Capability | Status |
|---|---|
| AST-based scanning (Python, JS) | Done |
| YAML-driven rule engine (80+ rules) | Done |
| CLI interface (`scan`, `project`, `dashboard`) | Done |
| Web dashboard (FastAPI + Socket.IO) | Done |
| HTML, CSV, JSON, PDF export | Done |
| LLM auto-fix (`fix-ai`) | Done |
| TypeScript, Java, Go, C# language support | Done |
| CI/CD GitHub Action | Done |
| Performance optimization (multiprocessing) | Done |
| Security hardening (OWASP, input sanitization) | Done |
| Kubernetes cloud deployment | Done |
| Telemetry and emissions tracking | Done |

---

## Phase 2: Action & Expansion — ACTIVE
**Versions:** v0.7 – v0.9.x  
**Goal:** IDE integration, ML-based detection, team collaboration, Rust support.

### Milestone M1 — Stability Gate (v0.9.1) — ACTIVE
**Gate:** 0 lint errors | 95% test coverage | Build pass

| Epic | Status |
|---|---|
| EPIC-00: Stability Gate (deps, deprecations) | Done |
| EPIC-09: IDE Plugins — LSP foundation | In Progress |
| EPIC-09: IDE Plugins — VS Code extension | In Progress |
| EPIC-18: System Audit & Hardening | In Progress |
| EPIC-18: Automated security test expansion | Todo |

### Milestone M2 — IDE Release (v0.9.4)
**Gate:** VS Code extension published | LSP full protocol | 95% coverage

| Epic | Target |
|---|---|
| EPIC-09: Full VS Code extension (scaffold, quick fix, diagnostics) | v0.9.4 |
| EPIC-09: LSP server complete (initialize, sync, diagnostics, code actions) | v0.9.4 |

### Milestone M3 — Team Collaboration (v0.9.5)
**Gate:** Team API tested | RBAC enforced | Dashboard shows team metrics

| Epic | Target |
|---|---|
| EPIC-12: Team database schema (SQLAlchemy) | v0.9.5 |
| EPIC-12: Team CRUD API endpoints | v0.9.5 |
| EPIC-12: RBAC (Viewer/Editor roles) | v0.9.5 |
| EPIC-12: Team dashboard UI (Chart.js) | v0.9.5 |
| EPIC-12: Historical trend charts | v0.9.5 |
| EPIC-12: OAuth2 authentication integration | v0.9.5 |
| EPIC-12: Email summary notifications | v0.9.5 |

### Milestone M4 — ML Detection (v0.9.6)
**Gate:** ONNX model inference working | F1 score documented | Fallback tested

| Epic | Target |
|---|---|
| EPIC-13: Training dataset collection | v0.9.6 |
| EPIC-13: PyTorch Transformer model | v0.9.6 |
| EPIC-13: Training + evaluation pipeline | v0.9.6 |
| EPIC-13: ONNX export and runtime integration | v0.9.6 |
| EPIC-13: MLDetector with regex fallback | v0.9.6 |
| EPIC-13: `--enable-ml` CLI flag | v0.9.6 |

### Milestone M5 — Rust Support (v0.9.7)
**Gate:** Rust scanning functional | 3 rules verified | E2E test passes

| Epic | Target |
|---|---|
| EPIC-14: tree-sitter-rust integration | v0.9.7 |
| EPIC-14: RustASTDetector class | v0.9.7 |
| EPIC-14: Rules: excessive clone, allocations, unwrap in loops | v0.9.7 |
| EPIC-14: Rust fixture project + E2E tests | v0.9.7 |

---

## Phase 3: Ecosystem & Scale — PLANNED
**Versions:** v1.0.x  
**Goal:** Enterprise adoption, cloud-native SaaS, plugin ecosystem.

| Capability | Notes |
|---|---|
| SSO / enterprise auth (SAML, OIDC) | Team admin control plane |
| Multi-tenant SaaS deployment | Isolated namespaces per org |
| IntelliJ / JetBrains plugin | Mirrors VS Code feature set |
| Rule marketplace | Community-contributed YAML rules |
| Public REST API (v1) | Stable, versioned, documented |
| Webhook integrations (Slack, JIRA, GitHub) | Violation alerting |
| Ollama self-hosted LLM tier | Air-gapped enterprise option |
| Advanced OWASP coverage (A01, A02, A07, A08, A10) | Close remaining security gaps |
| Carbon dashboard SaaS | Aggregate emissions across orgs |

---

## Phase 4: Autonomous Intelligence — FUTURE
**Versions:** v1.1+  
**Goal:** Fully autonomous scanning, remediation, and continuous learning.

| Capability | Notes |
|---|---|
| Continuous learning from real-world fixes | Model retrained on accepted suggestions |
| Autonomous PR bot | Opens PRs with fixes, no human trigger |
| Repo-level architectural recommendations | Beyond file-level violations |
| Multi-agent orchestration | Parallel scanner + fixer + reporter agents |
| Green SLA enforcement | CI gate on estimated CO2 budget |

---

## Definition of Done (all phases)

Every task must pass all four gates before closing:

| Gate | Requirement |
|---|---|
| Test | ≥95% coverage on new code paths |
| Lint | 0 flake8 errors in touched files |
| Opt | No O(n²) unless formally justified |
| Sec | Input sanitized; no shell injection, no raw SQL |
