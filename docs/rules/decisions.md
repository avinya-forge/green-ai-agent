# Architectural Decisions Log

This document tracks all significant architectural pivots, technical debt resolutions, and structural changes made during development.

## 1. Pydantic-Core Downgrade
- **Date**: 2024-05-24
- **Decision**: Revert `pydantic-core` dependency from `2.42.0` to `==2.41.5` in `requirements.txt`.
- **Context**: The existing specification requested an upgrade to `2.42.0`. However, the highest available version of `pydantic` (`2.12.5`) strictly depends on `pydantic-core==2.41.5`. Updating to `2.42.0` led to unresolvable dependency conflicts in `pip`, completely breaking the build and test pipelines.
- **Consequence**: We are pinning it exactly with `==2.41.5` to maintain environment integrity while remaining functional currently.
