"""High-level client for the Google Ad Manager REST API.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest

"""

import logging
from datetime import datetime
from functools import cached_property

from google.oauth2 import service_account

from .http_client import HTTPClient
from .services import (
    AdUnitClient,
    CustomTargetingClient,
    LineItemClient,
    NetworkClient,
    OrderClient,
    PlacementClient,
    PrivateAuctionClient,
    PrivateAuctionDealClient,
    ProgrammaticBuyerClient,
    ReportClient,
    RoleClient,
    UserClient,
)

logger = logging.getLogger(__name__)

READONLY_SCOPE = "https://www.googleapis.com/auth/admanager.readonly"
FULL_SCOPE = "https://www.googleapis.com/auth/admanager"


class GAMClient:
    """Entry point for the Google Ad Manager REST API.

    Wraps an `AuthorizedSession` (via `HTTPClient`) for a single `network_code`
    and exposes one resource client per GAM resource as a lazily-constructed,
    cached property (`.custom_targeting`, `.line_item`, `.report`), each sharing
    this client's `network_code` and `HTTPClient`. Prefer the
    `from_service_account_file`/`from_service_account_info` constructors over
    calling `__init__` directly, since they build the `Credentials` object for you.
    """

    def __init__(
        self,
        network_code: str | int,
        auth: service_account.Credentials,
    ):
        """Wrap already-constructed `Credentials` for `network_code`.

        `network_code` is coerced to `str` since GAM REST paths (`networks/{code}/...`)
        are string-formatted regardless of whether the caller has it as an `int`.
        """
        self.network_code = str(network_code)
        self.http_client = HTTPClient(auth)
        logger.debug("GAMClient initialized for network %s", self.network_code)

    @classmethod
    def from_service_account_file(
        cls, network_code: str | int, filename: str, readonly: bool = False, **kwargs
    ):
        """Build a client from a service-account JSON key file on disk.

        `readonly=True` requests `READONLY_SCOPE` instead of `FULL_SCOPE`;
        pass an explicit `scopes=[...]` in `kwargs` to override either default.
        Additional `kwargs` are forwarded to `Credentials.from_service_account_file`.
        """
        kwargs.setdefault("scopes", [READONLY_SCOPE if readonly else FULL_SCOPE])
        logger.info(
            "loading service account credentials from %s (scopes=%s)", filename, kwargs["scopes"]
        )
        creds = service_account.Credentials.from_service_account_file(
            filename,
            **kwargs,
        )
        return cls(network_code=network_code, auth=creds)

    @classmethod
    def from_service_account_info(
        cls, network_code: str | int, info: dict, readonly: bool = False, **kwargs
    ):
        """Build a client from an already-loaded service-account key dict.

        Same scope defaulting as `from_service_account_file`; use this
        variant when the key material comes from a secrets manager rather
        than a file on disk.
        """
        kwargs.setdefault("scopes", [READONLY_SCOPE if readonly else FULL_SCOPE])
        # Deliberately not logging `info` — it contains the private key.
        logger.info(
            "loading service account credentials from info dict (scopes=%s)", kwargs["scopes"]
        )
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
        """`CustomTargetingClient` for this network, built once and cached."""
        return CustomTargetingClient(self.network_code, self.http_client)

    @cached_property
    def line_item(self) -> LineItemClient:
        """`LineItemClient` for this network, built once and cached."""
        return LineItemClient(self.network_code, self.http_client)

    @cached_property
    def report(self) -> ReportClient:
        """`ReportClient` for this network, built once and cached."""
        return ReportClient(self.network_code, self.http_client)

    @cached_property
    def network(self) -> NetworkClient:
        """`NetworkClient` for this network, built once and cached."""
        return NetworkClient(self.network_code, self.http_client)

    @cached_property
    def role(self) -> RoleClient:
        """`RoleClient` for this network, built once and cached."""
        return RoleClient(self.network_code, self.http_client)

    @cached_property
    def user(self) -> UserClient:
        """`UserClient` for this network, built once and cached."""
        return UserClient(self.network_code, self.http_client)

    @cached_property
    def placement(self) -> PlacementClient:
        """`PlacementClient` for this network, built once and cached."""
        return PlacementClient(self.network_code, self.http_client)

    @cached_property
    def order(self) -> OrderClient:
        """`OrderClient` for this network, built once and cached."""
        return OrderClient(self.network_code, self.http_client)

    @cached_property
    def ad_unit(self) -> AdUnitClient:
        """`AdUnitClient` for this network, built once and cached."""
        return AdUnitClient(self.network_code, self.http_client)

    @cached_property
    def private_auction(self) -> PrivateAuctionClient:
        """`PrivateAuctionClient` for this network, built once and cached."""
        return PrivateAuctionClient(self.network_code, self.http_client)

    @cached_property
    def private_auction_deal(self) -> PrivateAuctionDealClient:
        """`PrivateAuctionDealClient` for this network, built once and cached."""
        return PrivateAuctionDealClient(self.network_code, self.http_client)

    @cached_property
    def programmatic_buyer(self) -> ProgrammaticBuyerClient:
        """`ProgrammaticBuyerClient` for this network, built once and cached."""
        return ProgrammaticBuyerClient(self.network_code, self.http_client)
