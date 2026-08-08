"""Filter builder for the lineItems GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.lineItems
"""

from datetime import datetime
from typing import Literal

from ..filters import BaseRestFilter, GAMRestFilters
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


class LineItemFilter(BaseRestFilter):
    def __init__(
        self,
        name: str | list[str] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        order: str | list[str] | None = None,
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
    ):
        self.name = name
        self.display_name = display_name
        self.order = order
        self.order_display_name = order_display_name
        self.line_item_type = line_item_type
        self.priority = priority
        self.status = status
        self.archived = archived
        self.cost_type = cost_type
        self.delivery_rate_type = delivery_rate_type
        self.start_time = start_time
        self.end_time = end_time
        self.environment_type = environment_type
        self.external_line_item_id = external_line_item_id
        self.missing_creatives = missing_creatives
        self.update_source = update_source
        self.create_time = create_time
        self.update_time = update_time
        self.web_property_code = web_property_code

    def _build_filter_list(self) -> list[str]:
        return [
            GAMRestFilters.id_based_filter("name", self.name),
            GAMRestFilters.text_filter("displayName", self.display_name),
            GAMRestFilters.id_based_filter("order", self.order),
            GAMRestFilters.text_filter("orderDisplayName", self.order_display_name),
            GAMRestFilters.text_filter("lineItemType", self.line_item_type),
            GAMRestFilters.number_filter("priority", self.priority),
            GAMRestFilters.text_filter("status", self.status),
            GAMRestFilters.boolean_filter("archived", self.archived),
            GAMRestFilters.text_filter("costType", self.cost_type),
            GAMRestFilters.text_filter("deliveryRateType", self.delivery_rate_type),
            GAMRestFilters.date_filter("startTime", self.start_time),
            GAMRestFilters.date_filter("endTime", self.end_time),
            GAMRestFilters.text_filter("environmentType", self.environment_type),
            GAMRestFilters.text_filter("externalLineItemId", self.external_line_item_id),
            GAMRestFilters.boolean_filter("missingCreatives", self.missing_creatives),
            GAMRestFilters.text_filter("updateSource", self.update_source),
            GAMRestFilters.date_filter("createTime", self.create_time),
            GAMRestFilters.date_filter("updateTime", self.update_time),
            GAMRestFilters.text_filter("webPropertyCode", self.web_property_code),
        ]


class LineItemClient(BaseRestFilter):
    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client

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
        gam_obj_type = "lineItems"
        endpoint = gam_obj_path(self.network_code, gam_obj_type)

        line_item_id_str = gam_obj_id_path(line_item_id, self.network_code, gam_obj_type)
        order_id_str = gam_obj_id_path(order_id, self.network_code, "orders")

        filter_str = LineItemFilter(
            name=line_item_id_str,
            display_name=display_name,
            order=order_id_str,
            order_display_name=order_display_name,
            line_item_type=line_item_type,
            priority=priority,
            status=status,
            archived=archived,
            cost_type=cost_type,
            delivery_rate_type=delivery_rate_type,
            start_time=start_time,
            end_time=end_time,
            environment_type=environment_type,
            external_line_item_id=external_line_item_id,
            missing_creatives=missing_creatives,
            update_source=update_source,
            create_time=create_time,
            update_time=update_time,
            web_property_code=web_property_code,
        ).get_filter_string()

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, gam_obj_type, params)

    def get_line_item(self, line_item_id: int):
        gam_obj_type = "lineItems"
        endpoint = gam_obj_id_path(line_item_id, self.network_code, gam_obj_type)
        return self.http_client.fetch(endpoint)
