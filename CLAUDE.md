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
- `ruff`, `pyright`, and `pytest` are pinned as dev dependencies (`[dependency-groups] dev` in `pyproject.toml`), matching the versions pinned in `.pre-commit-config.yaml` (installed via `prek`/pre-commit: `uv-lock`, `ruff-check --fix`, `ruff-format`, `pyright`, `pytest`).
- `polars` is an optional extra (`[project.optional-dependencies]`), needed for `services/report.py`'s `parse_report_rows`/`ReportJob.fetch_rows_as_dataframe`: `uv sync --extra polars`. Without it, `parse_report_rows` raises a clear `ImportError` at call time rather than failing on import, and `test_report.py`'s dataframe tests skip via `pytest.importorskip("polars")`.

## Architecture

### Layered structure

- `client.py` — `GAMClient`, the public entry point. Built via `GAMClient.from_service_account_file(...)` or `.from_service_account_info(...)` (wraps `google.oauth2.service_account.Credentials` + `google.auth.transport.requests.AuthorizedSession`). Exposes one resource client per GAM resource as a `cached_property`, each lazily constructed with the shared `network_code` and `HTTPClient`: `.custom_targeting`, `.line_item`, `.report`, `.network`, `.role`, `.user`, `.placement`, `.order`, `.ad_unit`, `.private_auction`, `.private_auction_deal`, `.programmatic_buyer`.
- `http_client.py` — `HTTPClient` is a thin authorized-session wrapper. `fetch()` does a single request (decorated with `@retry()`) and raises on HTTP errors; `fetch_all()` loops `fetch()` following `nextPageToken` until exhausted, collecting the `gam_obj_type` key from each page; `fetch_report_rows()` does the same paging but keeps each page's raw envelope instead (reports have no single collection key to flatten — see `services/report.py`).
- `retry.py` — `@retry()` decorator: retries on `RETRYABLE_STATUS_CODES` (429/500/502/503/504) and on transient `requests` connection/timeout errors, with exponential backoff. `requests.HTTPError.response` is `Response | None`, so check for `None` before reading `.status_code`. Logs a `warning` per retry attempt and an `error` when retries are exhausted (`func.__qualname__` isn't safe to read directly on arbitrary callables — e.g. a bare `unittest.mock.Mock` raises `AttributeError` on dunder access — so it's resolved once via `getattr(..., None) or repr(func)`).
- `filters.py` — `GAMRestFilters` centralizes building GAM's REST filter-query strings, one method per field type (`text_filter`, `id_based_filter`, `number_filter`, `boolean_filter`, `date_filter`), each returning a single clause string (`""` for an absent field). `get_filter_string(filters: list[str])` drops empty clauses and joins the rest with `AND`.
- `utils.py` — `gam_obj_path`/`gam_obj_id_path` build REST resource paths (`networks/{code}/{type}` / `.../{type}/{id}`), used both as GET endpoints and as the string values compared in id-based filters.
- `services/<resource>.py` — one module per GAM resource, each following the same pattern:
  - `Literal[...]` type aliases for the resource's enum fields.
  - A `<Resource>Client` with `list_<resource>()` (resolves any ID filters through `gam_obj_id_path`, builds a list of clause strings inline via `GAMRestFilters` methods, joins them with `filters.get_filter_string()`, then calls `http_client.fetch_all`) and `get_<resource>()` (direct `fetch` by id path).
  - New resources should follow this same shape and get wired into `services/__init__.py` and `client.py`.
  - **Read-only by design**: even when the real GAM REST resource supports `create`/`patch`/batch write operations (e.g. `orders`, `adUnits`, `placements`), only `list_*`/`get_*` are implemented — no resource client in this library performs writes. Don't add write methods without discussing scope first.
  - **Cross-resource id fields**: a field on one resource that references another resource by id (e.g. `LineItemClient`'s `order_id` → `orders`, `OrderClient`'s `trafficker_id`/`salesperson_id` → `users`, `AdUnitClient`'s `parent_ad_unit_id` → `adUnits` itself, `PrivateAuctionDealClient`'s `private_auction_id`/`buyer_account_id` → `privateAuctions`/`programmaticBuyers`) is resolved via `gam_obj_id_path(id, network_code, "<other_gam_obj_type>")` — the `gam_obj_type` string passed doesn't have to match the client's own resource type.
  - **Not every resource fits the full shape**: `networks` is top-level (`networks/{code}`, not nested under a network, no filter fields — see `network.py`) and `users` has no `list` method at all (`get` only — see `user.py`); check the module's docstring before assuming every resource has both `list_*`/`get_*` methods.
