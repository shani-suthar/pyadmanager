"""Filter builder for the Placements GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.placements
"""

from datetime import datetime
from typing import Literal

from ..filters import GAMRestFilters, get_filter_string
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

PlacementStatus = Literal["PLACEMENT_STATUS_UNSPECIFIED", "ACTIVE", "INACTIVE", "ARCHIVED"]


class PlacementClient:
    """Client for the `placements` GAM REST resource.

    Read-only (`list`/`get`), matching every other
    resource client here — the underlying API also documents `create`,
    `patch`, and batch activate/deactivate/archive operations, but those
    aren't implemented since no resource client in this library performs writes.
    """

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "placements"

    def list(
        self,
        placement_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        description: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        placement_code: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        status: PlacementStatus | list[PlacementStatus] | None = None,
        update_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        page_size: int = 1000,
    ):
        """List `placements`, paging through every result via `HTTPClient.fetch_all`.

        `placement_id` resolves to `placements/{id}` path(s) via
        `utils.gam_obj_id_path` before filtering; fields left as `None` are
        omitted from the filter.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_obj_type)

        placement_id_str = gam_obj_id_path(placement_id, self.network_code, self._gam_obj_type)

        filter_list = [
            GAMRestFilters.id_based_filter("name", placement_id_str),
            GAMRestFilters.text_filter("displayName", display_name),
            GAMRestFilters.text_filter("description", description),
            GAMRestFilters.text_filter("placementCode", placement_code),
            GAMRestFilters.text_filter("status", status),
            GAMRestFilters.date_filter("updateTime", update_time),
        ]

        filter_str = get_filter_string(filter_list)

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get(self, placement_id: int):
        """Fetch a single `placement` by numeric id."""
        endpoint = gam_obj_id_path(placement_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
