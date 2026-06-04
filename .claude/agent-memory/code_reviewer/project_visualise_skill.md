---
name: project-visualise-skill
description: Context on the visualise skill — what it does, where data lives, known issues, and conventions observed in build_kpis.py
metadata:
  type: project
---

The `visualise` skill (`.claude/skills/visualise/`) reads retail parquet files from `.claude/skills/migrate/data/<date>/` and produces six matplotlib PNG charts saved to `.claude/skills/visualise/visualization/<date>/`. The script entry point is `.claude/skills/visualise/scripts/build_kpis.py`.

**Why:** Reviewed 2026-06-03. SKILL.md incorrectly documents the data source as `sfetchApi/data/` but the script reads from `migrate/data/` — the documentation and implementation are out of sync.

**How to apply:** When suggesting changes to this skill, use `migrate/data/` as the actual data path until SKILL.md is corrected. The date folder (`2026-05-29`) is currently hardcoded and should be made dynamic. See [[project-visualise-known-bugs]] for the net sales double-count risk.
