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
