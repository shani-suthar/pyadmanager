# pyadmanager

**A simple, modern Python REST client for the Google Ad Manager API.**

[![PyPI version](https://img.shields.io/pypi/v/pyadmanager.svg?cachebust=1)](https://pypi.org/project/pyadmanager/)
[![Python versions](https://img.shields.io/pypi/pyversions/pyadmanager.svg?cachebust=1)](https://pypi.org/project/pyadmanager/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://github.com/shani-suthar/pyadmanager/blob/main/LICENSE)
[![Build status](https://github.com/shani-suthar/pyadmanager/actions/workflows/code-quality.yaml/badge.svg)](https://github.com/shani-suthar/pyadmanager/actions/workflows/code-quality.yaml)

## Overview / Why pyadmanager?

`pyadmanager` is a **developer-friendly** way to read data out of Google Ad Manager: typed, autocomplete-able filter builders, automatic pagination and retries, and one `GAMClient` entry point — no code generation, no WSDL, no hand-built query strings.

For comparison, Google offers two official clients:

- [`googleads`](https://pypi.org/project/googleads/) — the legacy SOAP API client. Powerful, but heavyweight and tied to SOAP's older, more ceremonious request/response model.
- [`google-ads-admanager`](https://pypi.org/project/google-ads-admanager/) — the official REST API (v1) client, code-generated from the API's protobuf definitions. Complete, but as with most generated clients, it prioritizes full API coverage over an ergonomic, idiomatic-Python feel.

`pyadmanager` targets that same REST API but is hand-written for ergonomics: it trades full write-API coverage (it's read-only today — see [Roadmap](#roadmap)) for a small, typed surface that's easy to read, autocomplete, and reason about. If you just need to pull line items, run a report, or look up custom targeting keys through the [Ad Manager REST API (v1)](https://developers.google.com/ad-manager/api/beta/reference/rest), it does that without you needing to hand-roll `requests` calls or re-derive GAM's filter-query grammar (`field = "value"` for strings, bare `true`/`false` for booleans, RFC-3339 strings for dates) yourself.

`pyadmanager` wraps that REST API in a thin, typed client:

- One `GAMClient` entry point, one resource client per GAM resource (`.line_item`, `.report`, `.order`, ...), each built lazily and cached.
- Typed `list_*` filter keyword arguments per resource so your editor autocompletes valid filter fields and `Literal` enum values (e.g. `LineItemType`), and `pyright` catches typos before you hit the API.
- Pagination, retries (with exponential backoff on 429/500/502/503/504), and GAM's filter-string quoting rules handled for you.
- **Read-only today.** Every resource client currently only implements `list_*`/`get_*`, even for resources where the REST API supports writes. `create`/`update`/`delete` support is on the [roadmap](#roadmap) — if you need write access right now, this isn't yet the library for you.

It's aimed at ad-ops engineers and backend developers who need to read Ad Manager data (line items, orders, reports, inventory) into Python — for dashboards, ETL pipelines, or one-off scripts — without pulling in the full `googleads` SOAP stack.

## Features

- **Typed, per-resource clients** — `line_item`, `order`, `placement`, `ad_unit`, `custom_targeting`, `role`, `user`, `network`, `private_auction`, `private_auction_deal`, `programmatic_buyer`, and `report`.
- **Correct GAM filter-string building** — `GAMRestFilters` centralizes the quoting rules (quoted strings/dates, bare numbers/booleans) so you never hand-write a malformed `filter` query param.
- **Automatic pagination** — `list_*` methods page through `nextPageToken` and return the fully collected list.
- **Built-in retry with backoff** — transient errors (429/500/502/503/504, connection/timeout errors) are retried automatically.
- **Async report support** — `run_report()` kicks off a GAM report job and returns a `ReportJob` you can poll and pull rows from, optionally parsed straight into a `polars.DataFrame`.
- **Cross-resource id resolution** — pass a bare `order_id`/`key_id`/`parent_ad_unit_id` int and it's resolved into the correct GAM resource path for you.

## Installation

Requires **Python 3.13+**.

```bash
pip install pyadmanager
```

To use `ReportJob.fetch_rows_as_dataframe()` / `parse_report_rows()`, install the optional `polars` extra:

```bash
pip install "pyadmanager[polars]"
```

Without the extra, everything else works normally — `parse_report_rows` just raises a clear `ImportError` if you call it without `polars` installed.

## Quick Start (The 80/20 Example)

```python
from pyadmanager import GAMClient

client = GAMClient.from_service_account_file(
    network_code="123456789",
    filename="creds.json",
    readonly=True,  # requests the read-only OAuth scope
)

# List every non-archived line item for a given order
line_items = client.line_item.list_line_items(order_id=98765, archived=False)

for item in line_items:
    print(item["displayName"], item["status"])
```

## Detailed Usage & Code Examples

### Basic Example

```python
from pyadmanager import GAMClient

client = GAMClient.from_service_account_file(
    network_code="123456789",
    filename="creds.json",
)

# Fetch a single line item by numeric id
line_item = client.line_item.get_line_item(line_item_id=112233)
print(line_item["name"], line_item["lineItemType"])

# List active custom targeting keys
keys = client.custom_targeting.list_keys(status="ACTIVE")
for key in keys:
    print(key["displayName"])
```

### Advanced Example

```python
from datetime import datetime, timedelta, timezone

from pyadmanager import GAMClient
from pyadmanager.filters import GAMRestFilters

client = GAMClient.from_service_account_file(
    network_code="123456789",
    filename="creds.json",
)

# Filter using a (value, filter_type) tuple to build CONTAINS/GT_EQ-style clauses
one_week_ago = datetime.now(timezone.utc) - timedelta(days=7)

delivering_line_items = client.line_item.list_line_items(
    display_name=("Q3", "CONTAINS"),  # displayName = "*Q3*"
    status=["DELIVERING", "READY"],  # (status = "DELIVERING" OR status = "READY")
    start_time=(one_week_ago, "GT_EQ"),  # startTime >= "2026-..."
    page_size=500,  # tune the page size (default 1000)
)

# Run a saved report and pull results straight into a polars DataFrame
# (requires: pip install "pyadmanager[polars]")
job = client.report.run_report(report_id=445566)
df = job.fetch_rows_as_dataframe()  # polls until GAM finishes computing rows
print(df.head())

# Handle report failures explicitly instead of letting fetch_rows_as_dataframe raise
try:
    job.wait_till_complete(sleep=5.0)
except ValueError as exc:
    print("report job failed:", exc)
else:
    rows = job.fetch_rows()  # raw pages, if you'd rather parse them yourself
```

## API Overview / Key Reference

| Class / Method | Inputs | Output | Description |
| --- | --- | --- | --- |
| `GAMClient.from_service_account_file(network_code, filename, readonly=False, **kwargs)` | GAM network code, path to a service-account JSON key, optional `readonly` flag | `GAMClient` | Builds credentials from a key file on disk and returns a ready-to-use client. |
| `GAMClient.from_service_account_info(network_code, info, readonly=False, **kwargs)` | GAM network code, service-account key as a `dict` | `GAMClient` | Same as above, for key material loaded from a secrets manager rather than a file. |
| `GAMClient.<resource>` | — | resource client (e.g. `LineItemClient`) | Lazily built, cached per-resource client sharing the parent's network code and session. |
| `<Resource>Client.list_<resource>(**filters, page_size=1000)` | typed filter kwargs per resource | `list[dict]` | Pages through every matching result via `nextPageToken`. |
| `<Resource>Client.get_<resource>(id)` | numeric resource id | `dict` | Fetches a single resource by id. |
| `ReportClient.run_report(report_id)` | numeric report id | `ReportJob` | Starts async generation of a saved report's rows. |
| `ReportJob.wait_till_complete(sleep=2.5)` | poll interval (seconds) | `None` | Blocks until the report job is done; raises `ValueError` on job failure. |
| `ReportJob.fetch_rows(sleep=2.5)` | poll interval (seconds) | `list[dict]` | Polls to completion if needed, then returns raw report result pages. |
| `ReportJob.fetch_rows_as_dataframe(sleep=2.5)` | poll interval (seconds) | `polars.DataFrame` | Same as `fetch_rows`, parsed into a DataFrame (requires the `polars` extra). |
| `GAMRestFilters.text_filter/number_filter/boolean_filter/date_filter/id_based_filter` | field name, value (or `(value, FILTER_TYPE)` tuple) | `str` | Low-level building blocks for GAM's filter-query grammar — used internally by every resource's `list_*` method. |

## Configuration & Customization

- **Auth scope** — `from_service_account_file`/`from_service_account_info` default to the full `https://www.googleapis.com/auth/admanager` scope; pass `readonly=True` for `https://www.googleapis.com/auth/admanager.readonly`, or an explicit `scopes=[...]` kwarg to override either default.
- **Extra credential kwargs** — any additional keyword arguments passed to the `from_service_account_*` constructors are forwarded directly to `google.oauth2.service_account.Credentials`.
- **Page size** — every `list_*` method accepts `page_size` (default `1000`) to tune how many results are fetched per underlying HTTP request; pagination across pages happens automatically regardless of this value.
- **Report poll interval** — `ReportJob.wait_till_complete`/`fetch_rows`/`fetch_rows_as_dataframe` accept a `sleep` argument (default `2.5` seconds) controlling how often the async report job's status is polled.
- **Logging** — the library logs via the standard `logging` module (`logging.getLogger("pyadmanager...")`); enable `DEBUG` logging to see outgoing request URLs/params and report-job poll iterations, or `INFO` for lifecycle events like credential loading and report job completion.

## Roadmap

- **Write support** (`create`/`update`/`delete`) for resources where the underlying REST API supports it (e.g. `orders`, `lineItems`, `placements`, `adUnits`). The library is read-only today; this is the main planned expansion of scope.
- New resource coverage, following the existing `services/<resource>.py` pattern as GAM's REST API surface grows.

Have a resource or write operation you need sooner? Open an issue — it helps prioritize the roadmap.

## Contributing

Contributions are welcome! To get set up locally:

```bash
uv sync --extra polars   # install all deps, including the optional polars extra
uv run pytest            # run the test suite
uv run ruff check .      # lint
uv run pyright src tests # type check
```

Please open an issue before starting on a larger change, especially write support (see [Roadmap](#roadmap)) so the approach can be agreed on before you invest the time. Bug reports and PRs for new read-only resources are especially appreciated — see `services/` for the pattern each resource client follows.

## License

MIT — see [LICENSE](https://github.com/shani-suthar/pyadmanager/blob/main/LICENSE) for details.
