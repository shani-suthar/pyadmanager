"""Filter builder for the Roles GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.roles
"""

from typing import Literal

from ..filters import BaseRestFilter, GAMRestFilters
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

RoleStatus = Literal["ROLE_STATUS_UNSPECIFIED", "ACTIVE", "INACTIVE"]


class RoleFilter(BaseRestFilter):
    """Filter for `RoleClient.list_roles` — one field per `roles` REST filter field."""

    def __init__(
        self,
        name: str | list[str] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        status: RoleStatus | list[RoleStatus] | None = None,
        built_in: bool | None = None,
    ):
        """Store filter field values; `name` is expected to already be a full resource path.

        `RoleClient.list_roles` resolves a bare `role_id` to `name` via
        `utils.gam_obj_id_path` before constructing this filter.
        """
        self.name = name
        self.display_name = display_name
        self.status = status
        self.built_in = built_in

    def _build_filter_list(self) -> list[str]:
        return [
            GAMRestFilters.id_based_filter("name", self.name),
            GAMRestFilters.text_filter("displayName", self.display_name),
            GAMRestFilters.text_filter("status", self.status),
            GAMRestFilters.boolean_filter("builtIn", self.built_in),
        ]


class RoleClient:
    """Client for the `roles` GAM REST resource."""

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "roles"

    def list_roles(
        self,
        role_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        status: RoleStatus | list[RoleStatus] | None = None,
        built_in: bool | None = None,
        page_size: int = 1000,
    ):
        """List `roles`, paging through every result via `HTTPClient.fetch_all`.

        `role_id` resolves to `roles/{id}` path(s) via `utils.gam_obj_id_path`
        before filtering; fields left as `None` are omitted from the filter.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_obj_type)

        role_id_str = gam_obj_id_path(role_id, self.network_code, self._gam_obj_type)

        filter_str = RoleFilter(
            name=role_id_str,
            display_name=display_name,
            status=status,
            built_in=built_in,
        ).get_filter_string()

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get_role(self, role_id: int):
        """Fetch a single `role` by numeric id."""
        endpoint = gam_obj_id_path(role_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
