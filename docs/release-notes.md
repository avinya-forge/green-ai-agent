# Release Notes

## [v0.8.0-alpha] - CI/CD & Telemetry

### Added
- **GitHub Action**: Implemented a Docker-based GitHub Action (`action.yml`) to run Green-AI in CI/CD pipelines (CI-001, CI-002, CI-003, CI-004).
- **Telemetry Core**: Implemented `TelemetryService` and data schemas (`ScanMetrics`) to collect usage and performance metrics (TEL-001, TEL-005, TEL-006, TEL-007).
- **Telemetry Export**: Added functionality to export telemetry events to JSON files for debugging and analysis.
- **Telemetry Persistence**: Implemented local storage for telemetry events (`output/telemetry.jsonl`) with anonymization support (TEL-002, TEL-010).
- **Telemetry CLI**: Added `--telemetry` flag to `scan` command and configuration support for opting out (TEL-003, TEL-004).
- **Enhanced Entropy Detection**: Improved secrets detection to recursively scan lists, dictionaries, and tuples for high-entropy strings (SEC-006).
- **Severity Overrides**: Verified and ensured configuration-based severity overrides are correctly applied during scans (CFG-004).
- **Config Templates**: Enhanced `green-ai init` with a comprehensive configuration template including telemetry settings (CFG-010).
- **API Security**: Implemented Security Headers (CSP, HSTS, X-Frame-Options) and Rate Limiting middleware for the dashboard API (SEC-009, SEC-010).
- **Cache Verification**: Verified and tested Disk Cache implementation for scan results, ensuring faster re-scans (PERF-009).
- **CI/CD Thresholds**: Added `--fail-on` flag to `scan` command to exit with error code if violations of specific severity are found (CI-008, CI-009).
- **PR Comment Bot**: Added `ci report` command to post scan results as comments on GitHub Pull Requests, including diff-aware filtering (CI-005, CI-006, CI-007).
- **LLM Security**: Added comprehensive security tests for prompt injection and code sandbox verification (LLM-018, LLM-019).
- **Telemetry Dashboard**: Verified and finalized the Telemetry Dashboard UI and API integration (TEL-008, TEL-009).

## [v0.7.0] - Consolidation & Quality

### Vaulted Epics
#### [EPIC-01] Java Language Support
- [JAVA-001] | Java AST Parser Integration | INDEPENDENT | DONE
- [JAVA-002] | Java Rule Engine Implementation | BLOCKS-JAVA-003 | DONE
- [JAVA-003] | Implement `System.out.println` detection rule | INDEPENDENT | DONE
- [JAVA-004] | Implement Empty Catch Block detection rule | INDEPENDENT | DONE
- [JAVA-005] | Java Test Suite & Coverage | BLOCKS-JAVA-006 | DONE

#### [EPIC-02] Go Language Support
- [GO-001] | Research Go AST libraries & Tree-sitter bindings | INDEPENDENT | DONE
- [GO-002] | Implement Go Language Detector Class | BLOCKS-GO-003 | DONE
- [GO-003] | Add Go Tree-sitter integration | BLOCKS-GO-004 | DONE
- [GO-004] | Implement Go "Empty Block" Rule | INDEPENDENT | DONE
- [GO-005] | Implement Go Test Suite | BLOCKS-GO-006 | DONE
- [GO-006] | CLI Integration for Go scanning | INDEPENDENT | DONE
- [GO-007] | Go End-to-End Test Scenario | INDEPENDENT | DONE
- [GO-008] | Go specific Documentation | INDEPENDENT | DONE
- [GO-010] | Release Go Support Beta | BLOCKS-GO-009 | DONE
- [GO-011] | Implement `string_concatenation_in_loop` Rule | INDEPENDENT | DONE

