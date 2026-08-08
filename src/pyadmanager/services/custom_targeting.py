"""Filter builder for the customTargetingKeys and customTargetingValues GAM REST endpoints.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.customTargetingKeys
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.customTargetingValues
"""

from typing import Literal

from ..filters import GAMRestFilters, get_filter_string
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

CustomTargetingKeyType = Literal["PREDEFINED", "FREEFORM"]
CustomTargetingKeyStatus = Literal["ACTIVE", "INACTIVE"]
CustomTargetingKeyReportableType = Literal["OFF", "ON", "CUSTOM_DIMENSION"]

CustomTargetingValueStatus = CustomTargetingKeyStatus
CustomTargetingValueMatchType = Literal[
    "EXACT", "BROAD", "PREFIX", "BROAD_PREFIX", "SUFFIX", "CONTAINS"
]


class CustomTargetingClient:
    """Client for the `customTargetingKeys`/`customTargetingValues` GAM REST resources.

    Keys and values share one client (rather than two, mirroring
    `LineItemClient`/`ReportClient`) since a value always belongs to a key
    and the two are almost always fetched together in practice.
    """

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_key_obj_type = "customTargetingKeys"
        self._gam_value_obj_type = "customTargetingValues"

    def list_keys(
        self,
        key_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        ad_tag_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        reportable_type: CustomTargetingKeyReportableType
        | list[CustomTargetingKeyReportableType]
        | None = None,
        status: CustomTargetingKeyStatus | list[CustomTargetingKeyStatus] | None = None,
        key_type: CustomTargetingKeyType | list[CustomTargetingKeyType] | None = None,
        page_size: int = 1000,
    ):
        """List `customTargetingKeys`, paging through every result via `HTTPClient.fetch_all`.

        `key_id` accepts a bare int (or list of ints) and is resolved to the
        full `customTargetingKeys/{id}` resource path(s) before filtering;
        all other fields are passed straight through to `CustomTargetingKeyFilter`.
        Fields left as `None` are omitted from the filter entirely.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_key_obj_type)

        key_id_str = gam_obj_id_path(key_id, self.network_code, self._gam_key_obj_type)

        filter_list = [
            GAMRestFilters.id_based_filter("name", key_id_str),
            GAMRestFilters.text_filter("displayName", display_name),
            GAMRestFilters.text_filter("adTagName", ad_tag_name),
            GAMRestFilters.text_filter("reportableType", reportable_type),
            GAMRestFilters.text_filter("status", status),
            GAMRestFilters.text_filter("type", key_type),
        ]

        filter_str = get_filter_string(filter_list)

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_key_obj_type, params)

    def get_key(self, key_id: int):
        """Fetch a single `customTargetingKey` by numeric id."""
        endpoint = gam_obj_id_path(key_id, self.network_code, self._gam_key_obj_type)
        return self.http_client.fetch(endpoint)

    def list_values(
        self,
        value_id: int | list[int] | None = None,
        custom_targeting_key_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        ad_tag_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        status: CustomTargetingValueStatus | list[CustomTargetingValueStatus] | None = None,
        match_type: CustomTargetingValueMatchType
        | list[CustomTargetingValueMatchType]
        | None = None,
        page_size: int = 1000,
    ):
        """List `customTargetingValues`, paging through every result via `HTTPClient.fetch_all`.

        `value_id` resolves to `customTargetingValues/{id}` path(s) and
        `custom_targeting_key_id` resolves to `customTargetingKeys/{id}`
        path(s) (both via `utils.gam_obj_id_path`) before filtering — pass
        `custom_targeting_key_id` to scope results to a specific key's values.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_value_obj_type)

        value_id_str = gam_obj_id_path(value_id, self.network_code, self._gam_value_obj_type)
        custom_targeting_key_id_str = gam_obj_id_path(
            custom_targeting_key_id, self.network_code, self._gam_key_obj_type
        )

        filter_list = [
            GAMRestFilters.id_based_filter("customTargetingKey", custom_targeting_key_id_str),
            GAMRestFilters.id_based_filter("name", value_id_str),
            GAMRestFilters.text_filter("displayName", display_name),
            GAMRestFilters.text_filter("adTagName", ad_tag_name),
            GAMRestFilters.text_filter("status", status),
            GAMRestFilters.text_filter("matchType", match_type),
        ]

        filter_str = get_filter_string(filter_list)

        params = {"pageSize": page_size, "filter": filter_str}
        return self.http_client.fetch_all(endpoint, self._gam_value_obj_type, params)

    def get_value(self, key_id: int):
        """Fetch a single `customTargetingValue` by numeric id.

        Note: despite the parameter name, this is a `customTargetingValue`
        id, not a `customTargetingKey` id — use `get_key` for the latter.
        """
        endpoint = gam_obj_id_path(key_id, self.network_code, self._gam_value_obj_type)
        return self.http_client.fetch(endpoint)
