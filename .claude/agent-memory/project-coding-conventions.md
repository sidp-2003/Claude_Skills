---
name: project-coding-conventions
description: Project enforces camelCase for all identifiers including constants, overriding PEP 8 SCREAMING_SNAKE_CASE defaults
metadata:
  type: project
---

The project's CLAUDE.md explicitly mandates camelCase for all variables, functions, and class names — including what would conventionally be constants in Python. This overrides PEP 8's SCREAMING_SNAKE_CASE convention for module-level constants. Names must also be descriptive enough to clearly indicate purpose.

**Why:** Project guidelines in `.claude/CLAUDE.md`. Encountered violations in `build_kpis.py` (`DATA_DIR`, `OUT_DIR`, `PALETTE`) and in `csv_to_parquet.py` (`FETCH_DATA`, `latest_folder`, `csv_files`, `src`, `dst`, `convert`).

**How to apply:**
- Flag any SCREAMING_SNAKE_CASE identifier as a naming violation; suggest camelCase equivalents (e.g., `FETCH_DATA` → `fetchData`, `DATA_DIR` → `dataDir`).
- Flag snake_case function/variable names (e.g., `latest_folder` → `latestFolder`, `csv_files` → `csvFiles`).
- Flag overly abbreviated names (e.g., `src`/`dst` → `srcDir`/`dstDir`) and generic function names (e.g., `convert` → `convertCsvToParquet`).
