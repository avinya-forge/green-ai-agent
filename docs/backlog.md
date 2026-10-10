# Backlog

> **Vision:** One tool — Environmental (energy/carbon) + Security (SAST/secrets/SCA) + Governance (quality/debt/license) + AI Fix. Single CLI, VS Code, CI/CD, and Dashboard.

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
|---|---|---|---|
| EPIC-19-2 | P1 | Implement taint tracking for SQL injection detection. | DONE |
| EPIC-19-3 | P1 | Implement taint tracking for command injection and SSRF. | DONE |
| EPIC-19-4 | P2 | Implement taint tracking for path traversal and XXE. | TODO |
| EPIC-19-5 | P2 | Implement insecure deserialization detection. | TODO |

### EPIC-20: Secret Scanning v2
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-20-1 | P1 | Implement 100+ proven secret regex patterns (AWS, GCP, Azure, GitHub, Stripe, Twilio, JWT, RSA, SSH). | DONE |
| EPIC-20-2 | P2 | Integrate git history scan for historical secrets. | TODO |
| EPIC-20-3 | P1 | Implement Shannon Entropy detection for high-entropy strings (e.g., base64 encoded secrets). | DONE |

### EPIC-21: Dependency & SCA
| ID | Priority | Task | Status |
|---|---|---|---|
| EXT-002 | P3 | Add support for automated dependency updates and PR creation. | TODO |
| EPIC-21-2 | P2 | Implement license detection and policy enforcement. | TODO |
| EPIC-21-3 | P2 | Add outdated package flagging. | TODO |

### EPIC-22: Code Quality Engine
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-22-2 | P2 | Implement method length, class size, and coupling metrics scoring. | TODO |

### EPIC-23: Technical Debt Scoring
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-23-1 | P2 | Aggregate debt score per file, module, and project based on remediation effort. | TODO |

### EPIC-24: ESG Score Engine
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-24-1 | P2 | Compute composite ESG score aggregating E-score, S-score, and G-score. | TODO |

### EPIC-25: Unified Dashboard Redesign
| ID | Priority | Task | Status |
|---|---|---|---|
| EXT-001 | P3 | Implement real-time energy usage visualization via Scaphandre on the dashboard. | TODO |
| EPIC-25-1 | P2 | Implement single dashboard showing ESG score, drill-down to each pillar, per-file breakdown, trend over time, fix priority queue. | TODO |

### EPIC-26: Custom Rules Engine & Baseline & Suppression
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-26-1 | P2 | Implement user-definable YAML rules (Semgrep-style). Pattern: regex, AST query, or taint. | TODO |
| EPIC-26-3 | P3 | Create community rule registry and rule versioning/import system. | TODO |

### EPIC-28: Sustainable AI Usage Analyzer
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-28-3 | P2 | Add configuration for custom token cost and carbon emission factors per model tier. | TODO |
