"""Filter builder for the lineItems GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.lineItems
"""

from datetime import datetime
from typing import Literal

from ..filters import GAMRestFilters, get_filter_string
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

# LineItemArchived = Literal[True, False]
LineItemType = Literal[
    "SPONSORSHIP",
    "STANDARD",
    "NETWORK",
    "BULK",
    "PRICE_PRIORITY",
    "HOUSE",
    "CLICK_TRACKING",
    "ADSENSE",
    "AD_EXCHANGE",
    "BUMPER",
    "PREFERRED_DEAL",
    "AUDIENCE_EXTENSION",
]
LineItemPriority = Literal[1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16]
LineItemComputedStatus = Literal[
    "CANCELED",
    "COMPLETED",
    "DELIVERING",
    "DELIVERY_EXTENDED",
    "DISAPPROVED",
    "DRAFT",
    "INACTIVE",
    "PAUSED",
    "PAUSED_INVENTORY_RELEASED",
    "PENDING_APPROVAL",
    "READY",
]
LineItemCostType = Literal["CPA", "CPC", "CPD", "CPM", "VCPM", "CPM_IN_TARGET", "CPF", "CPCV"]
LineItemDeliveryRateType = Literal["AS_FAST_AS_POSSIBLE", "EVENLY", "FRONTLOADED"]
LineItemEnvironmentType = Literal["BROWSER", "VIDEO_PLAYER"]


class LineItemClient:
    """Client for the `lineItems` GAM REST resource."""

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "lineItems"

    def list_line_items(
        self,
        line_item_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        order_id: int | list[int] | None = None,
        order_display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        line_item_type: LineItemType | list[LineItemType] | None = None,
        priority: LineItemPriority | list[LineItemPriority] | None = None,
        status: LineItemComputedStatus | list[LineItemComputedStatus] | None = None,
        archived: bool | None = None,
        cost_type: LineItemCostType | list[LineItemCostType] | None = None,
        delivery_rate_type: LineItemDeliveryRateType | list[LineItemDeliveryRateType] | None = None,
        start_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        end_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        environment_type: LineItemEnvironmentType | list[LineItemEnvironmentType] | None = None,
        external_line_item_id: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        missing_creatives: bool | None = None,
        update_source: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        create_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        update_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        web_property_code: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        page_size: int = 1000,
    ):
        """List `lineItems`, paging through every result via `HTTPClient.fetch_all`.

        `line_item_id` resolves to `lineItems/{id}` path(s) and `order_id`
        resolves to `orders/{id}` path(s) (both via `utils.gam_obj_id_path`)
        before filtering — pass `order_id` to scope results to a specific
        order's line items. Fields left as `None` are omitted from the filter.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_obj_type)

        line_item_id_str = gam_obj_id_path(line_item_id, self.network_code, self._gam_obj_type)
        order_id_str = gam_obj_id_path(order_id, self.network_code, "orders")

        filter_list = [
            GAMRestFilters.id_based_filter("name", line_item_id_str),
            GAMRestFilters.text_filter("displayName", display_name),
            GAMRestFilters.id_based_filter("order", order_id_str),
            GAMRestFilters.text_filter("orderDisplayName", order_display_name),
            GAMRestFilters.text_filter("lineItemType", line_item_type),
            GAMRestFilters.number_filter("priority", priority),
            GAMRestFilters.text_filter("status", status),
            GAMRestFilters.boolean_filter("archived", archived),
            GAMRestFilters.text_filter("costType", cost_type),
            GAMRestFilters.text_filter("deliveryRateType", delivery_rate_type),
            GAMRestFilters.date_filter("startTime", start_time),
            GAMRestFilters.date_filter("endTime", end_time),
            GAMRestFilters.text_filter("environmentType", environment_type),
            GAMRestFilters.text_filter("externalLineItemId", external_line_item_id),
            GAMRestFilters.boolean_filter("missingCreatives", missing_creatives),
            GAMRestFilters.text_filter("updateSource", update_source),
            GAMRestFilters.date_filter("createTime", create_time),
            GAMRestFilters.date_filter("updateTime", update_time),
            GAMRestFilters.text_filter("webPropertyCode", web_property_code),
        ]

        filter_str = get_filter_string(filter_list)

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get_line_item(self, line_item_id: int):
        """Fetch a single `lineItem` by numeric id."""
        endpoint = gam_obj_id_path(line_item_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
