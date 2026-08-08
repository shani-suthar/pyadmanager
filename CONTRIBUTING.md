# Contributing

## Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/)
- [just](https://github.com/casey/just) (optional, but the commands below assume it)

## Getting started

```
just setup
```

This runs `uv sync` (installs runtime + dev dependencies into `.venv`), installs `prek` as a global `uv tool`, and registers the git pre-commit hook via `prek install`. Without this last step, `.pre-commit-config.yaml` has no effect — nothing runs automatically on `git commit`.

If you're not using `just`, do the same steps manually:

```
uv sync
uv tool install prek
prek install
```

## Development commands

Run `just --list` to see all recipes. The main ones:

| Command | What it does |
| --- | --- |
| `just test` | `uv run pytest` |
| `just lint` | `uv run ruff check .` (pass `--fix` to autofix) |
| `just fmt` | `uv run ruff format .` |
| `just typecheck` | `uv run pyright src tests` |
| `just check` | lint + typecheck + tests + format check, all at once |
| `just precommit` | run every pre-commit hook against all files (`prek run --all-files`) |
| `just build` | `uv build` (sdist + wheel) |

## Pre-commit hooks

On every commit, `prek` runs (see `.pre-commit-config.yaml`):

- `uv-lock` — keeps `uv.lock` in sync with `pyproject.toml`
- `ruff-check --fix` — lint, autofixing what it can
- `ruff-format` — format
- `pyright` — type check

These run in hooks' own isolated environments, so they work the same regardless of what's installed in your project's `.venv`.

## Tests

`tests/` unit-tests everything without touching the live Ad Manager API — `filters.py`, `retry.py`, and `http_client.py` are pure/network-free, and `client.py`/`services/*.py` are tested by mocking `HTTPClient`/`authed_session`/`service_account.Credentials`. If you add a new `services/<resource>.py`, follow the same approach: mock rather than calling the real API.
