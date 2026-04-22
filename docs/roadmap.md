# Roadmap

---

## Vision (Revised)

**One tool. Every dimension of code health.**

Green-AI started as an energy-efficiency scanner rooted in Green Software Foundation rules. The expanded vision corrects its trajectory: become the single open-source code intelligence platform that makes software **sustainable, secure, and governable** — scanning for environmental impact, security vulnerabilities, code quality, and ESG compliance, with AI-powered remediation, deployable in any workflow.

> A developer should be able to run one command and get a complete picture of their codebase's environmental footprint, security posture, code debt, and compliance status — and have AI fix what it finds.

---

## Market Survey — Where We Stand

### Tools That Exist Today

| Tool | Focus | What It Does Well | What It Lacks |
|---|---|---|---|
| **SonarQube** | Code quality + security | 20+ languages, OWASP/CWE, bugs, smells, duplication | No energy/carbon rules, no AI fix, no ESG scoring |
| **Semgrep** | SAST + secrets | User-definable YAML rules, 30+ languages, huge community registry | No energy rules, no AI fix, no dashboard |
| **GitLeaks** | Secret scanning | 100+ proven secret patterns, git history scan | Only secrets, no quality or energy |
| **Snyk** | Dependency + SAST | CVE database, license compliance, automated PRs | No energy rules, cloud-only, paid |
| **CodeClimate** | Maintainability | Technical debt estimation, duplication, trends | No energy, no security depth, no AI fix |
| **ecoCode** | Green software | SonarQube plugin with energy rules | Plugin only, no standalone CLI, no AI, no dashboard |
| **CodeCarbon** | Emissions measurement | Real runtime emissions tracking | Runtime only, not static analysis |
| **pip-audit / npm audit** | Dependency vulns | CVE matching for packages | Single language, no other checks |
| **TruffleHog** | Entropy secrets | Shannon entropy + regex patterns, git history | Secrets only |
| **OpenSSF Scorecard** | Supply chain health | Security hygiene scoring for OSS repos | Repo-level only, no code analysis |
| **FOSSA / Black Duck** | License compliance | License detection, SCA | License only, enterprise/paid |
| **Bandit** | Python security | OWASP-aligned Python SAST | Python only, no fix, no dashboard |

### The Gap Green-AI Fills

No tool today combines:
- ✅ Energy efficiency + carbon scoring (our core)
- ✅ Security SAST across multiple languages
- ✅ Dependency vulnerability scanning
- ✅ Secret detection with proven patterns
- ✅ Code quality and technical debt
- ✅ ESG aggregate scoring (Environmental + Security + Governance)
- ✅ AI-powered auto-fix (not just suggestions — actual code changes)
- ✅ Single binary: CLI + VS Code + CI/CD + Dashboard

**No existing tool does all of this. That is our market position.**

### What We Already Have (Reality Check)

| Capability | Status | Notes |
|---|---|---|
| 68 energy/performance rules across 6 languages | ✅ Working | Python(26), JS(16), TS(18), Go(4), Java(4) |
| AST-based detection (tree-sitter) | ✅ Working | All 6 languages |
| Carbon emissions model per file | ✅ Working | Complexity-based estimate |
| Web dashboard with history and trends | ✅ Working | FastAPI + Socket.IO |
| CI/CD GitHub Action | ✅ Working | Docker-based, fail-on threshold |
| Multi-format export (CSV/JSON/HTML/PDF/XML) | ✅ Working | |
| LLM auto-fix (OpenAI + Mock) | ✅ Working | 3 full AST transforms + text hints for 65 others |
| Basic secret detection (entropy + 13 keywords) | ⚠️ Weak | No GitLeaks-style proven patterns |
| LSP server | ⚠️ Skeleton | Only detects `print(` → `logger.info()` |
| VS Code extension | ⚠️ Skeleton | Grammar + settings only |
| Security SAST (OWASP/CWE) | ❌ Missing | eval/innerHTML only |
| Dependency scanning (SCA) | ❌ Missing | |
| Duplicate code detection | ❌ Missing | |
| User-definable custom rules | ❌ Missing | All rules hardcoded |
| False positive suppression | ❌ Missing | No baseline or ignore mechanism |
| License compliance | ❌ Missing | |
| SBOM generation | ❌ Missing | |

---

## Product Pillars (ESG + S Framework)

```
┌──────────────────────────────────────────────────────────────┐
│                    Green-AI Code Intelligence                  │
├──────────────┬──────────────────┬──────────────┬─────────────┤
│      E       │        S         │      G       │   AI Fix    │
│ Environment  │    Security      │  Governance  │             │
├──────────────┼──────────────────┼──────────────┼─────────────┤
│ Energy rules │ SAST (OWASP/CWE) │ Code quality │ LLM-powered │
│ SCI scoring  │ Secret scanning  │ Tech debt    │ AST rewrite │
│ Carbon model │ Dependency vulns │ Duplication  │ PR bot      │
│ GSF/ecoCode  │ Supply chain     │ License      │ IDE quick   │
│ Cloud carbon │ Hardcoded creds  │ Test coverage│ fix         │
│ Runtime      │ Taint analysis   │ Dead code    │             │
│ emissions    │ Injection risks  │ Doc coverage │             │
└──────────────┴──────────────────┴──────────────┴─────────────┘
```

