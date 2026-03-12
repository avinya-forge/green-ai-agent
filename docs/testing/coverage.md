# Security Review & OWASP Top 10 Mapping

This document maps the current Green-AI scanner rules against the OWASP Top 10 vulnerabilities to identify coverage gaps.

## Current Rules Mapping

| OWASP Top 10 Category | Current Rules Covering Category |
|---|---|
| A01:2021-Broken Access Control | None |
| A02:2021-Cryptographic Failures | None |
| A03:2021-Injection | `eval_usage` (JS/TS), `inner_html` (JS/TS), `subprocess_run_without_timeout` (Python) |
| A04:2021-Insecure Design | `proper_resource_cleanup` (Python, implicit design issue mitigation) |
| A05:2021-Security Misconfiguration | `bare_except` (Python) |
| A06:2021-Vulnerable and Outdated Components | `momentjs_deprecated` (JS/TS) |
| A07:2021-Identification and Authentication Failures | None |
| A08:2021-Software and Data Integrity Failures | None |
| A09:2021-Security Logging and Monitoring Failures | `excessive_logging` (Go, Python), `excessive_console_logging` (JS/TS) |
| A10:2021-Server-Side Request Forgery (SSRF) | None |

## Other Security-Related Rules
- `alert_usage` (JS/TS) - Minor security/quality concern.
- `document_write` (JS/TS) - XSS vector (Injection).
- `mutable_default_argument` (Python) - Bug risk, potentially exploitable depending on state.
- `global_variable_mutation` (Python) - Thread safety/integrity risk.

## Coverage Gaps
The current ruleset is heavily optimized for **Green Coding** (performance, resource utilization, energy efficiency) rather than security. Significant gaps exist in:
- **A01: Broken Access Control**
- **A02: Cryptographic Failures** (e.g., hardcoded secrets, weak hashes)
- **A07: Identification and Authentication Failures**
- **A08: Software and Data Integrity Failures**
- **A10: SSRF**

### Recommendations
To harden the tool conceptually alongside its green capabilities, future rules should be developed to target:
1. Hardcoded credentials/secrets.
2. Insecure cryptographic algorithms.
3. Insufficient authorization checks.
