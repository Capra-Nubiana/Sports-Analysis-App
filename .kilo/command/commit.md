Commit changes and push to a feature branch.

Usage: /commit <message>

Example: /commit "feat: add Stripe webhook handler"

This will:
  1. Stage all changes
  2. Run pre-commit hook (gitleaks, pytest, mypy, ruff)
  3. Commit with conventional commit format
  4. Push to origin
