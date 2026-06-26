# ANALYSIS-002b: DB Schema for External Standard Caching

## Objective
Design a relational database schema (SQLAlchemy/Alembic) to locally cache dynamic rules fetched from external standard forums (OSV, GSF, etc.), enabling fast scans and custom overrides.

## Schema Design

### Table: `standard_sources`
Tracks the upstream repositories or APIs.
- `id` (UUID, PK)
- `name` (String, e.g., "GSF Python Rules")
- `url` (String)
- `last_synced_at` (DateTime)
- `sync_interval_hours` (Integer)

### Table: `rules`
Stores the individual rule definitions.
- `id` (String, PK, e.g., "GSF-PY-001")
- `source_id` (UUID, FK -> `standard_sources.id`)
- `language` (String)
- `severity` (Enum: CRITICAL, HIGH, MEDIUM, LOW)
- `description` (Text)
- `ast_query` (Text) - The Tree-sitter S-expression query
- `remediation_effort_minutes` (Integer)
- `is_active` (Boolean, default: True)
- `version` (String)

### Table: `rule_overrides` (For Org Customization)
Allows organizations to tweak standard rules without modifying the cached original.
- `id` (UUID, PK)
- `rule_id` (String, FK -> `rules.id`)
- `org_id` (UUID) # Assuming multi-tenant organization support
- `override_severity` (Enum, nullable)
- `is_disabled` (Boolean, default: False)
- `custom_message` (Text, nullable)

## Feasibility Conclusion
Implementing this schema via SQLAlchemy Core is straightforward and integrates perfectly with our existing PostgreSQL/SQLite setup. It provides the foundation for the "truly customizable product" requirement by allowing the UI to toggle the `is_disabled` state or tweak severities in the `rule_overrides` table.