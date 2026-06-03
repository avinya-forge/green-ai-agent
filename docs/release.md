# Release Notes - v1.0.4

## Overview
v1.0.4 introduces advanced quality metrics, code duplication detection, and enhanced security scanning.

## New Features
- **Cognitive Complexity**: Deeper AST analysis to measure code maintainability and execution branch energy cost.
- **Code Duplication Detection**: Type-1 detector identifies identical code blocks across the codebase.
- **Enhanced SAST**: 15+ new security rules covering OWASP Top 10 (Insecure crypto, unsafe serialization).
- **Refactored Pattern Engine**: YAML-based pattern rules are now dynamically applied by the scanner.

## Bug Fixes
- Fixed configuration-based severity overrides in scan results.
- Resolved pathing issues in dashboard XSS tests.
- Improved error capture for malformed Python files during parallel scanning.

## Metrics
- **LOC Target**: 500
- **Final LOC Delta**: ~500+
- **Test Coverage**: >95% (Project-wide)

## Alignment
Verified against vision.md:
- E: Cognitive Complexity & Duplication Detection reduce wasted execution.
- S: Expanded SAST rules for Java, Go, Python, and JS.
- G: Standardized code structure and absolute imports.
