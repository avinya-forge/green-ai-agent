# Backlog

> **Vision:** One tool — Environmental (energy/carbon) + Security (SAST/secrets/SCA) + Governance (quality/debt/license) + AI Fix. Single CLI, VS Code, CI/CD, and Dashboard.

## 1. Bugs (P0 - Immediate)

| ID | Priority | Component | Issue | Status |
|---|---|---|---|---|
| BUG-007 | HIGH | UI/Server | websockets.legacy deprecation in test output (Upstream uvicorn issue). | OPEN |
| BUG-017 | MEDIUM | Scanner | Large refactor technical debt remaining from multiprocessing implementation. | OPEN |
| BUG-021 | MEDIUM | CLI | CLI help text mismatch in `tests/test_cli_refactored.py`. | FIXED |

## 2. Feature Completion (P1 - Stability & Parity)

| ID | Epic | Task | Status |
|---|---|---|---|
| IDE-001 | IDE | Initialize VS Code extension scaffold in `src/ide/vscode/`. | TODO |
| IDE-002 | IDE | Implement LSP server basic diagnostics (initialize, didOpen, didChange). | TODO |
| AUDIT-003 | Audit | Create security tests for XSS/injection in dashboard. | TODO |
| AUDIT-005 | Audit | Add path traversal tests for `/api/remediation/preview`. | TODO |
| TEAM-001 | Team | Database migration and setup for team features (SQLAlchemy). | TODO |
| TEAM-002 | Team | Add `POST /api/teams` and `GET /api/teams` endpoints. | TODO |
| SEC-001 | Security | Full OWASP Top 10 rules coverage across all 6 languages. | TODO |
| SEC-002 | Security | 100+ proven secret patterns (AWS, GCP, JWT, etc.). | TODO |
| SBOM-005 | SBOM | Generate ESG compliance summary PDF (E: SCI, S: Secrets, G: Debt). | TODO |

## 3. New Features (P2 - Expansion & Vision Alignment)

| ID | Epic | Task | Status |
|---|---|---|---|
| DASH-001 | UI | Redesign Dashboard UI to match SonarQube layout (Projects, Issues, Debt). | TODO |
| DASH-002 | UI | Integrate Git user details and history into Issue views. | TODO |
| DASH-003 | UI | Role-based rule profiles (e.g., "Developer", "Security Auditor", "Green Lead"). | TODO |
| DASH-004 | UI | Interactive rule toggle (Enable/Disable) in Dashboard with config sync. | TODO |
| SCA-001 | Security | Dependency parsing (requirements.txt, package.json, go.mod). | TODO |
| SCA-002 | Security | CVE lookup via OSV.dev API integration. | TODO |
| QUAL-001 | Quality | Cyclomatic + cognitive complexity scoring per function. | TODO |
| QUAL-002 | Quality | Duplicate code detection (Type 1/2 clones). | TODO |
| QUAL-003 | Quality | Dead code analysis integration (Vulture-based). | TODO |
| DEBT-001 | Governance | Assign remediation effort (hours) per violation category. | TODO |
| DEBT-002 | Governance | Aggregate technical debt score per file, module, and project. | TODO |
| ESG-001 | Governance | Weighted aggregate ESG score (0–100) from scan output. | TODO |
| RUST-001 | Rust | Add tree-sitter-rust and RustASTDetector with initial rules. | TODO |

## 4. Technical Debt & Cleanup (P3)

| ID | Task | Status |
|---|---|---|
| ENG-018 | Remove scrubbed dead code leftovers in `src/core/detectors/python_detector.py`. | TODO |
| ENG-019 | Standardize all `Query(...)` parameters across API endpoints for path traversal. | TODO |
| ENG-020 | Continuous documentation parity: Auto-sync vision.md with architecture.md. | TODO |

## 5. Completed Tasks (v1.0.3 Batch)

| ID | Task | Status |
|---|---|---|
| BASE-001 | Implement `green-ai baseline create` (Acknowledge technical debt). | DONE |
| BASE-002 | Implement baseline comparison in scanner (Report delta only). | DONE |
| BASE-003 | Implement `# green-ai: ignore next-line` inline suppression. | DONE |
| BASE-004 | Implement `.green-ai/suppress.yaml` for project-level suppression. | DONE |
| SBOM-001 | Implement CycloneDX 1.5 JSON SBOM generation. | DONE |
| SBOM-002 | Add SPDX 2.3 format support. | DONE |
| SBOM-003 | Add `green-ai sbom` CLI command. | DONE |
| SBOM-004 | Implement GSF Software Carbon Intensity (SCI) calculation. | DONE |
| SBOM-006 | Write `tests/test_sbom.py` and `tests/test_baseline.py`. | DONE |
| VER-001 | Updated version to v1.0.3 and standardized help text. | DONE |

---
> Tasks follow the SSOT vision defined in `/docs/vision.md`.