**Delivery modes (all from one install):**
- `green-ai scan ./src` — CLI
- `green-ai dashboard` — Web UI
- VS Code extension — inline diagnostics + quick fixes
- GitHub/GitLab/Jenkins Action — CI/CD gate
- REST API — integrate with anything

---

## Phase 1: Awareness (MVP) — COMPLETE
**Versions:** v0.1 – v0.6

| Capability | Status |
|---|---|
| AST-based scanning (Python, JS) | Done |
| YAML-driven rule engine | Done |
| CLI interface | Done |
| Web dashboard | Done |
| HTML/CSV/JSON/PDF export | Done |
| LLM auto-fix (`fix-ai`) | Done |
| TypeScript, Java, Go, C# support | Done |
| CI/CD GitHub Action | Done |
| Performance optimization (multiprocessing) | Done |
| Security hardening | Done |
| Kubernetes cloud deployment | Done |
| Telemetry and emissions tracking | Done |

---

## Phase 2: Action & Expansion — ACTIVE
**Versions:** v0.7 – v0.9.x  
**Goal:** IDE integration, ML detection, team collaboration, Rust support.

### Milestone M1 — Stability Gate (v0.9.1) — DONE
- 0 lint errors | 597 tests passing | Build clean

### Milestone M2 — IDE Release (v0.9.4)
**Gate:** VS Code extension operable | LSP full protocol | 95% coverage

| Epic | Target |
|---|---|
| EPIC-09: Full VS Code extension (scaffold, quick fix, diagnostics) | v0.9.4 |
| EPIC-09: LSP server complete (initialize, sync, diagnostics, code actions) | v0.9.4 |

### Milestone M3 — Team Collaboration (v0.9.5)
**Gate:** Team API tested | RBAC enforced | Dashboard shows team metrics

| Epic | Target |
|---|---|
| EPIC-12: Team database schema + CRUD API + RBAC | v0.9.5 |
| EPIC-12: Team dashboard UI (Chart.js) + historical trends | v0.9.5 |
| EPIC-12: OAuth2 + email summaries | v0.9.5 |

### Milestone M4 — ML Detection (v0.9.6)
**Gate:** ONNX model inference working | F1 score documented | Fallback tested

| Epic | Target |
|---|---|
| EPIC-13: Dataset → PyTorch model → ONNX export → MLDetector | v0.9.6 |
| EPIC-13: `--enable-ml` CLI flag + integration tests | v0.9.6 |

### Milestone M5 — Rust Support (v0.9.7)
**Gate:** Rust scanning functional | 3 rules verified | E2E test passes

| Epic | Target |
|---|---|
| EPIC-14: tree-sitter-rust + RustASTDetector + 3 rules + E2E | v0.9.7 |

---

## Phase 3: Security, Quality & ESG — PLANNED
**Versions:** v1.0.x  
**Goal:** Become the single tool for all code health dimensions.

### Milestone M6 — Security Depth (v1.0.0)
**Gate:** OWASP Top 10 covered | 50+ secret patterns | Dependency CVE matching

| Epic | Description | Target |
|---|---|---|
| EPIC-19: SAST Expansion | Full OWASP Top 10 rules across all 6 languages. CWE mapping. Taint tracking for injection. SQL injection, command injection, SSRF, path traversal, XXE, insecure deserialization. | v1.0.0 |
| EPIC-20: Secret Scanning v2 | 100+ proven secret patterns (AWS, GCP, Azure, GitHub, Stripe, Twilio, JWT, RSA, SSH). Git history scan. Configurable entropy thresholds. False positive verification. | v1.0.0 |
| EPIC-21: Dependency & SCA | Parse requirements.txt/package.json/go.mod/pom.xml. CVE lookup via OSV.dev (free, open). License detection and policy enforcement. Outdated package flagging. | v1.0.0 |

### Milestone M7 — Quality & Debt (v1.0.1)
**Gate:** Complexity metrics match SonarQube output | Duplication detected | Debt scored

| Epic | Description | Target |
|---|---|---|
| EPIC-22: Code Quality Engine | Cyclomatic + cognitive complexity scoring per function. Duplicate code detection (Type 1/2 clones). Dead code analysis (integrate Vulture). Method length, class size, coupling metrics. | v1.0.1 |
| EPIC-23: Technical Debt Scoring | Assign remediation effort (hours) per violation category. Aggregate debt score per file, module, project. Trend: debt added/removed per commit. | v1.0.1 |

### Milestone M8 — ESG Dashboard (v1.0.2)
**Gate:** ESG score computable from scan output | Dashboard shows all 3 pillars | Export includes ESG report

