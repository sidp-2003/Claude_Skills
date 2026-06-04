---
name: patterns-migrate-scripts
description: Recurring code quality patterns found in the migrate skill scripts (csv_to_parquet.py review, 2026-06-03)
metadata:
  type: project
---

Reviewed `.claude/skills/migrate/scripts/csv_to_parquet.py` on 2026-06-03.

Recurring issues found:
- snake_case naming used throughout instead of the project-mandated camelCase (CLAUDE.md guideline violated at every function, variable, and constant name)
- `sys.exit()` called inside helper functions instead of raising exceptions, making the functions untestable and non-reusable
- No per-file error handling around pandas I/O operations
- Fragile path depth indexing (`Path(__file__).parents[2]`) with no comments explaining intent
- Lexicographic sort used to find "latest" date folder without validating the date format

**Why:** These patterns suggest the script was written quickly as a one-off utility without the project coding standards in mind.

**How to apply:** When reviewing other scripts under `.claude/skills/`, check immediately for camelCase compliance, sys.exit usage in non-main functions, and bare I/O without error handling. [[feedback_testing]]
