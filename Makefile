.PHONY: setup init check lint format typecheck test clean run-check

setup:
	uv sync --extra dev
	uv run rbiqa init

init:
	uv run rbiqa init

check:
	uv run rbiqa check

format:
	uv run ruff format src tests
	uv run ruff check --fix src tests

typecheck:
	uv run mypy

test:
	uv run pytest

clean:
	find . -type d \( -name __pycache__ -o -name .pytest_cache -o -name .ruff_cache -o -name .mypy_cache \) -prune -exec rm -rf {} +

all: typecheck test