- `services/report.py` is the one resource with meaningfully different behavior: `ReportClient.run_report()` starts async report generation and returns a `ReportJob`, which polls (`wait_till_complete`/`fetch_rows`) until GAM finishes computing rows, then `fetch_rows_as_dataframe()`/`parse_report_rows()` parse the raw pages into a `polars.DataFrame` (lazy-imported so the base install doesn't need `polars`).

### GAM filter-query grammar (important, easy to get wrong)

GAM's REST `filter` parameter has a specific literal grammar (see https://developers.google.com/ad-manager/api/beta/filters) that `GAMRestFilters` exists to encode correctly:

- **Strings** (including resource-path IDs) must be double-quoted: `field = "value"`.
- **Numbers and booleans** must be bare/unquoted: `field = 5`, `archived = true`.
- **DateTimes** must be RFC-3339 and double-quoted: `updateTime >= "2025-01-01T00:00:00+00:00"`.

Always route new filter fields through the matching `GAMRestFilters` method (`text_filter`, `id_based_filter`, `number_filter`, `boolean_filter`, `date_filter`) rather than hand-building clause strings — picking the wrong one silently produces a query the API rejects with a 400.

### Typing pattern for filter methods

`GAMRestFilters`' list-accepting overloads (`text_filter`, `id_based_filter`, `number_filter`) are generic over a `str`/`int`-bound `TypeVar` (`_StrT`, `_IntT`) rather than plain `list[str]`/`list[int]`. This is required because `list[...]` is invariant: a field typed `list[Literal["A", "B"]]` is not assignable to a `list[str]` parameter, so a fixed non-generic overload fails pyright for every `Literal`-typed filter field. When adding new list-accepting filter overloads, follow the same generic-TypeVar pattern.

### Logging

Every module that does real work (`client.py`, `http_client.py`, `retry.py`, `services/report.py`) has its own `logger = logging.getLogger(__name__)` and logs at the level matching what happened, not just "something happened":

- `debug` — routine/expected detail (an outgoing request's URL and params, a poll iteration that isn't done yet, `GAMClient` construction).
- `info` — a lifecycle event worth knowing about even without debug logging on (loading credentials, a report job starting/completing).
- `warning` — an operation failed but is being retried.
- `error` — an operation failed and is being given up on / raised.

The thin per-resource `services/<resource>.py` clients (everything except `report.py`) deliberately have **no** logging of their own — the request they build is already logged one layer down in `HTTPClient.fetch`, so adding logging there would just duplicate it. Only add logging to a new module if it has behavior `http_client.py`/`retry.py` doesn't already surface (e.g. an async polling loop, like `report.py`'s `ReportJob`).

### Tests

`tests/` unit-tests everything without touching the live Ad Manager API:

- `conftest.py` — shared `fake_http_client` fixture (`Mock(spec=HTTPClient)`) used by every `services/<resource>.py` test file; don't redefine it locally.
- `test_filters.py` — exercises `GAMRestFilters`' quoting rules directly (regression coverage for the filter grammar above), plus `get_filter_string`'s clause-joining behavior.
- `test_utils.py` — exercises `gam_obj_path`/`gam_obj_id_path`'s path-building and id/list/`None` overload behavior.
- `test_retry.py` — exercises `@retry()`'s backoff/give-up logic; `time.sleep` is monkeypatched so tests run instantly.
- `test_http_client.py` — exercises `HTTPClient.fetch`/`fetch_all`/`fetch_report_rows` via the local `http_client` fixture (a real `HTTPClient` with a `Mock(spec=google.auth.credentials.Credentials)` and a `Mock()` `.authed_session`, so no network call is made). Note this fixture is also named `http_client` but is unrelated to `conftest.py`'s `fake_http_client` — this file constructs a real `HTTPClient` to test its own internals, the other files mock `HTTPClient` itself to test callers of it.
- `test_client.py` — exercises `GAMClient`'s scope defaulting, `.expiry`, and every resource `cached_property`'s wiring/caching; `service_account.Credentials.from_service_account_file`/`from_service_account_info` are monkeypatched so no real key file is needed.
- `test_<resource>.py` (one per `services/<resource>.py`) — exercises each resource's `*Client` methods: filter-clause building per field (quoting rules, ID-path resolution including any cross-resource references) and endpoint construction, via the shared `fake_http_client` fixture.
- `test_report.py` — additionally covers `ReportJob`'s polling state machine and `parse_report_rows`'s dataframe building/error paths; dataframe-building tests use `pytest.importorskip("polars")` so the suite still passes without the `polars` extra installed.

Follow the same mocking approach (mock `HTTPClient`/`authed_session`/`service_account.Credentials`, never hit the live API) when adding tests for new resources.

### Live smoke test

`live_test.py` (repo root, not part of the pytest suite) exercises every resource client against a **real** GAM network using a `creds.json` service account key file — run manually via `uv run python live_test.py`, never automatically. It's a flat, sequential script (each call's output printed, then a `SLEEP_SECONDS` pause) rather than using any helper abstraction, so individual blocks are easy to comment out. When adding a new resource client, add a corresponding block here too: for resources with no natural hardcoded id to test `get_*` with, discover one from the preceding `list_*` call's first result (see the `role`/`placement`/`order` blocks) rather than hardcoding a guessed id.