### Added
- **PDF Export**: Added support for exporting scan results to PDF using WeasyPrint (`--export pdf`) (REP-001, REP-002, REP-004).
- **JS Secrets Detection**: Added `hardcoded_secret` rule for JavaScript/TypeScript to detect potential sensitive data in code (SEC-005).
- **Configuration Init**: Added `green-ai init` CLI command to easily generate configuration files (CFG-009).
- **Deep Merge Utility**: Implemented robust recursive dictionary merging for configuration layering (CFG-007).
- **Config Validation**: Migrated configuration validation to Pydantic models for stricter type safety and schema enforcement (CFG-005, CFG-006).
- **Security Rules**: Added detection for hardcoded secrets and AWS keys in Python code (SEC-005, SEC-007).
- **JSON Export Schema**: Implemented robust Pydantic schemas for JSON export validation (REP-011).
- **JSON Validation**: Added validation logic to `JSONExporter` to ensure data consistency (REP-012).
- **Export Metadata**: Standardized metadata fields in JSON export (REP-013).
- **Performance Profiling**: Added `--perf-profile` flag to `scan` command for internal cProfile analysis (PERF-001).
- **Bottleneck Analysis**: Conducted initial performance analysis and documented findings in `docs/performance_analysis.md` (PERF-002).
- **LLM CLI Enhancements**: Added colored diff view (`difflib`) to `fix-ai` command for verifying changes before applying, plus robust file patching logic.
- **Prompt Engineering**: Implemented specialized prompts for Python/JS loops, IO, and logic optimization in `src/core/llm/prompts.py`.
- **CSV Export Improvements**: Added `snippet` and `remediation` columns to CSV export, providing more context for violations.
- **Integration Tests**: Added comprehensive integration tests for LLM provider, token usage, and rate limiting.
- **Go Support**: Added support for Go scanning (`.go`) using `tree-sitter-go`.
- **New Go Rules**: Added `formatted_print`, `empty_block`, and `infinite_loop` rules.
- **Java Support**: Added support for Java scanning (`.java`) using `tree-sitter-java`.
- **New Java Rules**: Added `excessive_logging`, `blocking_io`, `string_concatenation_in_loop`, and `empty_block` rules.
- **TypeScript Support**: Added comprehensive support for TypeScript (`.ts`, `.tsx`) analysis using `tree-sitter-typescript`.
- **New TypeScript Rules**: Added `any_type_usage` and `prefer_const_enum` rules, plus inherited all JavaScript green coding rules.
- **Remediation Engine**: Implemented a robust, CST-based (LibCST) remediation engine for Python. Supports automated refactoring for `inefficient_loop`, `open_without_context`, `range_len_usage`, and `unnecessary_comprehension`.
- **Automated Fixes**: Added `src/core/remediation/` package replacing legacy regex-based `AISuggester`.
- **Refactoring Transformers**: Implemented 4 key CST transformers: `ListAppendToComprehension`, `ContextManagerTransformer`, `EnumerateTransformer`, `UnnecessaryComprehensionTransformer`.
- **E2E Dashboard Testing**: Added comprehensive end-to-end tests for the dashboard UI and API interactions.
- **Standards Sync**: Implemented `sync_standards` to fetch latest green software standards from remote sources (GSF, ecoCode).
- **Analyzer Robustness**: Added unit tests for `CodeComplexityAnalyzer` and `EmissionAnalyzer` covering edge cases.
- **Calibration UI**: Added system calibration button to the landing page and exposed `GET /api/calibrate` endpoint to support UI integration.
- **Domain Models**: Implemented Pydantic models for `Project` and `Violation` to ensure data consistency (BUG-004).
- **CLI Fix Command**: Added `fix_all` capability to `scan` command using `RemediationEngine`.
- **JUnit XML Export**: Added `xml` export format to `scan` command for CI integration.
- **New Python Rules**: Added 3 new rules: `unnecessary_comprehension`, `numpy_sum_vs_python_sum`, `subprocess_run_without_timeout`.
- **New JavaScript Rules**: Added 2 new rules: `console_time` (remove debug), `inner_html` (security/perf).
- **CLI Refactor**: Modularized CLI into `src/cli/` package for better maintainability and extensibility.
- **Pre-commit Hooks**: Enhanced local pre-commit hooks for robustness and better DX.
- **Mock LLM Provider**: Implemented `MockLLMProvider` for testing LLM integration without API calls.
- **LLM Integration**: Implemented comprehensive LLM infrastructure including `LLMProvider`, `OpenAIProvider`, and `MockLLMProvider`.
- **LLM CLI Command**: Added `fix-ai` command to interactively fix violations using LLM suggestions (Preview Mode).
- **Rate Limiting**: Implemented `TokenBucketRateLimiter` to enforce TPM and RPM limits for LLM API calls.
- **Cost Tracking**: Added `TokenUsage` tracking to estimate costs of LLM operations.
- **Configuration**: Added `llm` section to `.green-ai.yaml` for provider selection and rate limit configuration.
- **Input Sanitization**: Implemented strict validation for CLI arguments including file paths, project names, and Git URLs to prevent injection and traversal attacks (SEC-003).

### Changed
- **Scanner Refactor**: Refactored `src/core/scanner.py` into a modular package `src/core/scanner/` with `main.py`, `worker.py`, and `discovery.py`.
- **Export Refactor**: Refactored `src/core/export.py` into `src/core/export/` package.
- **Project Manager Reliability**: Enhanced `ProjectManager` to robustly handle edge cases and default values (e.g., branch defaulting).
- **Eventlet Migration**: Completed migration from Flask/Eventlet to FastAPI/Uvicorn (Phase 4). Replaced `dashboard_app.py` with `app_fastapi.py`. Updated `server.py` to use Uvicorn. Updated `requirements.txt`.
- **Server Architecture**: Refactored `src/ui/server.py` to use Uvicorn ASGI server.
- **ProjectDTO Refactor**: Updated `ProjectDTO` to use strict Pydantic `ViolationDetails` model instead of `Dict` for better type safety and consistency.

