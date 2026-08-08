from datetime import UTC, datetime
from unittest.mock import Mock

from pyadmanager.http_client import HTTPClient
from pyadmanager.services.line_item import LineItemClient, LineItemFilter

NETWORK_CODE = "123"


def fake_http_client() -> Mock:
    return Mock(spec=HTTPClient)


class TestLineItemFilter:
    def test_order_uses_id_based_filter(self):
        filter_str = LineItemFilter(order="networks/123/orders/9").get_filter_string()

        assert filter_str == 'order = "networks/123/orders/9"'

    def test_priority_is_bare_number(self):
        filter_str = LineItemFilter(priority=[1, 2]).get_filter_string()

        assert filter_str == "(priority = 1 OR priority = 2)"

    def test_archived_and_missing_creatives_are_bare_booleans(self):
        filter_str = LineItemFilter(archived=True, missing_creatives=False).get_filter_string()

        assert filter_str == "archived = true AND missingCreatives = false"

    def test_status_and_cost_type_are_quoted(self):
        filter_str = LineItemFilter(status="DRAFT", cost_type="CPM").get_filter_string()

        assert filter_str == 'status = "DRAFT" AND costType = "CPM"'

    def test_update_time_is_quoted_rfc3339(self):
        filter_str = LineItemFilter(
            update_time=(datetime(2025, 1, 1, tzinfo=UTC), "GT_EQ")
        ).get_filter_string()

        assert filter_str == 'updateTime >= "2025-01-01T00:00:00+00:00"'

    def test_no_fields_returns_none(self):
        assert LineItemFilter().get_filter_string() is None


class TestListLineItems:
    def test_builds_endpoint_and_filter(self):
        http_client = fake_http_client()
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(status="DRAFT", archived=True)

        http_client.fetch_all.assert_called_once_with(
            "networks/123/lineItems",
            "lineItems",
            {
                "pageSize": 1000,
                "filter": 'status = "DRAFT" AND archived = true',
            },
        )

    def test_line_item_id_is_resolved_to_full_path(self):
        http_client = fake_http_client()
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(line_item_id=456)

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/lineItems/456"'

    def test_order_id_is_resolved_against_orders_resource(self):
        http_client = fake_http_client()
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(order_id=9)

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'order = "networks/123/orders/9"'

    def test_no_filters_passes_none(self):
        http_client = fake_http_client()
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items()

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self):
        http_client = fake_http_client()
        http_client.fetch_all.return_value = [{"name": "li1"}]
        client = LineItemClient(NETWORK_CODE, http_client)

        assert client.list_line_items() == [{"name": "li1"}]


class TestGetLineItem:
    def test_fetches_by_id_path(self):
        http_client = fake_http_client()
        client = LineItemClient(NETWORK_CODE, http_client)

        client.get_line_item(456)

        http_client.fetch.assert_called_once_with("networks/123/lineItems/456")
