"""Filter builder for the AdUnits GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.adUnits
"""

from datetime import datetime
from typing import Literal

from ..filters import GAMRestFilters, get_filter_string
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

AdUnitStatus = Literal["ACTIVE", "INACTIVE", "ARCHIVED"]


class AdUnitClient:
    """Client for the `adUnits` GAM REST resource.

    Read-only (`list`/`get`) — the underlying API also
    documents `create`, `patch`, and batch create/update/activate/
    deactivate/archive operations, but those aren't implemented since no
    resource client in this library performs writes.
    """

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "adUnits"

    def list(
        self,
        ad_unit_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        parent_ad_unit_id: int | list[int] | None = None,
        ad_unit_code: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        status: AdUnitStatus | list[AdUnitStatus] | None = None,
        explicitly_targeted: bool | None = None,
        has_children: bool | None = None,
        update_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        page_size: int = 1000,
    ):
        """List `adUnits`, paging through every result via `HTTPClient.fetch_all`.

        `ad_unit_id` resolves to `adUnits/{id}` path(s); `parent_ad_unit_id`
        resolves the same way (an ad unit's parent is itself an ad unit) —
        both via `utils.gam_obj_id_path` before filtering. Fields left as
        `None` are omitted from the filter.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_obj_type)

        ad_unit_id_str = gam_obj_id_path(ad_unit_id, self.network_code, self._gam_obj_type)
        parent_ad_unit_id_str = gam_obj_id_path(
            parent_ad_unit_id, self.network_code, self._gam_obj_type
        )

        filter_list = [
            GAMRestFilters.id_based_filter("name", ad_unit_id_str),
            GAMRestFilters.text_filter("displayName", display_name),
            GAMRestFilters.id_based_filter("parentAdUnit", parent_ad_unit_id_str),
            GAMRestFilters.text_filter("adUnitCode", ad_unit_code),
            GAMRestFilters.text_filter("status", status),
            GAMRestFilters.boolean_filter("explicitlyTargeted", explicitly_targeted),
            GAMRestFilters.boolean_filter("hasChildren", has_children),
            GAMRestFilters.date_filter("updateTime", update_time),
        ]

        filter_str = get_filter_string(filter_list)

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get(self, ad_unit_id: int):
        """Fetch a single `adUnit` by numeric id."""
        endpoint = gam_obj_id_path(ad_unit_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
