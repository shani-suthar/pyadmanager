# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

`pyadmanager` — a Python REST client for the Google Ad Manager API v1 (`https://admanager.googleapis.com/v1`). Requires Python 3.13+, managed with `uv` (see `uv.lock`, `uv_build` backend).

## Commands

- Install deps: `uv sync`
- Run a script/one-off snippet: `uv run python -c "..."`
- Type check: `uv run pyright src tests` — the project relies heavily on `@overload` + `Literal` types for filter builders; this is the way to catch mistakes there. `[tool.pyright]` in `pyproject.toml` pins `venvPath`/`venv` to `.venv`, so this resolves correctly regardless of invocation method. Avoid `uvx pyright` — `uvx` runs in an isolated environment that can't see the project's installed dependencies (`google-auth`, `requests`), causing spurious import errors.
- Lint: `uv run ruff check .` (add `--fix` to autofix)
- Format: `uv run ruff format .`
- Run tests: `uv run pytest` — single test: `uv run pytest tests/test_filters.py::TestTextFilter::test_single_string`
- `ruff`, `pyright`, and `pytest` are pinned as dev dependencies (`[dependency-groups] dev` in `pyproject.toml`), matching the versions pinned in `.pre-commit-config.yaml` (installed via `prek`/pre-commit: `uv-lock`, `ruff-check --fix`, `ruff-format`, `pyright`).

## Architecture

### Layered structure

- `client.py` — `GAMClient`, the public entry point. Built via `GAMClient.from_service_account_file(...)` or `.from_service_account_info(...)` (wraps `google.oauth2.service_account.Credentials` + `google.auth.transport.requests.AuthorizedSession`). Exposes one resource client per GAM resource as a `cached_property` (e.g. `.custom_targeting`, `.line_item`), each lazily constructed with the shared `network_code` and `HTTPClient`.
- `http_client.py` — `HTTPClient` is a thin authorized-session wrapper. `fetch()` does a single GET (decorated with `@retry()`) and raises on HTTP errors; `fetch_all()` loops `fetch()` following `nextPageToken` until exhausted, collecting the `gam_obj_type` key from each page.
- `retry.py` — `@retry()` decorator: retries on `RETRYABLE_STATUS_CODES` (429/500/502/503/504) and on transient `requests` connection/timeout errors, with exponential backoff. `requests.HTTPError.response` is `Response | None`, so check for `None` before reading `.status_code`.
- `filters.py` — `GAMRestFilters` centralizes building GAM's REST filter-query strings; `BaseRestFilter` is the base class each per-resource `*Filter` extends, implementing `_build_filter_list() -> list[str]` (empty string per absent field) which `get_filter_string()` joins with `AND`.
- `utils.py` — `gam_obj_path`/`gam_obj_id_path` build REST resource paths (`networks/{code}/{type}` / `.../{type}/{id}`), used both as GET endpoints and as the string values compared in id-based filters.
- `services/<resource>.py` — one module per GAM resource (e.g. `custom_targeting.py`, `line_item.py`), each following the same pattern:
  - `Literal[...]` type aliases for the resource's enum fields.
  - A `<Resource>Filter(BaseRestFilter)` holding typed optional fields, building its clause list via `GAMRestFilters` methods.
  - A `<Resource>Client` with `list_<resource>()` (resolves any ID filters through `gam_obj_id_path`, builds the filter string via the `Filter` class, calls `http_client.fetch_all`) and `get_<resource>()` (direct `fetch` by id path).
  - New resources should follow this same shape and get wired into `services/__init__.py` and `client.py`.

### GAM filter-query grammar (important, easy to get wrong)

GAM's REST `filter` parameter has a specific literal grammar (see https://developers.google.com/ad-manager/api/beta/filters) that `GAMRestFilters` exists to encode correctly:

- **Strings** (including resource-path IDs) must be double-quoted: `field = "value"`.
- **Numbers and booleans** must be bare/unquoted: `field = 5`, `archived = true`.
- **DateTimes** must be RFC-3339 and double-quoted: `updateTime >= "2025-01-01T00:00:00+00:00"`.

Always route new filter fields through the matching `GAMRestFilters` method (`text_filter`, `id_based_filter`, `number_filter`, `boolean_filter`, `date_filter`) rather than hand-building clause strings — picking the wrong one silently produces a query the API rejects with a 400.

### Typing pattern for filter methods

`GAMRestFilters`' list-accepting overloads (`text_filter`, `id_based_filter`, `number_filter`) are generic over a `str`/`int`-bound `TypeVar` (`_StrT`, `_IntT`) rather than plain `list[str]`/`list[int]`. This is required because `list[...]` is invariant: a field typed `list[Literal["A", "B"]]` is not assignable to a `list[str]` parameter, so a fixed non-generic overload fails pyright for every `Literal`-typed filter field. When adding new list-accepting filter overloads, follow the same generic-TypeVar pattern.

### Tests

`tests/` unit-tests everything without touching the live Ad Manager API:

- `test_filters.py` — exercises `GAMRestFilters`' quoting rules directly (regression coverage for the filter grammar above).
- `test_retry.py` — exercises `@retry()`'s backoff/give-up logic; `time.sleep` is monkeypatched so tests run instantly.
- `test_http_client.py` — exercises `HTTPClient.fetch`/`fetch_all` by constructing `HTTPClient` with a `Mock(spec=google.auth.credentials.Credentials)` and replacing `.authed_session` with a `Mock`, so no network call is made.
- `test_client.py` — exercises `GAMClient`'s scope defaulting, `.expiry`, and the `.custom_targeting`/`.line_item` `cached_property` wiring; `service_account.Credentials.from_service_account_file`/`from_service_account_info` are monkeypatched so no real key file is needed.
- `test_custom_targeting.py`/`test_line_item.py` — exercise each resource's `*Filter` field-to-clause mapping and `*Client` methods (endpoint construction, ID-path resolution) via `Mock(spec=HTTPClient)`.

Follow the same mocking approach (mock `HTTPClient`/`authed_session`/`service_account.Credentials`, never hit the live API) when adding tests for new resources.
