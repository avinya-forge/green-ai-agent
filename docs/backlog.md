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

### EPIC-09: Full VS Code Extension (Scaffold, Quick Fix, Diagnostics)
*Objective: Deliver a robust developer experience inside VS Code with embedded dashboard and inline fixes.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-09-3 | P3 | Develop VS Code UI webview for Dashboard integration. | TODO |
| EPIC-09-4a | P2 | Design LLM prompt and payload schema for inline code actions (Quick Fix). | TODO |
| EPIC-09-4b | P2 | Implement LSP server endpoint for Quick Fix resolution. | TODO |
| EPIC-09-5a | P1 | Add automated build and test pipeline for VS Code extension. | TODO |
| EPIC-09-5b | P1 | Package and publish VS Code extension to the marketplace. | TODO |

### EPIC-12: Team Database Schema + CRUD API + RBAC
*Objective: Enable multi-user, multi-project workflows with strict access controls.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-12-1a | P2 | Define RBAC schemas and permission matrices in Pydantic. | TODO |
| EPIC-12-1b | P2 | Implement FastAPI dependency injection for RBAC checks. | TODO |
| EPIC-12-2a | P2 | Design Team dashboard wireframes and Chart.js integration plan. | TODO |
| EPIC-12-2b | P2 | Implement frontend UI for Team dashboard and historical trends. | TODO |
| EPIC-12-3 | P3 | Implement structured JSON audit logging for team management actions. | TODO |

### EPIC-13: Energy Inefficiency ML Detection
*Objective: Move beyond heuristics by training and deploying an ML model (ONNX) to detect inefficient loops and logic.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-13-1 | P2 | Curate and label a training dataset of 5k+ energy-inefficient code patterns. | TODO |
| EPIC-13-2a | P2 | Train PyTorch classifier on energy patterns dataset. | TODO |
| EPIC-13-2b | P2 | Export trained PyTorch model to optimized ONNX format. | TODO |
| EPIC-13-3 | P2 | Implement `MLDetector` class to execute ONNX inference with caching. | TODO |
| EPIC-13-4 | P2 | Wire `--enable-ml` CLI flag into the scanner orchestrator and add tests. | TODO |

## Phase 3: Security, Quality & ESG (PLANNED)

### EPIC-19: SAST Expansion (Taint Tracking)
*Objective: Expand code security checks to include deep taint analysis and deserialization vulnerabilities.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-19-4a | P1 | Implement AST taint tracking for path traversal detection. | TODO |
| EPIC-19-4b | P2 | Implement AST taint tracking for XXE (XML External Entity) injection. | TODO |
| EPIC-19-5 | P2 | Build detectors for insecure deserialization (pickle, yaml.load). | TODO |

### EPIC-20: Secret Scanning v2 Hardening
*Objective: Expand secret scanning to historic commits while maintaining performance.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-20-2a | P2 | Integrate pygit2 stream parsing to scan historical commits for secrets. | TODO |
| EPIC-20-2b | P2 | Implement an LRU cache layer and incremental scanning to prevent Git history performance drops. | TODO |

### EPIC-21: Dependency & Software Composition Analysis (SCA)
*Objective: Keep dependencies secure and compliant across environments.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EXT-002a | P3 | Design automated PR creation workflow for vulnerable dependencies. | TODO |
| EXT-002b | P3 | Build integration tests validating automated PR creation bot. | TODO |
| EPIC-21-2a | P2 | Implement parser for package lockfiles (`package.json`, `requirements.txt`, etc.) to extract licenses. | TODO |
| EPIC-21-2b | P2 | Implement license policy enforcer (block AGPL/GPL when configured). | TODO |
| EPIC-21-3 | P2 | Integrate PyPI/npm APIs to flag outdated dependencies directly in the scanner. | TODO |

### EPIC-22: Code Quality Engine
*Objective: Measure maintainability via complexity, coupling, and size metrics.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-22-2a | P2 | Implement AST-based method length metric scoring with user-configurable thresholds. | TODO |
| EPIC-22-2b | P2 | Implement AST-based class size metric scoring. | TODO |
| EPIC-22-2c | P2 | Compute coupling metrics (fan-in/fan-out) for Python classes and modules. | TODO |

### EPIC-23: Technical Debt Scoring
*Objective: Quantify code debt into measurable remediation time metrics.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-23-1a | P2 | Construct a mapping matrix assigning remediation effort (in minutes) to each rule ID. | TODO |
| EPIC-23-1b | P2 | Develop aggregation logic to calculate debt score (total minutes) per file, module, and project. | TODO |

### EPIC-24: Unified ESG Scoring Engine
*Objective: Combine environmental, security, and governance factors into a single executive score.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-24-1a | P2 | Finalize mathematical formula for E, S, and G sub-scores. | TODO |
| EPIC-24-1b | P2 | Integrate composite ESG scoring logic into the main `Scanner` output payload. | TODO |

### EPIC-25: Unified Dashboard Redesign & Live Telemetry
*Objective: Provide a modern, SonarQube-style dashboard with real-time hardware metrics.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EXT-001a | P3 | Investigate Scaphandre API for live hardware energy telemetry. | TODO |
| EXT-001b | P3 | Implement WebSocket/Polling connection to Scaphandre for dashboard graphs. | TODO |
| EPIC-25-1a | P2 | Create Figma/HTML mockups for ESG Dashboard (Score, Drill-down, Per-file). | TODO |
| EPIC-25-1b | P2 | Build React/Vue UI components corresponding to new dashboard mockups. | TODO |
| EPIC-25-1c | P2 | Implement priority queue view to sort issues by Severity + Tech Debt time. | TODO |

### EPIC-26: Custom Rules Engine (YAML & Baseline)
*Objective: Allow users to write and share their own security and quality rules.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-26-1a | P2 | Define and document the YAML schema (Semgrep-style) for custom rules. | TODO |
| EPIC-26-1b | P2 | Implement Regex, AST Query, and Taint pattern matching execution for YAML rules. | TODO |
| EPIC-26-3a | P3 | Design the API and schema for a community rule registry. | TODO |
| EPIC-26-3b | P3 | Add `green-ai rules pull` command for importing namespace rules. | TODO |

### EPIC-28: Sustainable AI Usage Analyzer Expansion
*Objective: Allow users to customize AI usage tracking for emissions and cost.*
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-28-3a | P2 | Update YAML configuration schema to support custom token costs per model tier. | TODO |
| EPIC-28-3b | P2 | Update YAML configuration schema to support carbon emission factors per model tier. | TODO |
| EPIC-28-3c | P2 | Pipe custom cost/emission data into the AI Usage calculation engine. | TODO |

### EPIC-30: Core Security Hardening
*Objective: Ensure the Green-AI tool itself is resilient against OWASP top 10 vulnerabilities.*
| ID | Priority | Task | Status |
|---|---|---|---|
| SEC-010a | P1 | Audit codebase and identify all usages of MD5 hashing (e.g. `hashlib.md5`). | TODO |
| SEC-010b | P1 | Replace all identified MD5 hashing with SHA-256 (`hashlib.sha256`) for strict security compliance. | TODO |
| SEC-012 | P1 | Harden LLM prompts using XML tag wrappers (`<user_input>`) to prevent Prompt Injection (LLM01). | TODO |
