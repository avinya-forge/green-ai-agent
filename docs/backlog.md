# Product Backlog

## Phase 2: Action & Expansion (Current)

### [EPIC-01] Java Language Support (Completion)
*Goal: Complete the support for Java scanning, ensuring parity with Python/JS.*
- [JAVA-001] | Java AST Parser Integration | INDEPENDENT | TODO
- [JAVA-002] | Java Rule Engine Implementation | BLOCKS-JAVA-003 | TODO
- [JAVA-003] | Implement `System.out.println` detection rule | INDEPENDENT | TODO
- [JAVA-004] | Implement Empty Catch Block detection rule | INDEPENDENT | TODO
- [JAVA-005] | Java Test Suite & Coverage | BLOCKS-JAVA-006 | TODO

### [EPIC-02] Go Language Support
*Goal: Expand language support to Go as per roadmap.*
- [GO-001] | Research Go AST libraries & Tree-sitter bindings | INDEPENDENT | TODO
- [GO-002] | Implement Go Language Detector Class | BLOCKS-GO-003 | TODO
- [GO-003] | Add Go Tree-sitter integration | BLOCKS-GO-004 | TODO
- [GO-004] | Implement Go "Empty Block" Rule | INDEPENDENT | TODO
- [GO-005] | Implement Go Test Suite | BLOCKS-GO-006 | TODO
- [GO-006] | CLI Integration for Go scanning | INDEPENDENT | TODO
- [GO-007] | Go End-to-End Test Scenario | INDEPENDENT | TODO
- [GO-008] | Go specific Documentation | INDEPENDENT | TODO
- [GO-009] | Go Performance Benchmark | INDEPENDENT | TODO
- [GO-010] | Release Go Support Beta | BLOCKS-GO-009 | TODO

### [EPIC-03] LLM Integration (Autonomous Fixer)
*Goal: Implement autonomous fixer using LLM integration.*
- [LLM-001] | Design LLM Interface & Provider Abstraction | INDEPENDENT | TODO
- [LLM-002] | Implement Mock LLM Provider for Testing | BLOCKS-LLM-003 | TODO
- [LLM-003] | Implement OpenAI API Provider | INDEPENDENT | TODO
- [LLM-004] | Prompt Engineering for Python Fixes | INDEPENDENT | TODO
- [LLM-005] | Prompt Engineering for JavaScript Fixes | INDEPENDENT | TODO
- [LLM-006] | Implement Rate Limiting & Cost Control Logic | INDEPENDENT | TODO
- [LLM-007] | Implement Token Usage Estimation | INDEPENDENT | TODO
- [LLM-008] | Create LLM CLI Command `fix-ai` | BLOCKS-LLM-009 | TODO
- [LLM-009] | LLM Integration Test Suite | INDEPENDENT | TODO
- [LLM-010] | Security Review for LLM Generated Code | INDEPENDENT | TODO

### [EPIC-04] Advanced Reporting
*Goal: Enhance reporting capabilities with HTML/CSV improvements and PDF support.*
- [REP-001] | HTML Report Styling Modernization | INDEPENDENT | TODO
- [REP-002] | Add Interactive Charts to HTML Report | INDEPENDENT | TODO
- [REP-003] | Implement PDF Export using WeasyPrint or ReportLab | INDEPENDENT | TODO
- [REP-004] | CSV Export: Add Detailed Violation Metadata | INDEPENDENT | TODO
- [REP-005] | JSON Export: Implement Schema Validation | INDEPENDENT | TODO

### [EPIC-05] CI/CD GitHub Action V2
*Goal: Deepen CI/CD integration with a robust GitHub Action.*
- [CI-001] | Create Docker-based GitHub Action | INDEPENDENT | TODO
- [CI-002] | Add PR Commenting Bot capability | INDEPENDENT | TODO
- [CI-003] | Implement "Fail on New Violations" Logic | INDEPENDENT | TODO
- [CI-004] | Add Performance Regression Check in CI | INDEPENDENT | TODO
- [CI-005] | Publish Action to GitHub Marketplace | INDEPENDENT | TODO

### [EPIC-06] Performance Optimization
*Goal: Ensure the tool remains lightweight and fast.*
- [PERF-001] | Profile Scanner Core for Bottlenecks | INDEPENDENT | TODO
- [PERF-002] | Optimize Tree-sitter Query Execution | INDEPENDENT | TODO
- [PERF-003] | Tune Parallel Processing Parameters | INDEPENDENT | TODO
- [PERF-004] | Reduce Memory Footprint during Large Scans | INDEPENDENT | TODO
- [PERF-005] | Implement Result Caching Mechanism | INDEPENDENT | TODO

### [EPIC-07] Security Hardening
*Goal: Meet DoD security requirements.*
- [SEC-001] | Perform Dependency Audit & Upgrade | INDEPENDENT | TODO
- [SEC-002] | Review Input Sanitization in CLI & API | INDEPENDENT | TODO
- [SEC-003] | Implement Secrets Detection Rule | INDEPENDENT | TODO
- [SEC-004] | Implement Hardcoded Password Rule | INDEPENDENT | TODO
- [SEC-005] | OWASP Top 10 Compliance Check | INDEPENDENT | TODO

### [EPIC-08] Telemetry & Metrics
*Goal: Provide transparent metrics on tool usage and impact.*
- [TEL-001] | Design Anonymous Telemetry System | INDEPENDENT | TODO
- [TEL-002] | Implement Opt-In Mechanism for Users | INDEPENDENT | TODO
- [TEL-003] | Collect Rule Hit Rates | INDEPENDENT | TODO
- [TEL-004] | Collect Scan Duration Statistics | INDEPENDENT | TODO
- [TEL-005] | Create Dashboard View for Local Telemetry | INDEPENDENT | TODO

### [EPIC-09] IDE Plugins (Prep)
*Goal: Prepare for Phase 3 IDE integration.*
- [IDE-001] | Create VS Code Extension Skeleton | INDEPENDENT | TODO
- [IDE-002] | Implement Basic LSP Server | INDEPENDENT | TODO
- [IDE-003] | Connect LSP to Green-AI Scanner | INDEPENDENT | TODO
- [IDE-004] | Implement Syntax Highlighting for Violations | INDEPENDENT | TODO
- [IDE-005] | Implement Quick Fix Action in VS Code | INDEPENDENT | TODO

### [EPIC-10] Configuration Management
*Goal: Enhance dynamic configuration capabilities.*
- [CFG-001] | Implement Remote Config Fetching (URL) | INDEPENDENT | TODO
- [CFG-002] | Allow Rule Severity Overrides in Config | INDEPENDENT | TODO
- [CFG-003] | Implement Config Validation Schema (JSON Schema) | INDEPENDENT | TODO
- [CFG-004] | Support Merging Multiple Config Files | INDEPENDENT | TODO
- [CFG-005] | Create CLI Config Generator Command | INDEPENDENT | TODO
