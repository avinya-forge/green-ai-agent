# Backlog

> **Vision:** One tool — Environmental (energy/carbon) + Security (SAST/secrets/SCA) + Governance (quality/debt/license) + AI Fix. Single CLI, VS Code, CI/CD, and Dashboard.

## Phase 2: Action & Expansion (ACTIVE)

### EPIC-09: Full VS Code extension (scaffold, quick fix, diagnostics)
| ID | Priority | Task | Status |
|---|---|---|---|
| EXT-003 | P3 | Develop a VS Code extension for inline Green-AI linting. | TODO |
| EPIC-09-1 | P1 | Implement LSP server initialization, sync, and diagnostics. | TODO |

### EPIC-12: Team database schema + CRUD API + RBAC
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-12-1 | P2 | Design Team database schema + CRUD API + RBAC. | TODO |
| EPIC-12-2 | P2 | Implement Team dashboard UI (Chart.js) + historical trends. | TODO |

### EPIC-13: Dataset → PyTorch model → ONNX export → MLDetector
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-13-1 | P2 | Dataset → PyTorch model → ONNX export → MLDetector. | TODO |
| EPIC-13-2 | P2 | Add `--enable-ml` CLI flag + integration tests. | TODO |

### EPIC-14: tree-sitter-rust + RustASTDetector + 3 rules + E2E
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-14-1 | P2 | Add tree-sitter-rust + RustASTDetector + 3 rules + E2E tests. | TODO |

## Phase 3: Security, Quality & ESG (PLANNED)

### EPIC-19: SAST Expansion
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-19-1 | P1 | Add full OWASP Top 10 rules across all 6 languages and CWE mapping. | TODO |
| EPIC-19-2 | P1 | Implement taint tracking for injection (SQL injection, command injection, SSRF, path traversal, XXE, insecure deserialization). | TODO |

### EPIC-20: Secret Scanning v2
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-20-1 | P1 | Add 100+ proven secret patterns (AWS, GCP, Azure, GitHub, Stripe, Twilio, JWT, RSA, SSH) and Git history scan. | TODO |

### EPIC-21: Dependency & SCA
| ID | Priority | Task | Status |
|---|---|---|---|
| EXT-002 | P3 | Add support for automated dependency updates and PR creation. | TODO |
| EPIC-21-1 | P2 | Parse requirements.txt/package.json/go.mod/pom.xml and CVE lookup via OSV.dev. | TODO |
| EPIC-21-2 | P2 | Add license detection, policy enforcement, and outdated package flagging. | TODO |

### EPIC-22: Code Quality Engine
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-22-1 | P2 | Add cyclomatic + cognitive complexity scoring per function, and duplicate code detection (Type 1/2 clones). | TODO |
| EPIC-22-2 | P2 | Implement dead code analysis (integrate Vulture), method length, class size, coupling metrics. | TODO |

### EPIC-23: Technical Debt Scoring
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-23-1 | P2 | Assign remediation effort (hours) per violation category and aggregate debt score per file, module, project. | TODO |

### EPIC-24: ESG Score Engine
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-24-1 | P2 | Compute E-score (energy violations + carbon), S-score (security vulns + secrets + deps), G-score (quality + debt + test coverage + license). | TODO |

### EPIC-25: Unified Dashboard Redesign
| ID | Priority | Task | Status |
|---|---|---|---|
| EXT-001 | P3 | Implement real-time energy usage visualization via Scaphandre on the dashboard. | TODO |
| EPIC-25-1 | P2 | Implement single dashboard showing ESG score, drill-down to each pillar, per-file breakdown, trend over time, fix priority queue. | TODO |

### EPIC-26: Custom Rules Engine & Baseline & Suppression
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-26-1 | P2 | Implement user-definable YAML rules (Semgrep-style). Pattern: regex, AST query, or taint. Community rule registry. Rule versioning and import. | TODO |
| EPIC-26-2 | P2 | Implement `green-ai baseline create` exports current violations as accepted baseline. | TODO |

### EPIC-27: SBOM & Compliance
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-27-1 | P2 | Generate CycloneDX and SPDX format SBOMs. License compliance report. Export for audit (SOC2, CSRD, ISO 14001). SCI (Software Carbon Intensity) score per GSF spec. | TODO |

### EPIC-28: Sustainable AI Usage Analyzer
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-28-1 | P1 | Detect AI/LLM SDK usage (Anthropic, OpenAI, LangChain, Ollama, Bedrock, Vertex, Groq, Mistral, Cohere, LlamaIndex, LiteLLM). | TODO |
| EPIC-28-2 | P1 | Flag 12 unsustainable patterns: overkill model selection, missing token budget, no prompt caching, API calls in loops, PII in prompts, prompt injection risk, unvalidated output, sync client in async context. Estimate CO2 per detected call by model tier. | TODO |

### EPIC-29: Standards Sync Engine
| ID | Priority | Task | Status |
|---|---|---|---|
| EPIC-29-1 | P1 | Automated fetch-validate-store pipeline for live standards: GSF patterns, ecoCode rules, OWASP Top 10, CWE/MITRE, EPSS. Version manifest with hash verification. | TODO |
