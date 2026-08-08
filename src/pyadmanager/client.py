"""High-level client for the Google Ad Manager REST API.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest

"""

from datetime import datetime
from functools import cached_property

from google.oauth2 import service_account

from .http_client import HTTPClient
from .services import CustomTargetingClient, LineItemClient

READONLY_SCOPE = "https://www.googleapis.com/auth/admanager.readonly"
FULL_SCOPE = "https://www.googleapis.com/auth/admanager"


class GAMClient:
    def __init__(
        self,
        network_code: str | int,
        auth: service_account.Credentials,
    ):
        self.network_code = str(network_code)
        self.http_client = HTTPClient(auth)

    @classmethod
    def from_service_account_file(
        cls, network_code: str | int, filename: str, readonly: bool = False, **kwargs
    ):
        kwargs.setdefault("scopes", [READONLY_SCOPE if readonly else FULL_SCOPE])
        creds = service_account.Credentials.from_service_account_file(
            filename,
            **kwargs,
        )
        return cls(network_code=network_code, auth=creds)

    @classmethod
    def from_service_account_info(
        cls, network_code: str | int, info: dict, readonly: bool = False, **kwargs
    ):
        kwargs.setdefault("scopes", [READONLY_SCOPE if readonly else FULL_SCOPE])
        creds = service_account.Credentials.from_service_account_info(
            info,
            **kwargs,
        )
        return cls(network_code=network_code, auth=creds)

    @property
    def expiry(self) -> datetime | None:
        """Expiry datetime of the currently loaded credentials, if any."""
        return self.http_client.auth.expiry

    @cached_property
    def custom_targeting(self) -> CustomTargetingClient:
        return CustomTargetingClient(self.network_code, self.http_client)

    @cached_property
    def line_item(self) -> LineItemClient:
        return LineItemClient(self.network_code, self.http_client)
