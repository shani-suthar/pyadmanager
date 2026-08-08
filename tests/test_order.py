from datetime import UTC, datetime

from pyadmanager.services.order import OrderClient, OrderFilter

NETWORK_CODE = "123"


class TestOrderFilter:
    def test_name_uses_id_based_filter(self):
        filter_str = OrderFilter(name="networks/123/orders/456").get_filter_string()

        assert filter_str == 'name = "networks/123/orders/456"'

    def test_advertiser_and_agency_use_id_based_filter(self):
        filter_str = OrderFilter(
            advertiser="networks/123/companies/1",
            agency="networks/123/companies/2",
        ).get_filter_string()

        assert filter_str == (
            'advertiser = "networks/123/companies/1" AND agency = "networks/123/companies/2"'
        )

    def test_trafficker_and_salesperson_use_id_based_filter(self):
        filter_str = OrderFilter(
            trafficker="networks/123/users/1",
            salesperson="networks/123/users/2",
        ).get_filter_string()

        assert filter_str == (
            'trafficker = "networks/123/users/1" AND salesperson = "networks/123/users/2"'
        )

    def test_display_name_and_currency_code_are_quoted(self):
        filter_str = OrderFilter(
            display_name="Q1 Campaign", currency_code="USD"
        ).get_filter_string()

        assert filter_str == 'displayName = "Q1 Campaign" AND currencyCode = "USD"'

    def test_start_time_is_quoted_rfc3339(self):
        filter_str = OrderFilter(
            start_time=(datetime(2025, 1, 1, tzinfo=UTC), "GT_EQ")
        ).get_filter_string()

        assert filter_str == 'startTime >= "2025-01-01T00:00:00+00:00"'

    def test_status_is_quoted(self):
        filter_str = OrderFilter(status="APPROVED").get_filter_string()

        assert filter_str == 'status = "APPROVED"'

    def test_programmatic_and_archived_are_bare_booleans(self):
        filter_str = OrderFilter(programmatic=True, archived=False).get_filter_string()

        assert filter_str == "programmatic = true AND archived = false"

    def test_external_order_id_and_po_number_are_quoted(self):
        filter_str = OrderFilter(external_order_id="ext-1", po_number="PO-1").get_filter_string()

        assert filter_str == 'externalOrderId = "ext-1" AND poNumber = "PO-1"'

    def test_no_fields_returns_none(self):
        assert OrderFilter().get_filter_string() is None


class TestListOrders:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list_orders(display_name="Q1 Campaign", status="APPROVED")

        fake_http_client.fetch_all.assert_called_once_with(
            "networks/123/orders",
            "orders",
            {
                "pageSize": 1000,
                "filter": 'displayName = "Q1 Campaign" AND status = "APPROVED"',
            },
        )

    def test_order_id_is_resolved_to_full_path(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list_orders(order_id=456)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/orders/456"'

    def test_advertiser_id_is_resolved_against_companies_resource(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list_orders(advertiser_id=9)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'advertiser = "networks/123/companies/9"'

    def test_agency_id_is_resolved_against_companies_resource(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list_orders(agency_id=9)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'agency = "networks/123/companies/9"'

    def test_trafficker_id_is_resolved_against_users_resource(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list_orders(trafficker_id=9)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'trafficker = "networks/123/users/9"'

    def test_salesperson_id_is_resolved_against_users_resource(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list_orders(salesperson_id=9)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'salesperson = "networks/123/users/9"'

    def test_no_filters_passes_none(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list_orders()

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "o1"}]
        client = OrderClient(NETWORK_CODE, fake_http_client)

        assert client.list_orders() == [{"name": "o1"}]


class TestGetOrder:
    def test_fetches_by_id_path(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.get_order(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/orders/456")
