# Release Notes

## [v0.7.0] - Consolidation & Quality
### Added
- **New Python Rules**: Added 3 new rules: `unnecessary_comprehension`, `numpy_sum_vs_python_sum`, `subprocess_run_without_timeout`.
- **New JavaScript Rules**: Added 2 new rules: `console_time` (remove debug), `inner_html` (security/perf).
- **CLI Refactor**: Modularized CLI into `src/cli/` package for better maintainability and extensibility.
- **Pre-commit Hooks**: Enhanced local pre-commit hooks for robustness and better DX.

## [Unreleased]
### Added
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

## v0.6.2 - Architecture & Security Update (Consolidated Batch)

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
