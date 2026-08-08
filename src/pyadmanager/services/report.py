"""Filter builder for the Reports GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.reports
"""

import logging
import time
from typing import TYPE_CHECKING

from ..filters import GAMRestFilters, get_filter_string
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

if TYPE_CHECKING:
    import polars as pl

logger = logging.getLogger(__name__)

DEFAULT_SLEEP_TIME = 2.5


def _unwrap_value(value: dict[str, str | float]) -> str | int | float | None:
    """Unwrap a GAM `DimensionValue`/`MetricValue` oneof dict to its scalar.

    `intValue` is JSON-encoded as a string (proto64 int64 convention), so it is
    cast back to `int`. `doubleValue` is cast to `float` since whole numbers
    (e.g. `0`) decode as `int` otherwise, mixing types within a column. An
    empty dict means the oneof is unset (null).
    """
    if not value:
        return None
    ((kind, raw),) = value.items()
    if kind == "intValue":
        return int(raw)
    if kind == "doubleValue":
        return float(raw)
    return raw


def parse_report_rows(
    pages: list[dict],
    dimensions: list[str],
    metrics: list[str],
) -> "pl.DataFrame":
    """Parse `ReportJob.fetch_rows()` pages into a single polars DataFrame.

    `dimensions`/`metrics` are the same-order lists from the report's
    `reportDefinition` (see `ReportClient.get_report`) — each row's
    `dimensionValues`/`metricValueGroups[0].primaryValues` line up with them
    positionally. Assumes a single metric value group per row (no comparison
    date range).

    Raises:
        ValueError: if a row's `dimensionValues`/`primaryValues` count doesn't
            match `dimensions`/`metrics`.
    """
    try:
        import polars as pl
    except ImportError as e:
        raise ImportError(
            "polars is required to parse report rows into a DataFrame. "
            "Install it with `pip install pyadmanager[polars]` (or `uv sync --extra polars`)."
        ) from e

    n_dims = len(dimensions)
    n_metrics = len(metrics)
    columns: list[list[str | int | float | None]] = [[] for _ in range(n_dims + n_metrics)]

    for page in pages:
        for row in page["rows"]:
            row_dims = row["dimensionValues"]
            if len(row_dims) != n_dims:
                raise ValueError(
                    f"row has {len(row_dims)} dimensionValues, expected {n_dims} "
                    f"to match dimensions={dimensions}: {row}"
                )
            for i, value in enumerate(row_dims):
                columns[i].append(_unwrap_value(value))

            row_metrics = row["metricValueGroups"][0]["primaryValues"]
            if len(row_metrics) != n_metrics:
                raise ValueError(
                    f"row has {len(row_metrics)} metric values, expected {n_metrics} "
                    f"to match metrics={metrics}: {row}"
                )
            for i, value in enumerate(row_metrics):
                columns[n_dims + i].append(_unwrap_value(value))

    return pl.DataFrame(dict(zip(dimensions + metrics, columns, strict=True)))


