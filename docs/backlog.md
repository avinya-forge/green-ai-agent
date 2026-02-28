# Product Backlog

## Phase 2: Action & Expansion (Current)


### [EPIC-04] Advanced Reporting
*Goal: Enhance reporting capabilities with HTML/CSV improvements and PDF support.*
- [REP-003] | PDF Export: Chart rendering (static image gen) | BLOCKS-REP-002 | Done

### [EPIC-05] CI/CD GitHub Action V2
*Goal: Deepen CI/CD integration with a robust GitHub Action.*
- [CI-010] | Marketplace prep: Documentation | INDEPENDENT | TODO

### [EPIC-06] Performance Optimization
*Goal: Ensure the tool remains lightweight and fast.*
- [GO-009] | Go Performance Benchmark | INDEPENDENT | TODO
- [PERF-005] | Parallel Processing: Multiprocessing pool tuning | INDEPENDENT | TODO
- [PERF-006] | Parallel Processing: Chunk size tuning | BLOCKS-PERF-005 | TODO
- [PERF-007] | Memory Reduction: Generator usage review | INDEPENDENT | TODO
- [PERF-008] | Memory Reduction: Tree-sitter tree disposal | INDEPENDENT | TODO

### [EPIC-07] Security Hardening
*Goal: Meet DoD security requirements.*
- [SEC-002] | Dependency Upgrade: Bump versions | BLOCKS-SEC-001 | TODO
- [SEC-008] | OWASP Top 10: Mapping review | INDEPENDENT | TODO

### [EPIC-09] IDE Plugins (Prep)
*Goal: Prepare for Phase 3 IDE integration.*
- [IDE-001] | VS Code Ext: Project scaffold | INDEPENDENT | TODO
- [IDE-002] | LSP Server: Basic protocol implementation | INDEPENDENT | TODO
- [IDE-003] | LSP Server: Initialize handshake | BLOCKS-IDE-002 | TODO
- [IDE-004] | LSP Server: Text document sync | BLOCKS-IDE-003 | TODO
- [IDE-005] | LSP Server: Diagnostics publishing | BLOCKS-IDE-004 | TODO
- [IDE-006] | Connect Scanner: CLI wrapper for LSP | BLOCKS-IDE-005 | TODO
- [IDE-007] | Syntax Highlighting: Grammar definition | INDEPENDENT | TODO
- [IDE-008] | Quick Fix: Code action provider | BLOCKS-IDE-005 | TODO
- [IDE-009] | VS Code Ext: Settings page | BLOCKS-IDE-001 | TODO
- [IDE-010] | VS Code Ext: Output channel logging | BLOCKS-IDE-001 | TODO


### [EPIC-11] Cloud Native Deployment
*Goal: Enable scalable cloud deployment via Kubernetes and Docker Swarm.*
- [CLD-001] | Create Helm Chart for Green-AI | INDEPENDENT | TODO
- [CLD-002] | Implement Kubernetes Deployment manifests | BLOCKS-CLD-001 | TODO
- [CLD-003] | Implement Kubernetes Service manifests | BLOCKS-CLD-002 | TODO
- [CLD-004] | Implement Kubernetes Ingress configurations | BLOCKS-CLD-003 | TODO
- [CLD-005] | Create Docker Compose file for local cloud testing | INDEPENDENT | TODO
- [CLD-006] | Write CI/CD pipeline for automated Docker image push | INDEPENDENT | TODO
- [CLD-007] | Configure horizontal pod autoscaling for scanner | BLOCKS-CLD-002 | TODO
- [CLD-008] | Implement readiness and liveness probes | BLOCKS-CLD-002 | TODO
- [CLD-009] | Document cloud deployment steps | INDEPENDENT | TODO
- [CLD-010] | Integration tests for Kubernetes deployment | BLOCKS-CLD-009 | TODO

