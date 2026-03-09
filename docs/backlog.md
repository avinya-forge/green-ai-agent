**MILESTONE M1** | **PHASE 2** | **GATEKEEPER** [0-Hygiene-Error | 95% Test | Build-Pass]

### [EPIC-06] Performance Optimization
**TASK GO-009: Go Performance Benchmark** | [DONE] | [PRAGMATIST]
**SPEC:** Implement standard benchmark suite using 'testing' package for Go language detector evaluating AST parsing speed vs python reference.
**TASK GO-010: Native Go Benchmark** | [TODO] | [PRAGMATIST]
**SPEC:** Implement a native Go benchmark using the `testing` package to verify AST parsing performance natively in Go instead of relying purely on Python bindings benchmark.

### [EPIC-07] Security Hardening
**TASK SEC-002: Dependency Upgrade: Bump versions** | [DONE] | [HARDENER]
**SPEC:** Run pip-audit and upgrade remaining dependencies flagged with CVEs in requirements.txt.
**TASK SEC-008: OWASP Top 10: Mapping review** | [DONE] | [HARDENER]
**SPEC:** Create security-review.md mapping current scanner rules against OWASP Top 10 vulnerabilities identifying coverage gaps.

### [EPIC-09] IDE Plugins (Prep)
**TASK IDE-001: VS Code Ext: Project scaffold** | [TODO] | [PRAGMATIST]
**SPEC:** Initialize VS Code extension scaffold in src/ide/vscode/ using yo code with package.json configuring the 'green-ai' command.
**TASK IDE-002: LSP Server: Basic protocol implementation** | [TODO] | [PRAGMATIST]
**SPEC:** Implement base pygls LanguageServer instance in src/ide/lsp/server.py supporting standard I/O communication.
**TASK IDE-003: LSP Server: Initialize handshake** | [TODO] | [PRAGMATIST]
**SPEC:** Implement initialize request handler in LanguageServer defining TextDocumentSyncKind.Incremental capabilities.
**TASK IDE-004: LSP Server: Text document sync** | [TODO] | [PRAGMATIST]
**SPEC:** Implement didOpen, didChange, and didSave event handlers bridging LSP events to the internal scanner API.
**TASK IDE-005: LSP Server: Diagnostics publishing** | [TODO] | [PRAGMATIST]
**SPEC:** Map scanner Violation objects to LSP Diagnostic objects and publish via LanguageServer.publish_diagnostics.
**TASK IDE-007: Syntax Highlighting: Grammar definition** | [TODO] | [PRAGMATIST]
**SPEC:** Define basic TextMate grammar for custom rule definition files in src/ide/vscode/syntaxes/.
**TASK IDE-008: Quick Fix: Code action provider** | [TODO] | [PRAGMATIST]
**SPEC:** Implement textDocument/codeAction handler providing quick fixes for detected optimizer violations.
**TASK IDE-009: VS Code Ext: Settings page** | [TODO] | [PRAGMATIST]
**SPEC:** Add configuration section 'green-ai.scanner' in package.json to control LSP server path and scanner strictness.
**TASK IDE-010: VS Code Ext: Output channel logging** | [TODO] | [PRAGMATIST]
**SPEC:** Implement window/logMessage reporting LSP server initialization and scanning progress to an output channel.

### [EPIC-11] Cloud Native Deployment
**TASK CLD-002: Implement Kubernetes Deployment manifests** | [TODO] | [PRAGMATIST]
**SPEC:** Create deploy/kubernetes/deployment.yaml defining green-ai replica set with resource requests/limits (CPU 500m, Mem 512Mi).
**TASK CLD-003: Implement Kubernetes Service manifests** | [TODO] | [PRAGMATIST]
**SPEC:** Create deploy/kubernetes/service.yaml defining ClusterIP service exposing the FastAPI UI on port 80.
**TASK CLD-004: Implement Kubernetes Ingress configurations** | [TODO] | [PRAGMATIST]
**SPEC:** Create deploy/kubernetes/ingress.yaml defining routing rules for green-ai dashboard domain mapping.
**TASK CLD-007: Configure horizontal pod autoscaling for scanner** | [TODO] | [PRAGMATIST]
**SPEC:** Create deploy/kubernetes/hpa.yaml targeting the deployment to scale between 1-5 pods based on 70% CPU utilization.
**TASK CLD-008: Implement readiness and liveness probes** | [TODO] | [PRAGMATIST]
**SPEC:** Add /api/health endpoint to app_fastapi.py and configure liveness/readiness probes in deployment.yaml.
**TASK CLD-009: Document cloud deployment steps** | [TODO] | [PRAGMATIST]
**SPEC:** Create docs/cloud-deployment.md detailing kubectl apply commands and Helm chart alternatives.
**TASK CLD-010: Integration tests for Kubernetes deployment** | [TODO] | [PRAGMATIST]
**SPEC:** Add pytest integration test deploying test manifest via local kind cluster and verifying service response.

