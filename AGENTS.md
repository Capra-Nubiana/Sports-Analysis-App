# AGENTS.md

## Development Workflow

### Branch Strategy
- **Main branches:** `main` (production), `develop` (integration)
- **Feature branches:** Always branch from `develop` → `feature/<descriptive-name>`
- **No direct commits** to `main` or `develop`

### Pre-commit Requirements
All commits trigger a pre-commit hook (`.githooks/pre-commit`) that runs:
1. **gitleaks** — secret scanner (blocks if API keys/passwords found)
2. **pytest** — full test suite (58 tests must pass)
3. **mypy** — static type checking (0 errors)
4. **ruff** — linting (0 errors)

### Commands

```bash
# Create feature branch
git checkout develop && git pull
git checkout -b feature/<name>

# Run checks before committing
.venv/bin/python -m pytest tests/ -x -q
.venv/bin/python -m mypy src/
.venv/bin/ruff check src/ tests/

# Commit (pre-commit hook runs automatically)
git add .
git commit -m "feat: <description>"

# Push and create PR
git push origin feature/<name>
```

### PR Requirements
- Base: `develop`
- Title format: `feat:` | `fix:` | `refactor:` | `docs:`
- Description: what changed + test results
- Reviewers: assign at least one

### Quick Reference

| Command | Description |
|---------|-------------|
| `make dev` | Start API server with auto-reload |
| `pytest` | Run all tests |
| `mypy src/` | Type check |
| `ruff check src/` | Lint |
| `.venv/bin/python -m src.api.main` | Start FastAPI server |
| `.venv/bin/python -m src.core.pipeline --sport rugby --video data/sample.mp4` | Run inference |
