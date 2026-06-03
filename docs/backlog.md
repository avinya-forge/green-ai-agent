# Project Backlog

## 1. High-Priority Granular Tasks (Immediate Execution)

| ID | Component | Task | Status |
|---|---|---|---|
| SAN-001 | Scanner | Fix `severity_override` logic in `worker.py` to respect config. | DONE |
| SAN-002 | Tests | Fix path resolution in `tests/test_xss_vulnerability.py` using absolute pathing. | DONE |
| SAN-003 | Scanner | Ensure `SyntaxError` in workers returns a specific 'syntax_error' issue ID. | DONE |
| QUAL-001a | Analyzer | Implement `CognitiveComplexityAnalyzer` AST visitor in `analyzer.py`. | DONE |
| QUAL-001b | Analyzer | Integrate cognitive complexity into `EmissionAnalyzer` and metrics. | DONE |
| SEC-001a | Detector | Refactor `PatternBasedDetector` to apply rules dynamically from YAML repository. | IN_PROGRESS |
| SEC-001b | Rules | Port 10+ OWASP security rules to `rules/python.yaml` and `rules/javascript.yaml`. | TODO |
| SEC-001c | Detector | Debug integrated scan failure for new security rules (Rules not detected in scan results). | TODO |

## 2. Technical Debt & Deep Cleaning

| ID | Component | Task | Status |
|---|---|---|---|
| CLEAN-001 | Detectors | Remove redundant regex patterns from `python_detector.py` (logic moved to PatternBasedDetector). | TODO |
| CLEAN-002 | Core | Standardize absolute imports in all touched files (from src.core...). | TODO |
| CLEAN-003 | Scanner | Resolve all `flake8` violations in `src/core/scanner/` and `src/core/detectors/`. | TODO |
| CLEAN-004 | Docs | Flatten all documentation in `/docs/` and verify against `vision.md`. | TODO |

## 3. Planned Features (Next)

| ID | Epic | Task | Status |
|---|---|---|---|
| QUAL-002a | Quality | Implement Type-1 code duplication detector (rolling hash). | TODO |
| QUAL-002b | Scanner | Integrate duplication detection into the main `Scanner.scan` loop. | TODO |
| SEC-002 | Security | Implement `SecurityHeadersMiddleware` audit and standardization. | TODO |
| ESG-001 | ESG | Define weighted aggregate score algorithm (40% E, 30% S, 30% G). | TODO |

