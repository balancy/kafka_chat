.DEFAULT_GOAL := lint

lint:
	@echo "Running linter"
	black .
	ruff check .
