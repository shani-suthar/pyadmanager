"""Filter builder for the PrivateAuctions GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.privateAuctions
"""

from datetime import datetime

from ..filters import GAMRestFilters, get_filter_string
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path


class PrivateAuctionClient:
    """Client for the `privateAuctions` GAM REST resource.

    Read-only (`list`/`get`) — the
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

    def list(
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

        filter_list = [
            GAMRestFilters.id_based_filter("name", private_auction_id_str),
            GAMRestFilters.text_filter("displayName", display_name),
            GAMRestFilters.text_filter("description", description),
            GAMRestFilters.boolean_filter("archived", archived),
            GAMRestFilters.date_filter("createTime", create_time),
            GAMRestFilters.date_filter("updateTime", update_time),
        ]

        filter_str = get_filter_string(filter_list)

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get(self, private_auction_id: int):
        """Fetch a single `privateAuction` by numeric id."""
        endpoint = gam_obj_id_path(private_auction_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
