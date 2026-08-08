"""Filter builder for the PrivateAuctions GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.privateAuctions
"""

from datetime import datetime

from ..filters import BaseRestFilter, GAMRestFilters
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path


class PrivateAuctionFilter(BaseRestFilter):
    """Filter for `PrivateAuctionClient.list_private_auctions`.

    One field per `privateAuctions` REST filter field.
    """

    def __init__(
        self,
        name: str | list[str] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        description: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        archived: bool | None = None,
        create_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        update_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
    ):
        """Store filter field values; `name` is expected to already be a full resource path.

        `PrivateAuctionClient.list_private_auctions` resolves a bare
        `private_auction_id` to `name` via `utils.gam_obj_id_path` before
        constructing this filter.
        """
        self.name = name
        self.display_name = display_name
        self.description = description
        self.archived = archived
        self.create_time = create_time
        self.update_time = update_time

    def _build_filter_list(self) -> list[str]:
        return [
            GAMRestFilters.id_based_filter("name", self.name),
            GAMRestFilters.text_filter("displayName", self.display_name),
            GAMRestFilters.text_filter("description", self.description),
            GAMRestFilters.boolean_filter("archived", self.archived),
            GAMRestFilters.date_filter("createTime", self.create_time),
            GAMRestFilters.date_filter("updateTime", self.update_time),
        ]


class PrivateAuctionClient:
    """Client for the `privateAuctions` GAM REST resource.

    Read-only (`list_private_auctions`/`get_private_auction`) — the
    underlying API also documents `create`/`patch`, but those aren't
    implemented since no resource client in this library performs writes.
    """

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "privateAuctions"

    def list_private_auctions(
        self,
        private_auction_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        description: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        archived: bool | None = None,
        create_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        update_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        page_size: int = 1000,
    ):
        """List `privateAuctions`, paging through every result via `HTTPClient.fetch_all`.

        `private_auction_id` resolves to `privateAuctions/{id}` path(s) via
        `utils.gam_obj_id_path` before filtering; fields left as `None` are
        omitted from the filter.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_obj_type)

        private_auction_id_str = gam_obj_id_path(
            private_auction_id, self.network_code, self._gam_obj_type
        )

        filter_str = PrivateAuctionFilter(
            name=private_auction_id_str,
            display_name=display_name,
            description=description,
            archived=archived,
            create_time=create_time,
            update_time=update_time,
        ).get_filter_string()

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get_private_auction(self, private_auction_id: int):
        """Fetch a single `privateAuction` by numeric id."""
        endpoint = gam_obj_id_path(private_auction_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
