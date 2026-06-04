# Code Review: csv_to_parquet.py
**Date:** 2026-06-03  
**File:** `.claude/skills/migrate/scripts/csv_to_parquet.py`  
**Reviewer:** code_reviewer agent

---

## Summary

The script converts CSV files from the latest dated subfolder in `fetchAPI/data` to Parquet format, saving them in a mirrored directory structure under `migrate/data/<same-date-folder>/`. It discovers the most recent date folder by lexicographic sort, then batch-converts every `.csv` found.

---

## Issues Found

### 1. Naming Convention Violations (camelCase not used)
**Severity:** Medium — project CLAUDE.md mandates camelCase for variables, functions, and class names.

- Line 11: `FETCH_DATA` — module-level constant, but as a variable it should be `fetchData`
- Line 12: `MIGRATE_DATA` — should be `migrateData`
- Line 15: `latest_folder` — function name should be `latestFolder`
- Line 16: `dated` — acceptable, but `datedFolders` would be more descriptive
- Line 26: `convert` — too generic; should be `convertCsvToParquet` (also applies the "descriptive names" guideline)
- Line 28: `dst_folder`, `src_folder` — should be `dstFolder`, `srcFolder`
- Line 33: `csv_path`, `csv_files` — should be `csvPath`, `csvFiles`
- Line 35: `out_path` — should be `outPath`
- Line 41: `src`, `dst` — too terse; `srcFolder`, `dstFolder` are clearer

### 2. sys.exit(1) Inside Library-Style Functions
**Severity:** Medium — `latest_folder` and `convert` call `sys.exit(1)` directly.

- Lines 22–23: `sys.exit` inside `latest_folder` prevents the caller from handling the error gracefully (e.g., in tests or when called programmatically).
- Lines 30–31: Same problem in `convert`.

**Suggestion:** Raise exceptions instead and let `main` handle them:

```python
def latestFolder(base: Path) -> Path:
    datedFolders = sorted(
        (d for d in base.iterdir() if d.is_dir()),
        key=lambda d: d.name,
    )
    if not datedFolders:
        raise FileNotFoundError(f"No dated folders found in {base}")
    return datedFolders[-1]

def main() -> None:
    try:
        src = latestFolder(FETCH_DATA)
        ...
    except (FileNotFoundError, ValueError) as e:
        print(e, file=sys.stderr)
        sys.exit(1)
```

### 3. No Error Handling for I/O Operations
**Severity:** Medium

- Line 34: `pd.read_csv(csv_path)` — if a CSV is malformed or empty, pandas raises an unhandled exception with no user-friendly message.
- Line 36: `df.to_parquet(out_path, index=False)` — write failures (permissions, disk full) are not caught.

**Suggestion:** Wrap per-file operations in a try/except and log failures without aborting the entire run:

```python
for csvPath in sorted(csvFiles):
    try:
        df = pd.read_csv(csvPath)
        outPath = dstFolder / (csvPath.stem + ".parquet")
        df.to_parquet(outPath, index=False)
        print(f"  {csvPath.name} -> {outPath.relative_to(migrateData.parent.parent)}")
    except Exception as e:
        print(f"  FAILED {csvPath.name}: {e}", file=sys.stderr)
```

### 4. Hardcoded Path Resolution Is Fragile
**Severity:** Low-Medium

- Line 11: `Path(__file__).parents[2]` uses a numeric index to climb the directory tree. If the script is moved one level up or down, this silently resolves to the wrong directory.
- Line 37: `out_path.relative_to(MIGRATE_DATA.parent.parent)` — double `.parent.parent` is opaque.

**Suggestion:** Define the root explicitly or use a named constant for the project root, then build all paths from it. At minimum, add a comment explaining the intended directory depth.

### 5. `latest_folder` Uses Lexicographic Sort Without Validation
**Severity:** Low

- Lines 16–23: The folder with the lexicographically greatest name is assumed to be the latest. This works for `YYYY-MM-DD` folders but will silently pick the wrong folder for any other naming scheme (e.g., `v2`, `final`, `backup`).

**Suggestion:** Either validate that folder names match a date pattern before sorting, or document the assumption clearly:

```python
import re
DATE_PATTERN = re.compile(r"^\d{4}-\d{2}-\d{2}$")

datedFolders = sorted(
    (d for d in base.iterdir() if d.is_dir() and DATE_PATTERN.match(d.name)),
    key=lambda d: d.name,
)
```

### 6. No Progress Indication for Large Batches
**Severity:** Low

- If `csv_files` contains many files, there is no count summary before or after conversion. A simple header line (`Converting N files...`) and a final count of successes/failures would improve observability.

### 7. `convert` Function Violates Single-Responsibility Principle
**Severity:** Low

- The `convert` function (line 26) does three things: creates the destination directory, validates input, and performs the conversion loop. Per the project guideline ("keep functions small and focused on a single task"), consider splitting into `ensureOutputDir`, `validateSourceFiles`, and the conversion loop itself — or at least separate directory creation from conversion logic.

---

## Summary Table

| # | Issue | Severity | Lines |
|---|-------|----------|-------|
| 1 | Naming convention violations (snake_case instead of camelCase) | Medium | 11–12, 15–17, 26–37, 41–42 |
| 2 | `sys.exit` inside library functions — should raise exceptions | Medium | 22–23, 30–31 |
| 3 | No per-file error handling for CSV read / Parquet write | Medium | 34, 36 |
| 4 | Fragile hardcoded path depth via numeric `.parents[N]` | Low-Medium | 11, 37 |
| 5 | Lexicographic sort without date-format validation | Low | 16–23 |
| 6 | No progress summary for batch operations | Low | 33–37 |
| 7 | `convert` function handles multiple responsibilities | Low | 26–37 |
