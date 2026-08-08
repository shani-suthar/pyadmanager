"""Filter builder for the PrivateAuctionDeals GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.privateAuctionDeals
"""

from datetime import datetime
from typing import Literal

from ..filters import BaseRestFilter, GAMRestFilters
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

PrivateAuctionDealStatus = Literal[
    "PENDING", "ACTIVE", "CANCELED", "SELLER_PAUSED", "BUYER_PAUSED", "COMPLETED"
]
PrivateAuctionDealBuyerPermissionType = Literal["NEGOTIATOR_ONLY", "BIDDER"]


class PrivateAuctionDealFilter(BaseRestFilter):
    """Filter for `PrivateAuctionDealClient.list_private_auction_deals`.

    One field per `privateAuctionDeals` REST filter field.
    """

    def __init__(
        self,
        name: str | list[str] | None = None,
        private_auction: str | list[str] | None = None,
        buyer_account: str | list[str] | None = None,
        external_deal_id: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        status: PrivateAuctionDealStatus | list[PrivateAuctionDealStatus] | None = None,
        buyer_permission_type: PrivateAuctionDealBuyerPermissionType
        | list[PrivateAuctionDealBuyerPermissionType]
        | None = None,
        auction_priority_enabled: bool | None = None,
        block_override_enabled: bool | None = None,
        end_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        create_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        update_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
    ):
        """Store filter field values.

        Id-reference fields are expected to already be full resource paths —
        `PrivateAuctionDealClient.list_private_auction_deals` resolves bare
        `private_auction_deal_id`/`private_auction_id`/`buyer_account_id`
        ints to `name`/`privateAuctionId`/`buyerAccountId` via
        `utils.gam_obj_id_path` before constructing this filter.
        `privateAuctionId` resolves against `privateAuctions`,
        `buyerAccountId` against `programmaticBuyers`, despite
        `privateAuctionDeals` itself being a flat top-level resource (not
        nested under either).
        """
        self.name = name
        self.private_auction = private_auction
        self.buyer_account = buyer_account
        self.external_deal_id = external_deal_id
        self.status = status
        self.buyer_permission_type = buyer_permission_type
        self.auction_priority_enabled = auction_priority_enabled
        self.block_override_enabled = block_override_enabled
        self.end_time = end_time
        self.create_time = create_time
        self.update_time = update_time

    def _build_filter_list(self) -> list[str]:
        return [
            GAMRestFilters.id_based_filter("name", self.name),
            GAMRestFilters.id_based_filter("privateAuctionId", self.private_auction),
            GAMRestFilters.id_based_filter("buyerAccountId", self.buyer_account),
            GAMRestFilters.text_filter("externalDealId", self.external_deal_id),
            GAMRestFilters.text_filter("status", self.status),
            GAMRestFilters.text_filter("buyerPermissionType", self.buyer_permission_type),
            GAMRestFilters.boolean_filter("auctionPriorityEnabled", self.auction_priority_enabled),
            GAMRestFilters.boolean_filter("blockOverrideEnabled", self.block_override_enabled),
            GAMRestFilters.date_filter("endTime", self.end_time),
            GAMRestFilters.date_filter("createTime", self.create_time),
            GAMRestFilters.date_filter("updateTime", self.update_time),
        ]


class PrivateAuctionDealClient:
    """Client for the `privateAuctionDeals` GAM REST resource.

    Read-only (`list_private_auction_deals`/`get_private_auction_deal`) —
    the underlying API also documents `create`/`patch`, but those aren't
    implemented since no resource client in this library performs writes.
    """

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "privateAuctionDeals"

    def list_private_auction_deals(
        self,
        private_auction_deal_id: int | list[int] | None = None,
        private_auction_id: int | list[int] | None = None,
        buyer_account_id: int | list[int] | None = None,
        external_deal_id: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        status: PrivateAuctionDealStatus | list[PrivateAuctionDealStatus] | None = None,
        buyer_permission_type: PrivateAuctionDealBuyerPermissionType
        | list[PrivateAuctionDealBuyerPermissionType]
        | None = None,
        auction_priority_enabled: bool | None = None,
        block_override_enabled: bool | None = None,
        end_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        create_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        update_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        page_size: int = 1000,
    ):
        """List `privateAuctionDeals`, paging through every result via `HTTPClient.fetch_all`.

        `private_auction_deal_id` resolves to `privateAuctionDeals/{id}`
        path(s); `private_auction_id` resolves to `privateAuctions/{id}`
        path(s); `buyer_account_id` resolves to `programmaticBuyers/{id}`
        path(s) — all via `utils.gam_obj_id_path` before filtering. Fields
        left as `None` are omitted from the filter.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_obj_type)

        deal_id_str = gam_obj_id_path(
            private_auction_deal_id, self.network_code, self._gam_obj_type
        )
        private_auction_id_str = gam_obj_id_path(
            private_auction_id, self.network_code, "privateAuctions"
        )
        buyer_account_id_str = gam_obj_id_path(
            buyer_account_id, self.network_code, "programmaticBuyers"
        )

        filter_str = PrivateAuctionDealFilter(
            name=deal_id_str,
            private_auction=private_auction_id_str,
            buyer_account=buyer_account_id_str,
            external_deal_id=external_deal_id,
            status=status,
            buyer_permission_type=buyer_permission_type,
            auction_priority_enabled=auction_priority_enabled,
            block_override_enabled=block_override_enabled,
            end_time=end_time,
            create_time=create_time,
            update_time=update_time,
        ).get_filter_string()

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get_private_auction_deal(self, private_auction_deal_id: int):
        """Fetch a single `privateAuctionDeal` by numeric id."""
        endpoint = gam_obj_id_path(private_auction_deal_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
