# Product Backlog

## Phase 2: Action & Expansion (Current)


### [EPIC-03] LLM Integration (Autonomous Fixer)
*Goal: Implement autonomous fixer using LLM integration.*
- [LLM-001] | Design LLM Interface & Provider Abstraction | INDEPENDENT | DONE
- [LLM-002] | Implement Mock LLM Provider for Testing | BLOCKS-LLM-003 | DONE
- [LLM-003] | Implement OpenAI API Provider | INDEPENDENT | DONE
- [LLM-004] | Implement Token Usage Logic (Cost estimation per model) | INDEPENDENT | TODO
- [LLM-005] | Implement Rate Limiting Logic (Token bucket) | INDEPENDENT | TODO
- [LLM-006] | Implement Rate Limiting Config | BLOCKS-LLM-005 | TODO
- [LLM-007] | LLM CLI command `fix-ai` (Core logic) | INDEPENDENT | TODO
- [LLM-008] | LLM CLI command `fix-ai` (Prompt integration) | BLOCKS-LLM-007 | TODO
- [LLM-009] | LLM CLI command `fix-ai` (Diff output) | BLOCKS-LLM-008 | TODO
- [LLM-010] | Prompt Engineering for Python Loop Fix | INDEPENDENT | TODO
- [LLM-011] | Prompt Engineering for Python IO Fix | INDEPENDENT | TODO
- [LLM-012] | Prompt Engineering for Python Logic Fix | INDEPENDENT | TODO
- [LLM-013] | Prompt Engineering for JS Loop Fix | INDEPENDENT | TODO
- [LLM-014] | Prompt Engineering for JS DOM Fix | INDEPENDENT | TODO
- [LLM-015] | Integration Test: OpenAI Mock | INDEPENDENT | TODO
- [LLM-016] | Integration Test: Token Logic | BLOCKS-LLM-004 | TODO
- [LLM-017] | Integration Test: Rate Limit Logic | BLOCKS-LLM-005 | TODO
- [LLM-018] | Security Review: Prompt Injection | INDEPENDENT | TODO
- [LLM-019] | Security Review: Generated Code Sandbox | INDEPENDENT | TODO

### [EPIC-04] Advanced Reporting
*Goal: Enhance reporting capabilities with HTML/CSV improvements and PDF support.*
- [REP-001] | PDF Export: Install WeasyPrint | INDEPENDENT | TODO
- [REP-002] | PDF Export: Report Template (HTML/CSS) | BLOCKS-REP-001 | TODO
- [REP-003] | PDF Export: Chart rendering (static image gen) | BLOCKS-REP-002 | TODO
- [REP-004] | PDF Export: Layout logic | BLOCKS-REP-003 | TODO
- [REP-005] | CSV Export: Add violation line number | INDEPENDENT | TODO
- [REP-006] | CSV Export: Add violation snippet | INDEPENDENT | TODO
- [REP-007] | CSV Export: Add remediation suggestion | INDEPENDENT | TODO
- [REP-008] | HTML Report: Add interactive chart (Chart.js integration) | INDEPENDENT | TODO
- [REP-009] | HTML Report: Add filtering (JS) | INDEPENDENT | TODO
- [REP-010] | HTML Report: Add search (JS) | INDEPENDENT | TODO
- [REP-011] | JSON Export: Schema definition (Pydantic) | INDEPENDENT | TODO
- [REP-012] | JSON Export: Validation logic | BLOCKS-REP-011 | TODO
- [REP-013] | JSON Export: Metadata fields (version, timestamp) | BLOCKS-REP-011 | TODO
- [REP-014] | JSON Export: Unit Tests | BLOCKS-REP-011 | TODO
- [REP-015] | PDF Export: Integration Test | BLOCKS-REP-004 | TODO

### [EPIC-05] CI/CD GitHub Action V2
*Goal: Deepen CI/CD integration with a robust GitHub Action.*
- [CI-001] | Docker Action: Dockerfile creation | INDEPENDENT | TODO
- [CI-002] | Docker Action: Entrypoint script | BLOCKS-CI-001 | TODO
- [CI-003] | GitHub Action: `action.yml` metadata | INDEPENDENT | TODO
- [CI-004] | GitHub Action: Inputs definition | BLOCKS-CI-003 | TODO
- [CI-005] | PR Comment Bot: GitHub API integration | INDEPENDENT | TODO
- [CI-006] | PR Comment Bot: Diff parsing | INDEPENDENT | TODO
- [CI-007] | PR Comment Bot: Comment posting logic | BLOCKS-CI-005 | TODO
- [CI-008] | Fail Logic: Threshold config | INDEPENDENT | TODO
- [CI-009] | Fail Logic: Exit code handling | BLOCKS-CI-008 | TODO
- [CI-010] | Marketplace prep: Documentation | INDEPENDENT | TODO