### [EPIC-12] Team Collaboration Dashboard
*Goal: Provide team-based aggregation and historical reporting.*
- [TEAM-001] | Design database schema for team analytics | INDEPENDENT | TODO
- [TEAM-002] | Implement API for creating and managing teams | BLOCKS-TEAM-001 | TODO
- [TEAM-003] | Implement RBAC (Role-Based Access Control) for teams | BLOCKS-TEAM-002 | TODO
- [TEAM-004] | Build team dashboard frontend views | INDEPENDENT | TODO
- [TEAM-005] | Implement aggregation logic for team scan metrics | BLOCKS-TEAM-001 | TODO
- [TEAM-006] | Add historical trend charts to team dashboard | BLOCKS-TEAM-005 | TODO
- [TEAM-007] | Integrate authentication system with team API | BLOCKS-TEAM-003 | TODO
- [TEAM-008] | Implement email notifications for team summaries | INDEPENDENT | TODO
- [TEAM-009] | Write unit tests for team analytics API | BLOCKS-TEAM-005 | TODO
- [TEAM-010] | Document team collaboration features | INDEPENDENT | TODO

### [EPIC-13] Machine Learning Pattern Recognition
*Goal: Use advanced ML models to predict and detect complex code inefficiencies.*
- [ML-001] | Collect and clean training dataset of code inefficiencies | INDEPENDENT | TODO
- [ML-002] | Design neural network architecture for code sequence classification | BLOCKS-ML-001 | TODO
- [ML-003] | Implement model training pipeline | BLOCKS-ML-002 | TODO
- [ML-004] | Evaluate model accuracy and tune hyperparameters | BLOCKS-ML-003 | TODO
- [ML-005] | Export trained model to ONNX format | BLOCKS-ML-004 | TODO
- [ML-006] | Integrate ONNX runtime into Green-AI scanner | BLOCKS-ML-005 | TODO
- [ML-007] | Implement fallback logic for ML model predictions | BLOCKS-ML-006 | TODO
- [ML-008] | Add CLI flag to enable/disable ML scanner | BLOCKS-ML-006 | TODO
- [ML-009] | Write integration tests for ML pattern recognition | BLOCKS-ML-006 | TODO
- [ML-010] | Document ML pattern recognition capabilities | INDEPENDENT | TODO

### [EPIC-14] Rust Language Support
*Goal: Add support for analyzing Rust projects.*
- [RUST-001] | Integrate `tree-sitter-rust` into the parser engine | INDEPENDENT | TODO
- [RUST-002] | Implement Rust language detector class | BLOCKS-RUST-001 | TODO
- [RUST-003] | Implement rule: excessive clone detection | BLOCKS-RUST-002 | TODO
- [RUST-004] | Implement rule: unnecessary allocations in loops | BLOCKS-RUST-002 | TODO
- [RUST-005] | Implement rule: inefficient unwrap inside loops | BLOCKS-RUST-002 | TODO
- [RUST-006] | Write unit tests for Rust rules | BLOCKS-RUST-005 | TODO
- [RUST-007] | Add CLI integration for scanning Rust projects | BLOCKS-RUST-002 | TODO
- [RUST-008] | Implement end-to-end Rust project scanning test | BLOCKS-RUST-007 | TODO
- [RUST-009] | Update documentation with Rust support details | INDEPENDENT | TODO
- [RUST-010] | Release Rust Support Beta | BLOCKS-RUST-008 | TODO

### [EPIC-15] C# Language Support
*Goal: Add support for analyzing C# (.NET) projects.*
- [CS-001] | Integrate `tree-sitter-c-sharp` into parser engine | INDEPENDENT | TODO
- [CS-002] | Implement C# language detector class | BLOCKS-CS-001 | TODO
- [CS-003] | Implement rule: blocking async calls (.Result/.Wait) | BLOCKS-CS-002 | TODO
- [CS-004] | Implement rule: inefficient string concatenation in loops | BLOCKS-CS-002 | TODO
- [CS-005] | Implement rule: multiple LINQ iterations (ToList inside loop) | BLOCKS-CS-002 | TODO
- [CS-006] | Write unit tests for C# rules | BLOCKS-CS-005 | TODO
- [CS-007] | Add CLI integration for scanning C# projects | BLOCKS-CS-002 | TODO
- [CS-008] | Implement end-to-end C# project scanning test | BLOCKS-CS-007 | TODO
- [CS-009] | Update documentation with C# support details | INDEPENDENT | TODO
- [CS-010] | Release C# Support Beta | BLOCKS-CS-008 | TODO
