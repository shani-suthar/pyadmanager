"""Filter builder for the Orders GAM REST endpoint.

Reference:
    https://developers.google.com/ad-manager/api/beta/reference/rest/v1/networks.orders
"""

from datetime import datetime
from typing import Literal

from ..filters import BaseRestFilter, GAMRestFilters
from ..http_client import HTTPClient
from ..utils import gam_obj_id_path, gam_obj_path

OrderStatus = Literal[
    "DRAFT",
    "PENDING_APPROVAL",
    "APPROVED",
    "DISAPPROVED",
    "PAUSED",
    "CANCELED",
    "DELETED",
]


class OrderFilter(BaseRestFilter):
    """Filter for `OrderClient.list_orders`.

    One field per `orders` REST filter field.
    """

    def __init__(
        self,
        name: str | list[str] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        advertiser: str | list[str] | None = None,
        agency: str | list[str] | None = None,
        trafficker: str | list[str] | None = None,
        salesperson: str | list[str] | None = None,
        currency_code: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        start_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        end_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        status: OrderStatus | list[OrderStatus] | None = None,
        programmatic: bool | None = None,
        archived: bool | None = None,
        external_order_id: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        po_number: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
    ):
        """Store filter field values.

        Id-reference fields are expected to already be full resource paths —
        `OrderClient.list_orders` resolves bare `order_id`/`advertiser_id`/
        `agency_id`/`trafficker_id`/`salesperson_id` ints to `name`/
        `advertiser`/`agency`/`trafficker`/`salesperson` via
        `utils.gam_obj_id_path` before constructing this filter.
        """
        self.name = name
        self.display_name = display_name
        self.advertiser = advertiser
        self.agency = agency
        self.trafficker = trafficker
        self.salesperson = salesperson
        self.currency_code = currency_code
        self.start_time = start_time
        self.end_time = end_time
        self.status = status
        self.programmatic = programmatic
        self.archived = archived
        self.external_order_id = external_order_id
        self.po_number = po_number

    def _build_filter_list(self) -> list[str]:
        return [
            GAMRestFilters.id_based_filter("name", self.name),
            GAMRestFilters.text_filter("displayName", self.display_name),
            GAMRestFilters.id_based_filter("advertiser", self.advertiser),
            GAMRestFilters.id_based_filter("agency", self.agency),
            GAMRestFilters.id_based_filter("trafficker", self.trafficker),
            GAMRestFilters.id_based_filter("salesperson", self.salesperson),
            GAMRestFilters.text_filter("currencyCode", self.currency_code),
            GAMRestFilters.date_filter("startTime", self.start_time),
            GAMRestFilters.date_filter("endTime", self.end_time),
            GAMRestFilters.text_filter("status", self.status),
            GAMRestFilters.boolean_filter("programmatic", self.programmatic),
            GAMRestFilters.boolean_filter("archived", self.archived),
            GAMRestFilters.text_filter("externalOrderId", self.external_order_id),
            GAMRestFilters.text_filter("poNumber", self.po_number),
        ]


class OrderClient:
    """Client for the `orders` GAM REST resource.

    Read-only (`list_orders`/`get_order`) — the underlying API also
    documents `batchApprove`, `batchCreate`, `batchUpdate`, and many other
    batch write operations, but those aren't implemented since no resource
    client in this library performs writes.
    """

    def __init__(
        self,
        network_code: str,
        http_client: HTTPClient,
    ):
        self.network_code = network_code
        self.http_client = http_client
        self._gam_obj_type = "orders"

    def list_orders(
        self,
        order_id: int | list[int] | None = None,
        display_name: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        advertiser_id: int | list[int] | None = None,
        agency_id: int | list[int] | None = None,
        trafficker_id: int | list[int] | None = None,
        salesperson_id: int | list[int] | None = None,
        currency_code: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        start_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        end_time: datetime | GAMRestFilters.Datetime_Filter_Type | None = None,
        status: OrderStatus | list[OrderStatus] | None = None,
        programmatic: bool | None = None,
        archived: bool | None = None,
        external_order_id: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        po_number: str | list[str] | GAMRestFilters.Text_Filter_Tuple | None = None,
        page_size: int = 1000,
    ):
        """List `orders`, paging through every result via `HTTPClient.fetch_all`.

        `order_id` resolves to `orders/{id}` path(s); `advertiser_id`/
        `agency_id` resolve to `companies/{id}` path(s); `trafficker_id`/
        `salesperson_id` resolve to `users/{id}` path(s) — all via
        `utils.gam_obj_id_path` before filtering. Fields left as `None` are
        omitted from the filter.
        """
        endpoint = gam_obj_path(self.network_code, self._gam_obj_type)

        order_id_str = gam_obj_id_path(order_id, self.network_code, self._gam_obj_type)
        advertiser_id_str = gam_obj_id_path(advertiser_id, self.network_code, "companies")
        agency_id_str = gam_obj_id_path(agency_id, self.network_code, "companies")
        trafficker_id_str = gam_obj_id_path(trafficker_id, self.network_code, "users")
        salesperson_id_str = gam_obj_id_path(salesperson_id, self.network_code, "users")

        filter_str = OrderFilter(
            name=order_id_str,
            display_name=display_name,
            advertiser=advertiser_id_str,
            agency=agency_id_str,
            trafficker=trafficker_id_str,
            salesperson=salesperson_id_str,
            currency_code=currency_code,
            start_time=start_time,
            end_time=end_time,
            status=status,
            programmatic=programmatic,
            archived=archived,
            external_order_id=external_order_id,
            po_number=po_number,
        ).get_filter_string()

        params = {"pageSize": page_size, "filter": filter_str}

        return self.http_client.fetch_all(endpoint, self._gam_obj_type, params)

    def get_order(self, order_id: int):
        """Fetch a single `order` by numeric id."""
        endpoint = gam_obj_id_path(order_id, self.network_code, self._gam_obj_type)
        return self.http_client.fetch(endpoint)
