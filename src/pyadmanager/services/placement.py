"""Filter builder for the Placements GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.placements
"""

from datetime import datetime
from typing import Literal

from ..filters import BaseRestFilter, GAMRestFilters
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

PlacementStatus = Literal["PLACEMENT_STATUS_UNSPECIFIED", "ACTIVE", "INACTIVE", "ARCHIVED"]


class PlacementFilter(BaseRestFilter):
    """Filter for `PlacementClient.list_placements`.

    One field per `placements` REST filter field.
    """

    def __init__(
        self,
        name: str | list[str] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        description: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        placement_code: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        status: PlacementStatus | list[PlacementStatus] | None = None,
        update_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
    ):
        """Store filter field values; `name` is expected to already be a full resource path.

        `PlacementClient.list_placements` resolves a bare `placement_id` to
        `name` via `utils.gam_obj_id_path` before constructing this filter.
        `placement_code` is a plain string identifier (not a resource path),
        so it's routed through `text_filter` rather than `id_based_filter`.
        """
        self.name = name
        self.display_name = display_name
        self.description = description
        self.placement_code = placement_code
        self.status = status
        self.update_time = update_time

    def _build_filter_list(self) -> list[str]:
        return [
            GAMRestFilters.id_based_filter("name", self.name),
            GAMRestFilters.text_filter("displayName", self.display_name),
            GAMRestFilters.text_filter("description", self.description),
            GAMRestFilters.text_filter("placementCode", self.placement_code),
            GAMRestFilters.text_filter("status", self.status),
            GAMRestFilters.date_filter("updateTime", self.update_time),
        ]


class PlacementClient:
    """Client for the `placements` GAM REST resource.

    Read-only (`list_placements`/`get_placement`), matching every other
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

    def list_placements(
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

        filter_str = PlacementFilter(
            name=placement_id_str,
            display_name=display_name,
            description=description,
            placement_code=placement_code,
            status=status,
            update_time=update_time,
        ).get_filter_string()

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get_placement(self, placement_id: int):
        """Fetch a single `placement` by numeric id."""
        endpoint = gam_obj_id_path(placement_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