class ReportJob:
    """Handle for an in-flight (or completed) `reports:run` operation.

    Returned by `ReportClient.run_report`. GAM report generation is
    asynchronous: `run_report` only kicks off the job, so this class polls
    the operation until it's `done` (`wait_till_complete`) before it can
    fetch the actual rows (`fetch_rows`/`fetch_rows_as_dataframe`).
    `result_path` is `None` until that poll succeeds, at which point it's
    cached on the instance so a second `fetch_rows` call skips re-polling.
    """

    def __init__(
        self,
        obj_metadata: dict,
        network_code: str,
        http_client: HTTPClient,
    ) -> None:
        """Derive `job_path`/`report_path` from the `reports:run` response `obj_metadata`.

        `job_path` (`obj_metadata["name"]`) is the long-running operation to
        poll; `report_path` (`obj_metadata["metadata"]["report"]`) is the
        underlying `reports/{id}` resource, needed later by
        `fetch_rows_as_dataframe` to look up `reportDefinition`.
        """
        self.obj_metadata = obj_metadata
        self.network_code = network_code
        self.http_client = http_client
        self.report_path = obj_metadata["metadata"]["report"]
        self.job_path = obj_metadata["name"]
        self.result_path: str | None = None

    def check_job_status(self):
        """Fetch the operation's current status metadata (does not update `self.result_path`)."""
        status_metadata = self.http_client.fetch(self.job_path)
        logger.debug("job %s status: %s", self.job_path, status_metadata)
        return status_metadata

    def fetch_rows(self, sleep: float = DEFAULT_SLEEP_TIME):
        """Return every raw report-result page, polling to completion first if needed.

        If `result_path` isn't known yet, blocks via `wait_till_complete`
        (polling every `sleep` seconds) before fetching. Returns the same
        list-of-pages shape `services.report.parse_report_rows` expects —
        use `fetch_rows_as_dataframe` instead if you want a parsed DataFrame.
        """
        if self.result_path is None:
            self.wait_till_complete(sleep=sleep)

        endpoint = f"{self.result_path}:fetchRows"
        rows = self.http_client.fetch_report_rows(endpoint)
        return rows

    def wait_till_complete(self, sleep: float = DEFAULT_SLEEP_TIME):
        """Poll `check_job_status` every `sleep` seconds until the operation reports `done`.

        On completion, caches the final status as `self.obj_metadata` and
        its `response.reportResult` path as `self.result_path`. Raises
        `ValueError` if the operation status carries an `error` field.
        """
        while True:
            status_metadata = self.check_job_status()
            if status_metadata.get("done", False):
                self.obj_metadata = status_metadata
                self.result_path = status_metadata["response"]["reportResult"]
                logger.info("job %s completed, result at %s", self.job_path, self.result_path)
                break
            if status_metadata.get("error", False):
                logger.error("job %s failed: %s", self.job_path, status_metadata["error"])
                raise ValueError(status_metadata["error"])
            logger.debug("job %s not done yet, sleeping %.1fs", self.job_path, sleep)
            time.sleep(sleep)

    def fetch_rows_as_dataframe(self, sleep: float = DEFAULT_SLEEP_TIME):
        """Fetch this job's rows and parse them into a polars DataFrame.

        Looks up the underlying report's `reportDefinition` (for its
        `dimensions`/`metrics` ordering) via `self.report_path`, then delegates
        to `parse_report_rows`. Requires the `polars` extra — see
        `parse_report_rows` for the `ImportError` raised if it isn't installed.
        """
        pages = self.fetch_rows(sleep=sleep)
        report_metadata = self.http_client.fetch(self.report_path)
        report_definition = report_metadata["reportDefinition"]
        df = parse_report_rows(
            pages,
            report_definition["dimensions"],
            report_definition["metrics"],
        )
        return df


class ReportClient:
    """Client for the `reports` GAM REST resource.

    `list_reports`/`get_report` read saved report definitions;
    `run_report` kicks off asynchronous generation of a report's rows and
    returns a `ReportJob` to poll/fetch them.
    """

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "reports"

    def list_reports(
        self,
        report_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        page_size: int = 1000,
    ):
        """List `reports`, paging through every result via `HTTPClient.fetch_all`.

        `report_id` resolves to `reports/{id}` path(s) via
        `utils.gam_obj_id_path` before filtering; fields left as `None` are
        omitted from the filter.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_obj_type)

        report_id_str = gam_obj_id_path(report_id, self.network_code, self._gam_obj_type)

        filter_list = [
            GAMRestFilters.id_based_filter("name", report_id_str),
            GAMRestFilters.text_filter("displayName", display_name),
        ]

        filter_str = get_filter_string(filter_list)

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get_report(self, report_id: int):
        """Fetch a single `report`'s definition (including its `reportDefinition`) by numeric id."""
        endpoint = gam_obj_id_path(report_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)

    def run_report(self, report_id: int):
        """Start asynchronous generation of `report_id`'s rows and return a `ReportJob` to track it.

        This only kicks off the operation — call `ReportJob.fetch_rows`/
        `fetch_rows_as_dataframe` on the returned job to poll it to
        completion and retrieve the actual rows.
        """
        endpoint = f"{gam_obj_id_path(report_id, self.network_code, self._gam_obj_type)}:run"
        job_metadata = self.http_client.fetch(endpoint, http_method="POST")
        logger.info("started report job %s for report %s", job_metadata["name"], report_id)
        return ReportJob(job_metadata, self.network_code, self.http_client)
