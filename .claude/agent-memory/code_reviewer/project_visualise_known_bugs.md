---
name: project-visualise-known-bugs
description: Known logic and quality issues in build_kpis.py discovered during 2026-06-03 code review
metadata:
  type: project
---

Net Sales calculation on line 22 of `build_kpis.py` may double-count returns:
`netSales = sales["net_amount"].sum() - totalReturns`
If `net_amount` already reflects return deductions, subtracting `totalReturns` (from the separate returns table) counts them twice. This has not been validated against the data schema.

**Why:** Identified during code review on 2026-06-03. The data source schema documentation is not in the repo — the assumption embedded in the code is undocumented.

**How to apply:** When modifying KPI logic in this script, flag the net sales formula for schema validation before accepting it as correct. See [[project-visualise-skill]] for broader context.
