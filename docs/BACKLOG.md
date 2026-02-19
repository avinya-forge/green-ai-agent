# BACKLOG.md

## 📋 Next 10 Prioritized Microtasks

1. **[CORE] Implement Java Support**
    - Status: In-Progress - Green-AI-Agent-03
    - Goal: Add support for Java scanning (AST-based detection, rules, config).
    - Priority: High

## ✅ Completed Tasks

- **[CORE] Refactor Scanner & Implement CLI Fixes** (Status: Done)
    - Goal: Modularize Scanner, implement `fix_all`, add XML export.
    - Priority: High

- **[CORE] Implement Standards Sync** (Status: Done)
    - Goal: Fetch latest standards from online sources (GSF, ecoCode).
    - Priority: Medium

- **[QA] E2E Dashboard Testing (Sprint 4.2)** (Status: Done)
    - Goal: Automate UI verification.
    - Priority: Medium

- **[QA] Pre-commit Hooks Integration (Sprint 4.1)** (Status: Done)
    - Goal: Improved robustness and installation script for local hooks.
    - Priority: Medium

- **[CORE] CLI Refactor** (Status: Done)
    - Goal: Refactor `src/cli.py` into a modular package structure `src/cli/` with subcommands.
    - Priority: High

- **[CORE] New Python Rules** (Status: Done)
    - Goal: Added `unnecessary_comprehension`, `numpy_sum_vs_python_sum`, `subprocess_run_without_timeout`.
    - Priority: Medium

- **[CORE] New JavaScript Rules** (Status: Done)
    - Goal: Added `console_time`, `inner_html` detection.
    - Priority: Medium

- **[JULES] Fix BUG-003.1: Research Eventlet migration path** (Status: Done)
   - Goal: Prepare for eventlet deprecation (Created `docs/eventlet-migration.md`).
   - Priority: Medium

- **[CORE] Eventlet Migration - Phase 1 (Dependencies)** (Status: Done)
   - Goal: Update requirements (added new deps; legacy deps retained until Phase 4).
   - Priority: High

- **[CORE] Eventlet Migration - Phase 2 (FastAPI Scaffolding)** (Status: Done)
   - Goal: Create `app_fastapi.py` and initial ASGI setup.
   - Priority: High

- **[CORE] Eventlet Migration - Phase 3 (Port Routes)** (Status: Done)
   - Goal: Port all Flask routes to FastAPI endpoints.
   - Priority: Medium

- **[CORE] Eventlet Migration - Phase 4 (Switchover)** (Status: Done)
   - Goal: Update entry points, remove Flask code, and migrate tests.
   - Priority: Medium

- **[QA] Fix Pre-commit Hook** (Status: Done)
   - Goal: Update `.git_hooks_pre-commit.sh` to allow required documentation files.
   - Priority: Medium

- **[UI] Calibration UI Integration (Sprint 3.2)** (Status: Done)
   - Goal: Expose system calibration via Dashboard UI and API.
   - Priority: High

- **[CORE] Refactor Project Model (BUG-004.1)** (Status: Done)
   - Goal: Replace weak `Dict` types with strict Pydantic `ViolationDetails` model in `Project`.
   - Priority: High

- **[JULES] Refactor export logic** (Status: Done)
   - Goal: Deduplicate code in `api_export_csv` and `api_export_html`.
   - Priority: Low

- **[UI] Real-time Progress Bar (Sprint 3.1)** (Status: Done)
   - Goal: Integration of WebSockets for live status during scans.
   - Priority: High

- **[UI] Remediation Preview (Sprint 3.3)** (Status: Done)
   - Goal: Show suggested code diffs directly in the dashboard.
   - Priority: Medium

- **[JULES] Fix BUG-004.2: Add Pydantic models for validation** (Status: Done)
   - Goal: Ensure data integrity.
   - Priority: High

- **[JULES] Fix BUG-004.3: Create `ProjectDTO` for API responses** (Status: Done)
   - Goal: Standardize API outputs.
   - Priority: High

- **[JULES] Project Discovery & Doc Generation** (Status: Done)
   - Goal: specific `docs/vision.md` and `docs/development-standards.md`.
   - Priority: High (Initialization)

- **[CORE] Refactor Detectors Architecture** (Status: Done)
    - Goal: Split monolithic `src/core/detectors.py` into modular package `src/core/detectors/`.
    - Priority: High

- **[CORE] New Python Rule: Blocking I/O in Async** (Status: Done)
    - Goal: Detect `time.sleep`, `requests.*`, `open` inside `async def`.
    - Priority: High

- **[CORE] New Python Rule: Requests Timeout** (Status: Done)
    - Goal: Ensure `requests` calls have `timeout` argument.
    - Priority: High

- **[CORE] New Python Rule: SQL Injection (Basic)** (Status: Done)
    - Goal: Detect f-strings in `cursor.execute`.
    - Priority: High

- **[CORE] New Rule: Empty Blocks** (Status: Done)
    - Goal: Detect empty functions/classes/loops in Python & JS.
    - Priority: Medium

- **[CI] CI/CD Workflow** (Status: Done)
    - Goal: Create GitHub Actions workflow for automated testing.
    - Priority: High

---

## 🐛 Known Issues (P0 - Critical)

### BUG-003: Eventlet Deprecation Warning (FIXED)
- **Impact**: Future compatibility risk, deprecated dependency
- **Fix**: Migrated to FastAPI and Uvicorn
- **Status**: Fixed in Phase 4 Switchover

### BUG-004: Inconsistent Project Data Model
- **Impact**: Confusion between dict and object representations
- **Fix**: Implement Repository + DTO pattern
- **Effort**: 6h

---

## 📅 Roadmap Overview

### Phase 2: Carbon Efficiency, Rules, Quality & Scale (In Progress)
- **Sprint 2**: Advanced Rules & Performance [DONE]
- **Sprint 3**: Real-time Dashboard & Metrics [IN PROGRESS]
- **Sprint 4**: Quality & CI [TODO]

### Phase 3: Cloud & Enterprise (Planned)
- Cloud deployment
- Team collaboration

---

## 📦 Release History
- **v0.6.1**: JavaScript AST Engine
- **v0.6.0**: Performance & New Rules
- **v0.5.0-beta**: Carbon Efficiency & Dynamic Rules

## 📝 Planned Improvements (Sprint 4.4 - Next Batch)

- **[CORE] Implement TypeScript Support** (Status: Done)
    - Goal: Add support for `.ts` and `.tsx` files with specific rules (`any`, `enum`) and inherited JS rules.
    - Priority: High
