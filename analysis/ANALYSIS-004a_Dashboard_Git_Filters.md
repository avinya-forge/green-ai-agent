# ANALYSIS-004a: Git Blame Integration & Dashboard Filters

## Objective
Evaluate the performance impact and implementation strategy for integrating `git blame` data into every violation during a scan to populate SonarQube-style dashboard filters (e.g., filter by Author, Commit Date).

## The Performance Problem
Running `git blame <file> -L <line>,<line>` for every single violation via a shell subprocess is extremely slow. If a scan generates 5,000 violations, spinning up 5,000 subprocesses will block the `ProcessPoolExecutor` and drastically increase scan time.

## Proposed Strategy: Batching & Libraries

### 1. In-Process Git Libraries
Instead of shelling out to `git`, use `pygit2` (libgit2 bindings for Python). This allows in-memory, highly optimized blame lookups.

### 2. File-Level Batching
Instead of blaming per-violation, blame per-file *once* at the end of the file's AST scan.
- When `worker.py` finishes scanning `src/main.py`, it has a list of violation line numbers: `[10, 45, 88]`.
- It executes a single `pygit2` blame traversal for `src/main.py`.
- It maps the specific lines to the commit author, email, and timestamp.
- It attaches this metadata to the `Violation` Pydantic model.

```python
class Violation(BaseModel):
    # ... existing fields ...
    author: Optional[str] = None
    author_email: Optional[str] = None
    commit_date: Optional[str] = None
```

### 3. Dashboard Integration
Once the backend database stores this metadata alongside violations, the FastAPI backend can easily construct aggregation queries:

```sql
SELECT author, COUNT(*) as violation_count
FROM violations
WHERE project_id = ?
GROUP BY author;
```

This populates the "Author" filter facet in the UI.

## Feasibility Conclusion
Feasible, provided we avoid shell subprocesses. By using `pygit2` and file-level batching, the overhead of attaching blame data to violations will be minimal (estimated <5% increase in total scan time), enabling advanced UI filters without compromising speed.