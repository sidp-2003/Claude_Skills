# Code Review: build_kpis.py
**Date:** 2026-06-03
**File:** `.claude/skills/visualise/scripts/build_kpis.py`
**Reviewer:** code_reviewer agent

---

## Summary

The script reads five parquet files (sales facts, returns facts, and three dimension tables) from a hardcoded date-stamped directory, calculates six retail KPIs, and produces six matplotlib bar/pie charts saved as PNG files. The SKILL.md describes a broader skill for visualizing data from the `sfetchApi/data/` directory, but the script actually reads from a `migrate/data/` path — indicating the skill description and implementation are out of sync.

---

## Issues Found

### 1. Logic Bug — Net Sales Calculation (Line 22)

**Severity: High**

```python
netSales = sales["net_amount"].sum() - totalReturns
```

`net_amount` in the sales table most likely already deducts line-level discounts or taxes but does not account for returns. However, `totalReturns` is summed from `refund_amount` in a *separate* returns table. This double-counts any return that was already reflected in `net_amount` if the source data records a negative net_amount row per return. This logic needs validation against the data schema. If `net_amount` already excludes returns, subtracting `totalReturns` again is incorrect.

A more defensible approach uses a single, explicit source of truth:
```python
# Option A: returns are NOT reflected in net_amount (current assumption)
netSales = sales["net_amount"].sum() - totalReturns

# Option B: net_amount already accounts for returns
netSales = sales["net_amount"].sum()
```

At a minimum, add a comment documenting which assumption is being made.

---

### 2. Hardcoded Paths — No Dynamic Date Handling (Lines 8–9)

**Severity: High**

```python
DATA_DIR = ".claude/skills/migrate/data/2026-05-29/"
OUT_DIR  = ".claude/skills/visualise/visualization/2026-05-29/"
```

Both paths embed a hardcoded date. Every run against new data requires a manual edit. Additionally, paths are relative to the working directory at runtime, not to the script's location, which will break if the script is called from a different working directory.

Suggested fix — detect the latest available date folder automatically and use `pathlib` for robust path handling:
```python
from pathlib import Path
import datetime

BASE_DIR   = Path(__file__).resolve().parents[3]  # repo root
DATA_BASE  = BASE_DIR / ".claude/skills/migrate/data"
VIZ_BASE   = BASE_DIR / ".claude/skills/visualise/visualization"

# Pick the latest date folder automatically
latestDate = max(p.name for p in DATA_BASE.iterdir() if p.is_dir())
DATA_DIR   = DATA_BASE / latestDate
OUT_DIR    = VIZ_BASE  / latestDate
OUT_DIR.mkdir(parents=True, exist_ok=True)
```

---

### 3. No Error Handling on File I/O (Lines 13–17)

**Severity: High**

```python
sales     = pd.read_parquet(DATA_DIR + "fact_sales.parquet")
returns   = pd.read_parquet(DATA_DIR + "fact_returns.parquet")
products  = pd.read_parquet(DATA_DIR + "dim_product.parquet")
stores    = pd.read_parquet(DATA_DIR + "dim_store.parquet")
customers = pd.read_parquet(DATA_DIR + "dim_customer.parquet")
```

If any parquet file is missing or malformed, the script raises an unhandled exception with no actionable message. Wrap in try/except and surface a clear error:
```python
def loadParquet(filePath):
    try:
        return pd.read_parquet(filePath)
    except FileNotFoundError:
        raise FileNotFoundError(f"Required data file not found: {filePath}")
    except Exception as e:
        raise RuntimeError(f"Failed to read {filePath}: {e}") from e
```

---

### 4. SKILL.md Path Mismatch — Script Reads Wrong Data Directory (Line 8)

**Severity: Medium**

SKILL.md states data lives in `.claude/skills/sfetchApi/data/`. The script reads from `.claude/skills/migrate/data/`. This inconsistency means the skill cannot be followed as documented. The SKILL.md needs to be updated to reflect the actual data source, or the script path needs to change.

---

### 5. Naming Convention Violation — `formatMillions` Function (Line 36)

**Severity: Low**

Per project guidelines (CLAUDE.md), all functions must use camelCase. `formatMillions` is already camelCase — this is fine. However, the anonymous lambda on line 147 performs the same formatting logic as `formatMillions` for small values, creating duplication:

