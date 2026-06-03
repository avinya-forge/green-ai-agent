# Project Backlog

## 1. High-Priority Granular Tasks (Immediate Execution)

| ID | Component | Task | Status |
|---|---|---|---|
| SAN-001 | Scanner | Fix `severity_override` logic in `worker.py` to respect config. | DONE |
| SAN-002 | Tests | Fix path resolution in `tests/test_xss_vulnerability.py` using absolute pathing. | DONE |
| SAN-003 | Scanner | Ensure `SyntaxError` in workers returns a specific 'syntax_error' issue ID. | DONE |
| QUAL-001a | Analyzer | Implement `CognitiveComplexityAnalyzer` AST visitor in `analyzer.py`. | DONE |
| QUAL-001b | Analyzer | Integrate cognitive complexity into `EmissionAnalyzer` and metrics. | DONE |
| SEC-001a | Detector | Refactor `PatternBasedDetector` to apply rules dynamically from YAML repository. | DONE |
| SEC-001b | Rules | Port 10+ OWASP security rules to `rules/python.yaml` and `rules/javascript.yaml`. | DONE |
| SEC-001c | Detector | Debug integrated scan failure for new security rules (Rules not detected in scan results). | DONE |

## 2. Technical Debt & Deep Cleaning

| ID | Component | Task | Status |
|---|---|---|---|
| CLEAN-001 | Detectors | Remove redundant regex patterns from `python_detector.py` (logic moved to PatternBasedDetector). | DONE |
| CLEAN-002 | Core | Standardize absolute imports in all touched files (from src.core...). | DONE |
| CLEAN-003 | Scanner | Resolve all `flake8` violations in `src/core/scanner/` and `src/core/detectors/`. | DONE |
| CLEAN-004 | Docs | Flatten all documentation in `/docs/` and verify against `vision.md`. | DONE |

## 3. Planned Features (Next)

| ID | Epic | Task | Status |
|---|---|---|---|
| QUAL-002a | Quality | Implement Type-1 code duplication detector (rolling hash). | DONE |
| QUAL-002b | Scanner | Integrate duplication detection into the main `Scanner.scan` loop. | DONE |
| SEC-002 | Security | Implement `SecurityHeadersMiddleware` audit and standardization. | DONE |
| ESG-001 | ESG | Define weighted aggregate score algorithm (40% E, 30% S, 30% G). | DONE |


## 4. Phase 4 Completed Tasks (Granular Loop)

| ID | Component | Task | Status |
|---|---|---|---|
| QUAL-003 | Quality | Implement Dead Code Detection AST visitor. | DONE |
| SCA-001 | Security | Implement Dependency Manifest Parser (Python/Node). | DONE |
| SCA-002 | Security | Implement OSV.dev API integration for vulnerability lookup. | DONE |
| ARCH-001 | Docs | Automated vision-architecture alignment check script. | DONE |
