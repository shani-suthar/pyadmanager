"""Filter builder for the PrivateAuctionDeals GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.privateAuctionDeals
"""

from datetime import datetime
from typing import Literal

from ..filters import GAMRestFilters, get_filter_string
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

PrivateAuctionDealStatus = Literal[
    "PENDING", "ACTIVE", "CANCELED", "SELLER_PAUSED", "BUYER_PAUSED", "COMPLETED"
]
PrivateAuctionDealBuyerPermissionType = Literal["NEGOTIATOR_ONLY", "BIDDER"]


class PrivateAuctionDealClient:
    """Client for the `privateAuctionDeals` GAM REST resource.

    Read-only (`list`/`get`) —
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

    def list(
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

        filter_list = [
            GAMRestFilters.id_based_filter("name", deal_id_str),
            GAMRestFilters.id_based_filter("privateAuctionId", private_auction_id_str),
            GAMRestFilters.id_based_filter("buyerAccountId", buyer_account_id_str),
            GAMRestFilters.text_filter("externalDealId", external_deal_id),
            GAMRestFilters.text_filter("status", status),
            GAMRestFilters.text_filter("buyerPermissionType", buyer_permission_type),
            GAMRestFilters.boolean_filter("auctionPriorityEnabled", auction_priority_enabled),
            GAMRestFilters.boolean_filter("blockOverrideEnabled", block_override_enabled),
            GAMRestFilters.date_filter("endTime", end_time),
            GAMRestFilters.date_filter("createTime", create_time),
            GAMRestFilters.date_filter("updateTime", update_time),
        ]

        filter_str = get_filter_string(filter_list)

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get(self, private_auction_deal_id: int):
        """Fetch a single `privateAuctionDeal` by numeric id."""
        endpoint = gam_obj_id_path(private_auction_deal_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
