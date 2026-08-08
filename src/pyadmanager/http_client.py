"""Low-level HTTP client for the Google Ad Manager REST API."""

import logging
from typing import Any

from google.auth.transport.requests import AuthorizedSession
from google.oauth2 import service_account

from .retry import retry

logger = logging.getLogger(__name__)

BASE_URL = "https://admanager.googleapis.com/v1"


class HTTPClient:
    """
    Authorized `requests` session with retry and page-following support.
    """

    def __init__(self, credentials: service_account.Credentials) -> None:
        self.base_url = BASE_URL
        self.auth = credentials
        self.authed_session = AuthorizedSession(self.auth)

    @retry()
    def fetch(self, endpoint: str, params: dict | None = None) -> Any:
        url = f"{self.base_url}/{endpoint}"
        logger.debug("fetching %s params=%s", url, params)
        resp = self.authed_session.get(url, params=params, cookies={})
        resp.raise_for_status()
        return resp.json()

    def fetch_all(self, endpoint: str, gam_obj_type: str, params: dict | None = None) -> list:
        """Fetch every page of `gam_obj_type` from `endpoint`, following `nextPageToken`."""
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

        return results
