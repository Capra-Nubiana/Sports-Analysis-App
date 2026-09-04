.PHONY: dev test lint install

dev:
	.venv/bin/python -m src.api.main

test:
	.venv/bin/python -m pytest tests/ -x -q

lint:
	.venv/bin/python -m mypy src/
	.venv/bin/ruff check src/ tests/

install:
	.venv/bin/pip install -r requirements.txt
