Run all pre-commit checks (gitleaks, pytest, mypy, ruff).

Usage: /check

Runs:
  1. gitleaks detect (secret scan)
  2. pytest tests/ -x -q (58 tests)
  3. mypy src/
  4. ruff check src/ tests/