### [EPIC-06] Performance Optimization
*Goal: Ensure the tool remains lightweight and fast.*
- [GO-009] | Go Performance Benchmark | INDEPENDENT | TODO
- [PERF-001] | Profile Scanner: cProfile setup | INDEPENDENT | TODO
- [PERF-002] | Profile Scanner: Identify bottlenecks | BLOCKS-PERF-001 | TODO
- [PERF-003] | Optimize Query: Review Python queries | INDEPENDENT | TODO
- [PERF-004] | Optimize Query: Review JS queries | INDEPENDENT | TODO
- [PERF-005] | Parallel Processing: Multiprocessing pool tuning | INDEPENDENT | TODO
- [PERF-006] | Parallel Processing: Chunk size tuning | BLOCKS-PERF-005 | TODO
- [PERF-007] | Memory Reduction: Generator usage review | INDEPENDENT | TODO
- [PERF-008] | Memory Reduction: Tree-sitter tree disposal | INDEPENDENT | TODO
- [PERF-009] | Result Caching: Disk cache implementation | INDEPENDENT | TODO
- [PERF-010] | Result Caching: In-memory LRU cache | INDEPENDENT | TODO

### [EPIC-07] Security Hardening
*Goal: Meet DoD security requirements.*
- [SEC-001] | Dependency Audit: Run `pip-audit` | INDEPENDENT | TODO
- [SEC-002] | Dependency Upgrade: Bump versions | BLOCKS-SEC-001 | TODO
- [SEC-003] | Input Sanitization: CLI args review | INDEPENDENT | TODO
- [SEC-004] | Input Sanitization: API payload validation | INDEPENDENT | TODO
- [SEC-005] | Secrets Detection: Rule implementation (Regex) | INDEPENDENT | TODO
- [SEC-006] | Secrets Detection: Rule implementation (Entropy) | BLOCKS-SEC-005 | TODO
- [SEC-007] | Hardcoded Password: Rule implementation | INDEPENDENT | TODO
- [SEC-008] | OWASP Top 10: Mapping review | INDEPENDENT | TODO
- [SEC-009] | Security Headers: API middleware | INDEPENDENT | TODO
- [SEC-010] | Rate Limiting: API middleware | INDEPENDENT | TODO

### [EPIC-08] Telemetry & Metrics
*Goal: Provide transparent metrics on tool usage and impact.*
- [TEL-001] | Telemetry System: Data schema design | INDEPENDENT | TODO
- [TEL-002] | Telemetry System: Local storage logic | BLOCKS-TEL-001 | TODO
- [TEL-003] | Opt-in Mechanism: CLI flag | INDEPENDENT | TODO
- [TEL-004] | Opt-in Mechanism: Config file setting | BLOCKS-TEL-003 | TODO
- [TEL-005] | Metric Collection: Rule hit counters | INDEPENDENT | TODO
- [TEL-006] | Metric Collection: Scan duration timer | INDEPENDENT | TODO
- [TEL-007] | Metric Collection: Error tracking | INDEPENDENT | TODO
- [TEL-008] | Dashboard View: Telemetry tab UI | BLOCKS-TEL-002 | TODO
- [TEL-009] | Dashboard View: Telemetry charts | BLOCKS-TEL-008 | TODO
- [TEL-010] | Anonymization: Data scrubbing logic | BLOCKS-TEL-001 | TODO

### [EPIC-09] IDE Plugins (Prep)
*Goal: Prepare for Phase 3 IDE integration.*
- [IDE-001] | VS Code Ext: Project scaffold | INDEPENDENT | TODO
- [IDE-002] | LSP Server: Basic protocol implementation | INDEPENDENT | TODO
- [IDE-003] | LSP Server: Initialize handshake | BLOCKS-IDE-002 | TODO
- [IDE-004] | LSP Server: Text document sync | BLOCKS-IDE-003 | TODO
- [IDE-005] | LSP Server: Diagnostics publishing | BLOCKS-IDE-004 | TODO
- [IDE-006] | Connect Scanner: CLI wrapper for LSP | BLOCKS-IDE-005 | TODO
- [IDE-007] | Syntax Highlighting: Grammar definition | INDEPENDENT | TODO
- [IDE-008] | Quick Fix: Code action provider | BLOCKS-IDE-005 | TODO
- [IDE-009] | VS Code Ext: Settings page | BLOCKS-IDE-001 | TODO
- [IDE-010] | VS Code Ext: Output channel logging | BLOCKS-IDE-001 | TODO

### [EPIC-10] Configuration Management
*Goal: Enhance dynamic configuration capabilities.*
- [CFG-001] | Remote Config: URL fetcher | INDEPENDENT | TODO
- [CFG-002] | Remote Config: Caching logic | BLOCKS-CFG-001 | TODO
- [CFG-003] | Severity Override: Config parsing logic | INDEPENDENT | TODO
- [CFG-004] | Severity Override: Rule application logic | BLOCKS-CFG-003 | TODO
- [CFG-005] | JSON Schema: Define schema.json | INDEPENDENT | TODO
- [CFG-006] | JSON Schema: Validate config on load | BLOCKS-CFG-005 | TODO
- [CFG-007] | Merge Configs: Deep merge utility | INDEPENDENT | TODO
- [CFG-008] | Merge Configs: Precedence logic (CLI > Local > Global) | BLOCKS-CFG-007 | TODO
- [CFG-009] | CLI Generator: `init` command logic | INDEPENDENT | TODO
- [CFG-010] | CLI Generator: Template creation | BLOCKS-CFG-009 | TODO