### [EPIC-12] Team Collaboration Dashboard
**TASK TEAM-001: Design database schema for team analytics** | [TODO] | [PRAGMATIST]
**SPEC:** Create SQLAlchemy models for Team and TeamMember in src/core/telemetry/models.py.
**TASK TEAM-002: Implement API for creating and managing teams** | [TODO] | [PRAGMATIST]
**SPEC:** Add POST /api/teams and GET /api/teams endpoints to app_fastapi.py using Pydantic schemas.
**TASK TEAM-003: Implement RBAC (Role-Based Access Control) for teams** | [TODO] | [PRAGMATIST]
**SPEC:** Implement Role dependency in src/ui/middleware/auth.py mapping Viewer/Editor roles to endpoints.
**TASK TEAM-004: Build team dashboard frontend views** | [TODO] | [PRAGMATIST]
**SPEC:** Create src/ui/templates/team_dashboard.html rendering team-specific charts via Chart.js.
**TASK TEAM-005: Implement aggregation logic for team scan metrics** | [TODO] | [PRAGMATIST]
**SPEC:** Add TelemetryService.get_team_metrics(team_id) method aggregating ScanMetrics across team projects.
**TASK TEAM-006: Add historical trend charts to team dashboard** | [TODO] | [PRAGMATIST]
**SPEC:** Implement endpoint GET /api/teams/{id}/history returning time-series violation counts.
**TASK TEAM-007: Integrate authentication system with team API** | [TODO] | [PRAGMATIST]
**SPEC:** Add OAuth2 password flow to authenticate users and attach Team IDs to current requests.
**TASK TEAM-008: Implement email notifications for team summaries** | [TODO] | [PRAGMATIST]
**SPEC:** Create weekly CRON job script that generates PDF reports and sends via smtplib.
**TASK TEAM-009: Write unit tests for team analytics API** | [TODO] | [PRAGMATIST]
**SPEC:** Add tests/api/test_teams.py using TestClient to verify CRUD operations and RBAC enforcement.
**TASK TEAM-010: Document team collaboration features** | [TODO] | [PRAGMATIST]
**SPEC:** Create docs/team-features.md describing organization setup and metric aggregation behavior.

### [EPIC-13] Machine Learning Pattern Recognition
**TASK ML-001: Collect and clean training dataset of code inefficiencies** | [TODO] | [PRAGMATIST]
**SPEC:** Create script src/scripts/scrape_dataset.py extracting historical commits labeled 'refactor(perf)'.
**TASK ML-002: Design neural network architecture for code sequence classification** | [TODO] | [PRAGMATIST]
**SPEC:** Define PyTorch Transformer model in src/ml/model.py mapping tokenized ASTs to efficiency labels.
**TASK ML-003: Implement model training pipeline** | [TODO] | [PRAGMATIST]
**SPEC:** Create src/ml/train.py handling batching, loss calculation, and epoch tracking.
**TASK ML-004: Evaluate model accuracy and tune hyperparameters** | [TODO] | [PRAGMATIST]
**SPEC:** Implement cross-validation logic reporting F1-score on test split to src/ml/eval.py.
**TASK ML-005: Export trained model to ONNX format** | [TODO] | [PRAGMATIST]
**SPEC:** Add script src/ml/export.py calling torch.onnx.export converting the trained PyTorch model.
**TASK ML-006: Integrate ONNX runtime into Green-AI scanner** | [TODO] | [PRAGMATIST]
**SPEC:** Add onnxruntime dependency and implement MLDetector class in src/core/detectors/ml.py.
**TASK ML-007: Implement fallback logic for ML model predictions** | [TODO] | [PRAGMATIST]
**SPEC:** Wrap MLDetector.scan() with exception handler falling back to RegexDetector on inference failure.
**TASK ML-008: Add CLI flag to enable/disable ML scanner** | [TODO] | [PRAGMATIST]
**SPEC:** Add --enable-ml flag to src/cli/commands/scan.py passing the option to GreenAIConfig.
**TASK ML-009: Write integration tests for ML pattern recognition** | [TODO] | [PRAGMATIST]
**SPEC:** Add tests/ml/test_inference.py verifying ONNX model outputs deterministic labels for known patterns.
**TASK ML-010: Document ML pattern recognition capabilities** | [TODO] | [PRAGMATIST]
**SPEC:** Create docs/ml-architecture.md explaining the training pipeline and ONNX integration.

### [EPIC-14] Rust Language Support
**TASK RUST-001: Integrate `tree-sitter-rust` into the parser engine** | [TODO] | [PRAGMATIST]
**SPEC:** Add tree-sitter-rust to requirements.txt and Language.build_library to src/core/scanner/parser.py.
**TASK RUST-002: Implement Rust language detector class** | [TODO] | [PRAGMATIST]
**SPEC:** Implement RustASTDetector inheriting BaseTreeSitterDetector mapping node types.
**TASK RUST-003: Implement rule: excessive clone detection** | [TODO] | [PRAGMATIST]
**SPEC:** Write tree-sitter query matching explicit .clone() calls within loop bodies in RustASTDetector.
**TASK RUST-004: Implement rule: unnecessary allocations in loops** | [TODO] | [PRAGMATIST]
**SPEC:** Write tree-sitter query detecting String::new() or vec![] inside for/while loops.
**TASK RUST-005: Implement rule: inefficient unwrap inside loops** | [TODO] | [PRAGMATIST]
**SPEC:** Write tree-sitter query finding .unwrap() calls directly enclosed by loop constructs.
**TASK RUST-006: Write unit tests for Rust rules** | [TODO] | [PRAGMATIST]
**SPEC:** Add tests/detectors/test_rust.py executing AST queries against mock inefficient rust source strings.
**TASK RUST-007: Add CLI integration for scanning Rust projects** | [TODO] | [PRAGMATIST]
**SPEC:** Update src/core/scanner/discovery.py to include .rs file extensions during traversal.
**TASK RUST-008: Implement end-to-end Rust project scanning test** | [TODO] | [PRAGMATIST]
**SPEC:** Create a sample rust cargo project in tests/fixtures/rust_app and scan it.
**TASK RUST-009: Update documentation with Rust support details** | [TODO] | [PRAGMATIST]
**SPEC:** Update README.md and docs/ to indicate Rust language support is available.
**TASK RUST-010: Release Rust Support Beta** | [TODO] | [PRAGMATIST]
**SPEC:** Bump application minor version and generate release note for Rust Beta.
