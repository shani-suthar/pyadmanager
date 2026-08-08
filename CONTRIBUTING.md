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
- `pytest` — runs the full test suite (`uv run pytest`)

The first four run in hooks' own isolated environments, so they work the same regardless of what's installed in your project's `.venv`. `pytest` is a local hook (`language: system`), so it runs against your `.venv` — make sure `just setup`/`uv sync` has been run.

## Optional dependencies

`polars` is an optional extra used by `services/report.py` to parse report rows into a DataFrame. It's not installed by default — `uv sync --extra polars` if you need it, or if you want `test_report.py`'s dataframe-building tests to run instead of skip (they use `pytest.importorskip("polars")`).

## Tests

`tests/` unit-tests everything without touching the live Ad Manager API — `filters.py`, `retry.py`, and `http_client.py` are pure/network-free, and `client.py`/`services/*.py` are tested by mocking `HTTPClient`/`authed_session`/`service_account.Credentials`. `tests/conftest.py` provides a shared `fake_http_client` fixture (`Mock(spec=HTTPClient)`) used across the `services/*` test files — use it rather than constructing your own mock. If you add a new `services/<resource>.py`, follow the same approach: mock rather than calling the real API.

`live_test.py` at the repo root is a separate, manual smoke test against a real GAM network (requires your own `creds.json`) — it's not run by `just test` or CI, only by you directly (`uv run python live_test.py`) when you want to sanity-check against live data.
