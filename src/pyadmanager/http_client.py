"""Low-level HTTP client for the Google Ad Manager REST API.

`HTTPClient` is the single object every `services/*.py` `*Client` is built
around: it owns the `AuthorizedSession` and knows how to make one authenticated
GET/POST (`fetch`) and how to page through a paginated list response
(`fetch_all`, `fetch_report_rows`). Resource clients call these two, then hand
the result to their own filter/parsing logic.
"""

import logging
from typing import Any, Literal

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from .retry import retry

logger = logging.getLogger(__name__)

BASE_URL = "https://admanager.googleapis.com/v1"

HTTPRequestMethod = Literal["GET", "POST"]


class HTTPClient:
    """
    Authorized `requests` session with retry and page-following support.
    """

    def __init__(self, credentials: service_account.Credentials) -> None:
        """Build an `AuthorizedSession` from `credentials` for `BASE_URL`.

        `credentials` is typically a `google.oauth2.service_account.Credentials`
        built by `GAMClient.from_service_account_file`/`from_service_account_info`;
        it's stored as `.auth` so callers (e.g. `GAMClient.expiry`) can inspect it.
        """
        self.base_url = BASE_URL
        self.auth = credentials
        self.authed_session = AuthorizedSession(self.auth)

    @retry()
    def fetch(
        self, endpoint: str, params: dict | None = None, http_method: HTTPRequestMethod = "GET"
    ) -> Any:
        """Make one authenticated request to `{base_url}/{endpoint}` and return parsed JSON.

        Raises `requests.HTTPError` via `resp.raise_for_status()` on a non-2xx
        response — the `@retry()` decorator retries that error automatically
        for retryable status codes (see `retry.RETRYABLE_STATUS_CODES`) before
        it propagates here. Callers needing every page of a list response
        should use `fetch_all`/`fetch_report_rows` instead of calling this directly.
        """
        url = f"{self.base_url}/{endpoint}"
        logger.debug("fetching %s params=%s", url, params)
        resp = self.authed_session.request(http_method, url, params=params, cookies={})
        resp.raise_for_status()
        return resp.json()

    def fetch_all(self, endpoint: str, gam_obj_type: str, params: dict | None = None) -> list:
        """Fetch every page of `gam_obj_type` from `endpoint`, following `nextPageToken`.

        Each page's response is a dict keyed by `gam_obj_type` (e.g.
        `{"lineItems": [...], "nextPageToken": "..."}`); this flattens all
        pages' `gam_obj_type` lists into one combined list, rather than
        returning the raw per-page envelopes (compare `fetch_report_rows`,
        which does keep the raw pages).
        """
        results = []
        next_page_token = None
        if params is None:
            params = {}

        while True:
            if next_page_token:
                params["pageToken"] = next_page_token

            data = self.fetch(endpoint, params)

            results.extend(data.get(gam_obj_type, []))

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        logger.debug("fetch_all %s: collected %d %s", endpoint, len(results), gam_obj_type)
        return results

    def fetch_report_rows(self, endpoint: str) -> list:
        """Fetch every page of a `:fetchRows` report result, following `nextPageToken`.

        Unlike `fetch_all`, this appends each page's *raw* response dict
        (rows plus its own `dateRanges`/`runTime`/`totalRowCount`) rather
        than extracting a single key, since a report page carries no single
        "collection" field to flatten. `services.report.parse_report_rows`
        expects exactly this list-of-raw-pages shape. Uses a fixed
        `pageSize=10_000` (GAM's max) rather than accepting one from the
        caller, since report rows have no natural per-request tuning need.
        """
        results = []
        next_page_token = None
        params = {"pageSize": 10_000}

        while True:
            if next_page_token:
                params["pageToken"] = next_page_token

            data = self.fetch(endpoint, params)

            results.append(data)

            next_page_token = data.get("nextPageToken")
            if not next_page_token:
                break

        logger.debug("fetch_report_rows %s: collected %d page(s)", endpoint, len(results))
        return results
