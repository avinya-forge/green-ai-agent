# Backlog

> **Vision:** One tool — Environmental (energy/carbon) + Security (SAST/secrets/SCA) + Governance (quality/debt/license) + AI Fix. Single CLI, VS Code, CI/CD, and Dashboard.

## 🌌 6–8 Month Strategic Roadmap & Horizon Plan

| Horizon | Core Strategic Milestone | Lead Focus | Key Deliverables |
|:---:|:---|:---|:---|
| **Month 1–2** | **SAST & Secret Scanning v2 Hardening** | AST Analysis & Entropy | Taint tracking for path traversal/XXE, 100+ regex secret patterns, Shannon entropy scanner |
| **Month 3–4** | **Energy Inefficiency ML Detection (ONNX)** | Model Training & Inference | PyTorch energy pattern training, ONNX export, MLDetector CLI integration (`--enable-ml`) |
| **Month 5–6** | **VS Code Extension & Interactive LSP Remediation** | IDE Developer Experience | LSP server with LLM quick-fixes, dashboard webview, automated PR creation for SCA |
| **Month 7–8** | **Unified ESG Scoring & Scaphandre Real-time Telemetry** | Full-Stack Metrics & Dashboard | Composite ESG score aggregation, Scaphandre hardware energy tracking, Semgrep-style custom YAML rules |

---

## Phase 2: Action & Expansion (ACTIVE)

### EPIC-09: Full VS Code extension (scaffold, quick fix, diagnostics)
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-09-3 | P3 | Develop VS Code UI webview for Dashboard integration. | TODO |
| EPIC-09-4 | P2 | Implement inline code actions (Quick Fix) using LLM remediation in LSP server. | TODO |
| EPIC-09-5 | P1 | Package and publish VS Code extension to the marketplace. | TODO |

### EPIC-12: Team database schema + CRUD API + RBAC
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-12-1 | P2 | Implement Role-Based Access Control (RBAC) middleware for existing Team API endpoints. | TODO |
| EPIC-12-2 | P2 | Implement Team dashboard UI (Chart.js) + historical trends visualization. | TODO |
| EPIC-12-3 | P3 | Add audit logging for team management actions (add/remove members). | TODO |

### EPIC-13: Dataset → PyTorch model → ONNX export → MLDetector
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-13-1 | P2 | Prepare training dataset of energy-inefficient code patterns. | TODO |
| EPIC-13-2 | P2 | Train PyTorch model and export to ONNX format. | TODO |
| EPIC-13-3 | P2 | Implement MLDetector class to run ONNX model inference. | TODO |
| EPIC-13-4 | P2 | Add `--enable-ml` CLI flag + integration tests. | TODO |

## Phase 3: Security, Quality & ESG (PLANNED)

### EPIC-19: SAST Expansion
| ID | Priority | Task | Status |
| EPIC-19-4a | P1 | Implement AST taint tracking for path traversal vulnerability detection. | TODO |
| EPIC-19-4b | P2 | Implement AST taint tracking for XXE (XML External Entity) injection detection. | TODO |
| EPIC-19-5 | P2 | Implement insecure deserialization detection (pickle, yaml, etc.). | TODO |

### EPIC-20: Secret Scanning v2
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-20-2a | P2 | Integrate pygit2 for git history scanning of historical secrets across branches. | TODO |
| EPIC-20-2b | P2 | Design and implement an optimized caching layer for git history scanning to prevent performance degradation. | TODO |

### EPIC-21: Dependency & SCA
| ID | Priority | Task | Status |
|---|---|---|---|
| EXT-002a | P3 | Research and implement an automated PR creation bot for outdated or vulnerable dependency updates. | TODO |
| EXT-002b | P3 | Add automated integration tests for the PR creation bot. | TODO |
| EPIC-21-2a | P2 | Parse licenses from `package.json`, `requirements.txt`, `go.mod`, and `pom.xml`. | TODO |
| EPIC-21-2b | P2 | Enforce strict license policies (fail CI if AGPL/GPL is detected in proprietary mode). | TODO |
| EPIC-21-3 | P2 | Add outdated package flagging by calling respective package registry APIs (PyPI, npm, etc). | TODO |

### EPIC-22: Code Quality Engine
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-22-2a | P2 | Implement AST-based method length metric scoring with configurable thresholds. | TODO |
| EPIC-22-2b | P2 | Implement AST-based class size metric scoring. | TODO |
| EPIC-22-2c | P2 | Implement coupling metrics (fan-in/fan-out) scoring for classes and modules. | TODO |

### EPIC-23: Technical Debt Scoring
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-23-1a | P2 | Define remediation effort mapping (in minutes) for each rule id in the rule registry. | TODO |
| EPIC-23-1b | P2 | Calculate and aggregate debt score (total minutes) per file, module, and project. | TODO |

### EPIC-24: ESG Score Engine
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-24-1a | P2 | Define formula to compute Environmental (E), Social/Security (S), and Governance (G) sub-scores. | TODO |
| EPIC-24-1b | P2 | Compute composite ESG score aggregating E-score, S-score, and G-score and integrate into `Scanner` output. | TODO |

### EPIC-25: Unified Dashboard Redesign
| ID | Priority | Task | Status |
|---|---|---|---|
| EXT-001a | P3 | Research Scaphandre API and define data models for real-time energy usage. | TODO |
| EXT-001b | P3 | Implement real-time energy usage visualization via Scaphandre on the dashboard. | TODO |
| EPIC-25-1a | P2 | Design comprehensive ESG dashboard mockups (Score, Drill-down, Per-file breakdown). | TODO |
| EPIC-25-1b | P2 | Implement unified dashboard UI components in React/Vue or HTML templates for ESG scores. | TODO |
| EPIC-25-1c | P2 | Implement fix priority queue view sorted by severity and technical debt in the dashboard. | TODO |

### EPIC-26: Custom Rules Engine & Baseline & Suppression
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-26-1a | P2 | Define Semgrep-style YAML schema for user-definable custom rules. | TODO |
| EPIC-26-1b | P2 | Implement regex, AST query, and taint pattern matchers for custom YAML rules. | TODO |
| EPIC-26-3a | P3 | Create schema and registry API for community rules. | TODO |
| EPIC-26-3b | P3 | Implement rule versioning and an import system (`green-ai rules pull <namespace/rule>`). | TODO |

### EPIC-28: Sustainable AI Usage Analyzer
| ID | Priority | Task | Status |
|---|---|---|---|
<<<<<<< HEAD
| EPIC-28-3a | P2 | Create YAML configuration schema for custom token cost per model tier. | TODO |
| EPIC-28-3b | P2 | Create YAML configuration schema for carbon emission factors per model tier. | TODO |
| EPIC-28-3c | P2 | Integrate custom cost and emission configurations into AI Usage calculation engine. | TODO |
=======
| EPIC-28-3 | P2 | Add configuration for custom token cost and carbon emission factors per model tier. | TODO |

### EPIC-30: Core Security Hardening (NEW)
| ID | Priority | Task | Status |
|---|---|---|---|
| SEC-010 | P1 | Audit and replace all MD5 hashing functions with SHA-256 for security compliance. | TODO |
| SEC-011 | P1 | Replace all risky `os.system` and `subprocess.call` usages with safe subprocess.run with shell=False. | TODO |
| SEC-012 | P1 | Ensure LLM inputs are isolated from system instructions to prevent Prompt Injection (LLM01). | TODO |
>>>>>>> origin/docs/update-backlog-release-13559265004434037698
