"""Filter builder for the customTargetingKeys and customTargetingValues GAM REST endpoints.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.customTargetingKeys
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.customTargetingValues
"""

from typing import Literal

from ..filters import BaseRestFilter, GAMRestFilters
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

CustomTargetingKeyType = Literal["PREDEFINED", "FREEFORM"]
CustomTargetingKeyStatus = Literal["ACTIVE", "INACTIVE"]
CustomTargetingKeyReportableType = Literal["OFF", "ON", "CUSTOM_DIMENSION"]

CustomTargetingValueStatus = CustomTargetingKeyStatus
CustomTargetingValueMatchType = Literal[
    "EXACT", "BROAD", "PREFIX", "BROAD_PREFIX", "SUFFIX", "CONTAINS"
]


class CustomTargetingKeyFilter(BaseRestFilter):
    def __init__(
        self,
        name: str | list[str] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        ad_tag_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        reportable_type: CustomTargetingKeyReportableType
        | list[CustomTargetingKeyReportableType]
        | None = None,
        status: CustomTargetingKeyStatus | list[CustomTargetingKeyStatus] | None = None,
        key_type: CustomTargetingKeyType | list[CustomTargetingKeyType] | None = None,
    ):
        self.name = name
        self.display_name = display_name
        self.ad_tag_name = ad_tag_name
        self.reportable_type = reportable_type
        self.status = status
        self.key_type = key_type

    def _build_filter_list(self) -> list[str]:
        return [
            GAMRestFilters.id_based_filter("name", self.name),
            GAMRestFilters.text_filter("displayName", self.display_name),
            GAMRestFilters.text_filter("adTagName", self.ad_tag_name),
            GAMRestFilters.text_filter("reportableType", self.reportable_type),
            GAMRestFilters.text_filter("status", self.status),
            GAMRestFilters.text_filter("type", self.key_type),
        ]


class CustomTargetingValueFilter(BaseRestFilter):
    def __init__(
        self,
        name: str | list[str] | None = None,
        custom_targeting_key: str | list[str] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        ad_tag_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        status: CustomTargetingValueStatus | list[CustomTargetingValueStatus] | None = None,
        match_type: CustomTargetingValueMatchType
        | list[CustomTargetingValueMatchType]
        | None = None,
    ):
        self.name = name
        self.custom_targeting_key = custom_targeting_key
        self.display_name = display_name
        self.ad_tag_name = ad_tag_name

        self.status = status
        self.match_type = match_type

    def _build_filter_list(self) -> list[str]:
        return [
            GAMRestFilters.id_based_filter("customTargetingKey", self.custom_targeting_key),
            GAMRestFilters.id_based_filter("name", self.name),
            GAMRestFilters.text_filter("displayName", self.display_name),
            GAMRestFilters.text_filter("adTagName", self.ad_tag_name),
            GAMRestFilters.text_filter("status", self.status),
            GAMRestFilters.text_filter("matchType", self.match_type),
        ]


class CustomTargetingClient(BaseRestFilter):
    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client

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
        gam_obj_type = "customTargetingKeys"
        endpoint = gam_obj_path(self.network_code, gam_obj_type)

        key_id_str = gam_obj_id_path(key_id, self.network_code, gam_obj_type)

        filter_str = CustomTargetingKeyFilter(
            name=key_id_str,
            display_name=display_name,
            ad_tag_name=ad_tag_name,
            reportable_type=reportable_type,
            status=status,
            key_type=key_type,
        ).get_filter_string()

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, gam_obj_type, params)

    def get_key(self, key_id: int):
        gam_obj_type = "customTargetingKeys"
        endpoint = gam_obj_id_path(key_id, self.network_code, gam_obj_type)
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
        gam_obj_type = "customTargetingValues"
        endpoint = gam_obj_path(self.network_code, gam_obj_type)

        value_id_str = gam_obj_id_path(value_id, self.network_code, gam_obj_type)
        custom_targeting_key_id_str = gam_obj_id_path(
            custom_targeting_key_id, self.network_code, "customTargetingKeys"
        )

        filter_str = CustomTargetingValueFilter(
            name=value_id_str,
            custom_targeting_key=custom_targeting_key_id_str,
            display_name=display_name,
            ad_tag_name=ad_tag_name,
            status=status,
            match_type=match_type,
        ).get_filter_string()

        params = {"pageSize": page_size, "filter": filter_str}
        return self.http_client.fetch_all(endpoint, gam_obj_type, params)

    def get_value(self, key_id: int):
        gam_obj_type = "customTargetingValues"
        endpoint = gam_obj_id_path(key_id, self.network_code, gam_obj_type)
        return self.http_client.fetch(endpoint)
