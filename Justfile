# Run `just` (or `just --list`) to see all recipes.
default:
    @just --list

# One-time setup for a new clone: install deps + git hooks
setup:
    uv sync
    uv tool install prek
    prek install

# Install/sync dependencies
sync:
    uv sync

# Run the test suite
test *args:
    uv run pytest {{args}}

# Run the test suite and open an HTML coverage report
coverage:
    uv run pytest --cov-report=html
    uv run python -m webbrowser htmlcov/index.html

# Lint (add --fix to autofix)
lint *args:
    uv run ruff check . {{args}}

# Format code
fmt:
    uv run ruff format .

# Type check
typecheck:
    uv run pyright src tests

# Run lint, format check, typecheck, and tests
check: lint typecheck test
    uv run ruff format --check .

# Run all pre-commit hooks against every file
precommit:
    prek run --all-files

# Build sdist + wheel
build:
    uv build