### Fixed
- **API JSON Responses**: Refactored `api_charts` and `api_results` endpoints to robustly handle empty results using `jsonify` and ensured correct `application/json` Content-Type (verified by new tests).
- **Template Error Handling**: Robustly handle missing templates and prevent SSTI/XSS in error messages by escaping content and using raw blocks (TASK-001).
- **Pre-commit Hook**: Fixed `.git_hooks_pre-commit.sh` to correctly handle `BACKLOG.md` casing and allow standard documentation files, improving developer experience.

### Documentation
- **Standards & Vision**: Updated `docs/vision.md` and `docs/development-standards.md` to reflect current capabilities (v0.6.1) and rule definitions.
- **Migration Plan**: Added comprehensive `docs/eventlet-migration.md` outlining the roadmap to replace Eventlet with FastAPI/Uvicorn.

## [v0.6.2] - Architecture & Security Update (Consolidated Batch)
### 🏗️ Architectural Refactor
- **Modular Detectors**: Split the monolithic `src/core/detectors.py` into a modular package `src/core/detectors/` with separate Python and JavaScript detectors. This improves maintainability and extensibility.

### 🛡️ New Detection Rules (Python)
- **Blocking I/O in Async**: Detects `time.sleep`, `requests.*`, and `open()` calls inside `async def` functions, which can block the event loop.
- **SQL Injection Risk**: Basic heuristic to detect f-strings or string formatting used directly in `cursor.execute()`.
- **Requests Timeout**: Warns if `requests.get/post/etc` are called without a `timeout` argument, preventing potential hangs.
- **Empty Blocks**: Detects empty loops, if-statements, and try-except blocks that should be implemented or removed.

### 🌐 New Detection Rules (JavaScript)
- **Empty Blocks**: Detects empty statement blocks (`{}`) in JavaScript code.

### ⚙️ Infrastructure
- **CI/CD**: Added GitHub Actions workflow (`.github/workflows/ci.yml`) to automatically run tests (`pytest`) and linting (`flake8`) on push and PR.

## [v0.6.1] - 2026-02-11
### Added
- **JavaScript AST Engine**: Replaced legacy regex-based detectors with robust Tree-sitter AST analysis for JavaScript, covering loops, DOM manipulation, and deprecated APIs.

## [v0.6.0] - 2026-02-09
### Added
- **New Detection Rules**: Added 7 new Python rules: `eager_logging_formatting`, `mutable_default_argument`, `any_all_list_comprehension`, `bare_except`, `unnecessary_generator_list`, `string_concatenation_in_loop`, `inefficient_dictionary_iteration`.
- **Performance**: Implemented multiprocessing scanner for faster file analysis.

### Fixed
- **Deprecations**: Replaced deprecated `datetime.utcnow()` with `datetime.now(datetime.UTC)`.

## [v0.5.0-beta] - 2026-01-29
### Added
- **Dynamic YAML Rule System**: Rules are now loaded from YAML files, enabling easier updates without code changes.
- **Advanced AST Detection**: Implemented sophisticated detection for redundant computations in loops (e.g., `len()`, `range()` in Python).
- **Standardized Logging**: Centralized logging system now records all tool operations to `output/logs/app.log`.

### Fixed
- **Scanner Performance**: Optimized file discovery to respect configuration ignore patterns (skipping `.venv`, `node_modules`, etc.).
- **Self-Scan Bottleneck**: Reduced self-scan execution time by ~85%.
- **Type Mismatch Fix**: Updated `Project` object usage in `server.py` and tests to fix 14 failures (BUG-001).
- **Missing Metric Function**: Renamed and moved `calculate_average_grade` to `src/utils/metrics.py` (BUG-002).
- **Project Data Model**: Added `violations` field to `Project` class for detailed tracking (BUG-005).
- **Test Configuration**: Updated `test_rules.py` and `test_standards.py` to use correct fields and dummy config (BUG-006).
- **Missing Test Files**: Added `tests/simple_test.py` for integration testing (BUG-007).
- **Code Cleanliness**: Removed deprecated `ast.NameConstant` usage.
- **New Rules**: Added `deep_recursion` and `inefficient_lookup` detection rules.

---

## [v0.4.0] - 2026-01-28
### Added
- **Multi-Project Support**: Ability to register and scan multiple projects.
- **Export Capabilities**: Added CSV and HTML reporting formats.
- **Git Integration**: Direct scanning of repositories via Git URL.
- **Web Dashboard**: New UI for visualizing scan results across projects.

---

## [v0.3.0] - 2026-01-26
### Added
- **Configuration System**: Added `.green-ai.yaml` for custom scan settings.
- **Rule Customization**: Enable/disable specific rules via config or CLI.
- **Initial CLI**: Core `scan` command for Python and JavaScript.

---

## [v0.1.0] - 2026-01-20
### Added
- **Core Engine**: Initial AST-based scanner for basic Python and JavaScript violations.
- **Emissions Modeling**: Basic CO2 impact estimation based on static analysis.
