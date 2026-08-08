from datetime import UTC, datetime

from pyadmanager.services.line_item import LineItemClient

NETWORK_CODE = "123"


class TestListLineItems:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        http_client = fake_http_client
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

    def test_line_item_id_is_resolved_to_full_path(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(line_item_id=456)

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/lineItems/456"'

    def test_order_id_is_resolved_against_orders_resource(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(order_id=9)

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'order = "networks/123/orders/9"'

    def test_line_item_id_list_is_resolved_to_or_clause(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(line_item_id=[1, 2])

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(name = "networks/123/lineItems/1" OR name = "networks/123/lineItems/2")'
        )

    def test_order_id_list_is_resolved_to_or_clause(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(order_id=[1, 2])

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(order = "networks/123/orders/1" OR order = "networks/123/orders/2")'
        )

    def test_all_fields_produce_expected_filter_str_in_order(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(
            line_item_id=100,
            display_name="Homepage",
            order_id=9,
            order_display_name="Q1 Order",
            line_item_type="STANDARD",
            priority=6,
            status="DRAFT",
            archived=True,
            cost_type="CPM",
            delivery_rate_type="EVENLY",
            start_time=datetime(2025, 1, 1, tzinfo=UTC),
            end_time=datetime(2025, 2, 1, tzinfo=UTC),
            environment_type="BROWSER",
            external_line_item_id="ext-1",
            missing_creatives=False,
            update_source="API",
            create_time=datetime(2024, 12, 1, tzinfo=UTC),
            update_time=datetime(2025, 3, 1, tzinfo=UTC),
            web_property_code="WP1",
        )

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'name = "networks/123/lineItems/100" AND displayName = "Homepage" '
            'AND order = "networks/123/orders/9" AND orderDisplayName = "Q1 Order" '
            'AND lineItemType = "STANDARD" AND priority = 6 AND status = "DRAFT" '
            'AND archived = true AND costType = "CPM" AND deliveryRateType = "EVENLY" '
            'AND startTime = "2025-01-01T00:00:00+00:00" '
            'AND endTime = "2025-02-01T00:00:00+00:00" '
            'AND environmentType = "BROWSER" AND externalLineItemId = "ext-1" '
            'AND missingCreatives = false AND updateSource = "API" '
            'AND createTime = "2024-12-01T00:00:00+00:00" '
            'AND updateTime = "2025-03-01T00:00:00+00:00" AND webPropertyCode = "WP1"'
        )

    def test_partial_fields_are_joined_in_field_order_skipping_unset(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(order_id=9, cost_type="CPM", missing_creatives=True)

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'order = "networks/123/orders/9" AND costType = "CPM" AND missingCreatives = true'
        )

    def test_priority_list_is_resolved_to_bare_or_clause(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(priority=[1, 2])

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == "(priority = 1 OR priority = 2)"

    def test_archived_and_missing_creatives_are_bare_booleans(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(archived=True, missing_creatives=False)

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == "archived = true AND missingCreatives = false"

    def test_display_name_contains_renders_wildcard_both_sides(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(display_name=("Q3", "CONTAINS"))

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'displayName = "*Q3*"'

    def test_display_name_startwith_renders_wildcard_suffix(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(display_name=("Q3", "STARTWITH"))

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'displayName = "Q3*"'

    def test_display_name_endwith_renders_wildcard_prefix(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(display_name=("Q3", "ENDWITH"))

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'displayName = "*Q3"'

    def test_status_and_cost_type_are_quoted(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(status="DRAFT", cost_type="CPM")

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'status = "DRAFT" AND costType = "CPM"'

    def test_update_time_is_quoted_rfc3339(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items(update_time=(datetime(2025, 1, 1, tzinfo=UTC), "GT_EQ"))

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'updateTime >= "2025-01-01T00:00:00+00:00"'

    def test_no_filters_passes_none(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.list_line_items()

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        http_client = fake_http_client
        http_client.fetch_all.return_value = [{"name": "li1"}]
        client = LineItemClient(NETWORK_CODE, http_client)

        assert client.list_line_items() == [{"name": "li1"}]


class TestGetLineItem:
    def test_fetches_by_id_path(self, fake_http_client):
        http_client = fake_http_client
        client = LineItemClient(NETWORK_CODE, http_client)

        client.get_line_item(456)

        http_client.fetch.assert_called_once_with("networks/123/lineItems/456")
