---
name: feedback-python-patterns
description: Python code quality patterns and conventions to enforce when reviewing or writing code in this project
metadata:
  type: feedback
---

Project CLAUDE.md mandates camelCase for all variables, functions, and class names in Python. This is non-standard for Python (PEP 8 uses snake_case) but is an explicit project override.

**Why:** CLAUDE.md is the authoritative style guide. Any snake_case variable or function name is a convention violation in this codebase.

**How to apply:** Flag any snake_case identifiers in Python files as convention violations during review. When writing new Python code, use camelCase throughout (e.g., `totalSales`, `formatMillions`, `loadParquet`).

Additional patterns observed in this codebase:
- Scripts should use `if __name__ == "__main__":` guards with a `main()` function
- Use `pathlib.Path` instead of string path concatenation
- Shared formatter functions should not be duplicated as inline lambdas
- Repeated matplotlib chart setup should be extracted into a helper function
