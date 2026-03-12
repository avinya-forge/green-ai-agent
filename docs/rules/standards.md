# Development Standards

## 🛠️ Codebase Structure

We follow a modular `src` layout. All source code resides in `src/`.

```
green-ai-agent/
├── src/                      # Source code (all modules)
├── tests/                    # Test files (pytest)
├── rules/                    # YAML rule definitions (per language)
├── docs/                     # Documentation (planning, architecture, testing, release, rules)
├── output/                   # ALL generated reports (CSV, HTML, emissions, logs)
├── data/                     # Data files (CSVs from scanning)
└── [root files]              # Only: README.md, requirements.txt, config files
```

### 🚫 Copilot & File Creation Policy

> **STRICT RULE:** No new files or folders may be created in this repository by Copilot or any automated tool without explicit USER permission. All documentation, code, and configuration changes must be reviewed and approved by a human user. Any attempt to auto-generate files, markdowns, or logs outside the approved structure will be rejected.

- All outputs must go to the `output/` folder.
- Only files following the `IO_SSOT` mapping are allowed in `docs/`.
- No new markdown or config files may be created in any folder unless approved by the USER.
- All code, test, and rule files must follow the structure in this README.
- Any violation of this policy will be reverted.

## 📏 Rule Definitions

Rules are defined in YAML files within the `rules/` directory (e.g., `rules/python.yaml`).

### Rule Structure
Each rule must contain the following fields:

```yaml
- id: no_infinite_loops              # Unique snake_case identifier
  name: No Infinite Loops            # Human-readable name
  description: Infinite loops...     # Detailed description
  severity: critical                 # critical, high, medium, low, info
  languages: [python]                # List of applicable languages
  pattern: |                         # Regex or AST pattern description
    while\s*\(\s*[Tt]rue\s*\)
  remediation: Add termination...    # How to fix the issue
  source: GSF                        # Source standard (GSF, ecoCode, etc.)
  tags: [performance, energy]        # Categorization tags
```

## 📝 Coding Conventions

### Python (PEP 8+)

- **Imports**: Always use absolute imports rooted at `src`.
  ```python
  # ✅ CORRECT
  from src.core.export import CSVExporter
  from src.core.scanner import Scanner

  # ❌ WRONG
  from export import CSVExporter
  ```

- **Path Handling**: Use `pathlib.Path` for cross-platform compatibility.
  ```python
  # ✅ CORRECT
  from pathlib import Path
  output_dir = Path(__file__).parent.parent.parent / 'output'

  # ❌ WRONG - String paths, platform-specific
  output_file = 'output\\report.csv'
  ```

- **Type Hints**: Use type hints for function arguments and return values.
  ```python
  def analyze_complexity(code: str) -> dict[str, int]:
      ...
  ```

- **Output Files**: All generated files must be saved in the `output/` directory.
  ```python
  # ✅ CORRECT - Uses output folder
  from src.core.export import CSVExporter
  exporter = CSVExporter()  # Defaults to output/green-ai-report.csv

  # ❌ WRONG - Creates file in root
  exporter = CSVExporter('green-ai-report.csv')
  ```

- **Logging**: All logs must be directed to `output/logs/app.log`.
  ```python
  # ✅ CORRECT - Logs to output/logs/
  import logging
  from pathlib import Path
  logs_dir = Path(__file__).parent.parent.parent / 'output' / 'logs'
  logs_dir.mkdir(parents=True, exist_ok=True)
  handler = logging.FileHandler(logs_dir / 'app.log')

  # ❌ WRONG - Logging to root
  handler = logging.FileHandler('app.log')
  ```

### JavaScript / TypeScript (If applicable)

- Use strict mode (`'use strict';`).
- Prefer `const` over `let`, avoid `var`.
- Use async/await for asynchronous operations.

## 🧪 Testing Strategy

- **Framework**: Use `pytest`.
- **Location**: `tests/` directory.
- **Coverage**: Maintain >80% code coverage. Target 85%+.
- **Mocking**: Use `unittest.mock` or `pytest-mock` for external dependencies (network, file I/O).
- **Fixtures**: Use `conftest.py` for shared fixtures.
- **Rule Testing**: New rules must be verified in `tests/test_rules.py` or via integration tests.

Run tests:
```bash
pytest tests/ -v
```

## 📦 Data Models

- Use `pydantic` for data validation and serialization.
- Ensure strict typing for all models.

## 🧹 Maintenance & Folder Policy

- All cache, build, and temporary folders (e.g., `.pytest_cache/`, `__pycache__/`, `data/`) are deleted as part of regular maintenance and must not be committed or recreated.
- Only the following folders are allowed at the top level: `src/`, `tests/`, `rules/`, `docs/`, `output/`, `.github/`.
- All module documentation should be merged into the main README unless it is essential for developer onboarding or rule explanation.
- If a file or folder is not referenced in code or documentation, it will be deleted.

## 🔄 Workflow

1. **Pull Request**: Create a PR for significant changes (>200 LOC or 5 tasks).
2. **Review**: All PRs must be reviewed.
3. **Merge**: Merge only when all tests pass and coverage is maintained.
4. **Release**: Update `docs/release/release-notes.md` with user-facing changes.

## 🛡️ Pre-commit Hooks

We use pre-commit hooks to ensure code quality and prevent violations from being committed.

### Installation

Run the installation script to set up the hooks:

```bash
./scripts/install_hooks.sh
```

### Checks Performed

The pre-commit hook performs the following checks:
1.  **File Placement**: Ensures no CSV/HTML files are in the root directory (must be in `output/`).
2.  **Documentation**: Enforces strict allowlist for files in `docs/`.
3.  **Imports**: Checks for correct absolute imports (rooted at `src`).
4.  **Auto-Scan**: Scans staged Python files for green software violations using `green-ai scan`. If violations are found, the commit is blocked.

### Bypassing (Not Recommended)

If you must bypass the checks (e.g., for work-in-progress commits), use:

```bash
git commit --no-verify
```
# Green-AI Agent Standards

## Coding Conventions
All components in the `Green-AI` architecture must follow strict modularity. There should be NO "one-off" components or hacks. Every new capability must be added cleanly according to the following principles.

1. **Red/Green/Refactor Workflow:**
   - The developer must first write a failing test demonstrating the defect or requirement (`Red`).
   - Write the simplest code necessary to pass the test (`Green`).
   - Refactor the code for better optimization, maintainability, and clean design (`Refactor`).

2. **Testing Requirements (95% Coverage Rule):**
   - We require a minimum of 95% test compliance verified via the full test suite (`python3 -m pytest`).
   - Before submission, all unit tests and End-to-End tests must pass.

3. **Performance Rules (O(n) / O(1)):**
   - Algorithms must be strictly written with optimizations in mind. O(1) hashing/caching should be preferred when caching state, and iteration should at most be O(n). Multi-layered nesting > 3 should be avoided or refactored.

4. **Schema-First API Rule:**
   - No API implementation or endpoint is permitted to go to production without a verified `docs/api/swagger.yaml` structure.
   - Mock Data Schema must be written to `docs/api/mock_data.json` alongside API creation.

5. **Pruning Mandate:**
   - Every coding session must identify and remove any reachable dead code or redundancies using standard static analyzers (e.g., `vulture`). Unused methods, imports, and variables must be stripped to maintain a "Cleanliness Score".