```python
# Line 147 — duplicates logic already in formatMillions
ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${x:,.0f}"))
```

Replace with the shared formatter:
```python
ax.yaxis.set_major_formatter(mticker.FuncFormatter(formatMillions))
```

---

### 6. Bar Label Format Inconsistency (Lines 53–57 vs. Lines 166–171)

**Severity: Low**

Chart 1 bar labels use `f"${val:,.0f}"` (comma-separated integer). Chart 6 bar labels use `f"${val/1e6:.2f}M"` (millions with two decimal places). For Charts 1 and 6 both showing total/net sales aggregates of similar magnitude, the labels should use a consistent format. Use the shared `formatMillions` logic for both:
```python
def formatBarLabel(val):
    return f"${val/1e6:.2f}M" if val >= 1e6 else f"${val:,.0f}"
```

---

### 7. All Script Logic at Module Level — No Entrypoint Guard (Lines 1–184)

**Severity: Medium**

The entire script runs at import time. There is no `if __name__ == "__main__":` guard. This prevents the script from being imported as a module for testing individual functions, and it means any accidental `import build_kpis` somewhere will execute all file I/O and rendering immediately.

Wrap execution logic:
```python
def main():
    # all loading, KPI calculation, and chart generation

if __name__ == "__main__":
    main()
```

---

### 8. Functions Not Used for Repeated Chart Pattern — Poor Reuse (Lines 50–183)

**Severity: Medium**

Each of the six charts repeats the same boilerplate:
- `fig, ax = plt.subplots(...)`
- Remove top/right spines
- Add grid
- `plt.tight_layout()`
- `plt.savefig(...)` / `plt.close()`
- `print("Saved ...")`

This violates the guideline to "keep functions small and focused on a single task." Extract the repeated setup and save pattern:
```python
def saveBarChart(ax, title, outputPath, ylabel="Amount (USD)"):
    ax.set_title(title, fontsize=14, fontweight="bold", pad=12)
    ax.set_ylabel(ylabel)
    ax.spines[["top", "right"]].set_visible(False)
    ax.yaxis.grid(True, linestyle="--", alpha=0.4)
    ax.set_axisbelow(True)
    plt.tight_layout()
    plt.savefig(outputPath, dpi=150)
    plt.close()
    print(f"Saved {Path(outputPath).name}")
```

---

### 9. Pie Chart Risk — PALETTE Has Only 6 Colors (Line 34 / Lines 120–127)

**Severity: Low**

`PALETTE` contains exactly 6 hex colors. If `returns["return_reason"]` has more than 6 distinct values, matplotlib will silently cycle colors or raise an error depending on version. Guard against this:
```python
# Limit to top N reasons to match palette, or use a larger color map
returnsByReason = returns.groupby("return_reason")["refund_amount"].sum().sort_values(ascending=False).head(len(PALETTE))
```
Or replace `PALETTE` with `plt.cm.tab10.colors` for a built-in 10-color safe palette.

---

### 10. String Concatenation for Paths (Lines 13, 66, 89, etc.)

**Severity: Low**

Paths are built via string concatenation (`DATA_DIR + "fact_sales.parquet"`). Using `pathlib.Path` eliminates OS separator issues and is the modern Python idiom:
```python
sales = pd.read_parquet(DATA_DIR / "fact_sales.parquet")
```

---

## Summary of Recommendations (Priority Order)

| Priority | Issue | Action |
|---|---|---|
| 1 | Net Sales logic may double-count returns | Validate against schema; document assumption |
| 2 | Hardcoded date path | Auto-detect latest folder using pathlib |
| 3 | No file I/O error handling | Add try/except with descriptive messages |
| 4 | SKILL.md path mismatch | Align documentation with actual data path |
| 5 | No `__main__` guard | Wrap in `main()` with entrypoint guard |
| 6 | Repeated chart boilerplate | Extract `saveBarChart()` helper |
| 7 | Duplicate formatter lambda | Replace with shared `formatMillions` |
| 8 | Bar label format inconsistency | Standardize with shared `formatBarLabel()` |
| 9 | Palette overflow for pie chart | Cap to `len(PALETTE)` or use larger colormap |
| 10 | String path concatenation | Switch to `pathlib.Path` |