| Epic | Description | Target |
|---|---|---|
| EPIC-24: ESG Score Engine | Compute E-score (energy violations + carbon), S-score (security vulns + secrets + deps), G-score (quality + debt + test coverage + license). Weighted aggregate ESG score (0–100). | v1.0.2 |
| EPIC-25: Unified Dashboard Redesign | Single dashboard showing ESG score, drill-down to each pillar, per-file breakdown, trend over time, fix priority queue. Replace current single-category view. | v1.0.2 |
| EPIC-26: Custom Rules Engine | User-definable YAML rules (Semgrep-style). Pattern: regex, AST query, or taint. Community rule registry. Rule versioning and import. | v1.0.2 |

### Milestone M9 — Baseline & Governance (v1.0.3)
**Gate:** Baseline exportable and importable | CI gate respects baseline | SBOM generated

| Epic | Description | Target |
|---|---|---|
| EPIC-26: Baseline & Suppression | `green-ai baseline create` exports current violations as accepted baseline. New scans only report delta. Per-violation suppress with reason and expiry. | v1.0.3 |
| EPIC-27: SBOM & Compliance | Generate CycloneDX and SPDX format SBOMs. License compliance report. Export for audit (SOC2, CSRD, ISO 14001). SCI (Software Carbon Intensity) score per GSF spec. | v1.0.3 |

### Milestone M10 — Sustainable AI & Living Standards (v1.0.4)
**Gate:** AI usage detector covers 10+ providers | Standards sync operational with ≥4 sources | Auto-update verified in CI

#### Why This Milestone Exists

AI-generated and AI-assisted code is now ubiquitous. But **using AI sustainably is itself a code quality problem** — wasteful model choices, missing token budgets, redundant API calls in loops, PII leaking into prompts. No tool currently scans for this.

Simultaneously, every standard this tool enforces (GSF, OWASP, CWE, ecoCode) is a **living document** that updates. Without an automated sync mechanism, rules become stale — like an antivirus with a year-old database.

| Epic | Description | Target |
|---|---|---|
| EPIC-28: Sustainable AI Usage Analyzer | Detect AI/LLM SDK usage (Anthropic, OpenAI, LangChain, Ollama, Bedrock, Vertex, Groq, Mistral, Cohere, LlamaIndex, LiteLLM). Flag 12 unsustainable patterns: overkill model selection, missing token budget, no prompt caching, API calls in loops, PII in prompts, prompt injection risk, unvalidated output, sync client in async context. Estimate CO2 per detected call by model tier. | v1.0.4 |
| EPIC-29: Standards Sync Engine | Automated fetch-validate-store pipeline for live standards: GSF patterns, ecoCode rules, OWASP Top 10, CWE/MITRE, EPSS. Version manifest with hash verification. `green-ai standards sync/list/versions/check` CLI. Auto-sync on scan start (configurable interval, offline fallback). `fail_on_stale` CI gate. | v1.0.4 |

**Supported AI providers (EPIC-28):**
```
Anthropic (claude-*)  │  OpenAI (gpt-*, o1-*, o3-*)  │  Google (gemini-*)
Azure OpenAI          │  AWS Bedrock                   │  Groq
Ollama (local)        │  Mistral                       │  Cohere
LangChain             │  LlamaIndex                    │  LiteLLM (universal)
```

**Standards sources (EPIC-29):**
```
GSF Patterns       → api.github.com/repos/Green-Software-Foundation/patterns
ecoCode Rules      → api.github.com/repos/green-code-initiative/ecoCode
OWASP Top 10       → github.com/OWASP/www-project-top-ten
CWE/MITRE          → cwe.mitre.org/data/json/ (NVD data feed)
EPSS Scores        → api.first.org/data/v1/epss (exploit probability)
```

---

## Phase 4: Ecosystem & Autonomy — FUTURE
**Versions:** v1.1+  
**Goal:** Full ecosystem — enterprise, community, autonomous.

| Capability | Description |
|---|---|
| IntelliJ / JetBrains plugin | Feature-parity with VS Code extension |
| Autonomous PR bot | Opens PRs with AI fixes on schedule, no human trigger |
| Rule marketplace | Community YAML rules with ratings and downloads |
| SSO / enterprise auth | SAML, OIDC, org-level namespacing |
| Multi-tenant SaaS | Isolated per-org, cloud-hosted option |
| Policy-as-Code | `green-ai policy.yaml` defines gates; CI enforces |
| Green SLA | CI fails if estimated CO2 budget for the PR exceeded |
| Continuous learning | Model retrained on accepted vs. rejected fix suggestions |
| Webhook integrations | Slack, JIRA, GitHub Issues on violation threshold crossed |
| Ollama self-hosted LLM | Air-gapped enterprise option for AI fix |

---

## Definition of Done (all phases)

| Gate | Requirement |
|---|---|
| Test | ≥95% coverage on new code paths |
| Lint | 0 flake8 errors in touched files |
| Opt | No O(n²) unless formally justified |
| Sec | Input sanitized; no shell injection, no raw SQL, no path traversal |
