# ANALYSIS-003a: Organization-Level Rule Customization Hierarchy

## Objective
Design a configuration hierarchy allowing global standards to be customized at the Organization, Project, and User (local) levels.

## Hierarchy Model

Resolution order (Highest precedence first):
1. **User/Local (`.green-ai/suppress.yaml`):** Developer-specific exceptions or temporary local overrides.
2. **Project Level (DB or `green-ai.yaml`):** Settings specific to a single repository.
3. **Organization Level (DB):** Enterprise-wide mandates (e.g., "All secrets are CRITICAL").
4. **Global Defaults (Engine DB):** The baseline rules synced from OSV/GSF.

## Implementation Architecture

### 1. The Configuration Resolver
During scan initialization (`src/core/scanner/main.py`), the engine must build a merged configuration dictionary:

```python
def resolve_config(org_id: str, project_id: str, local_path: Path):
    config = deepcopy(GLOBAL_RULES)

    org_config = fetch_org_overrides(org_id)
    config = merge(config, org_config)

    proj_config = fetch_project_overrides(project_id)
    config = merge(config, proj_config)

    local_config = parse_local_yaml(local_path)
    config = merge(config, local_config)

    return config
```

### 2. UI / Dashboard Implications
The "truly customizable product" requirement means the UI must provide views for:
- **Organization Settings:** Admins toggle rules globally.
- **Project Settings:** Project managers tweak rules.
- When viewing a rule in the dashboard, the UI should indicate *where* the rule's current severity is inherited from (e.g., "Severity: High (Inherited from Organization)").

## Feasibility Conclusion
Highly feasible. We already support `.green-ai.yaml` and suppression files. Transitioning to a deep-merge dictionary model backed by the SQLAlchemy schema proposed in ANALYSIS-002b will fulfill this requirement efficiently.