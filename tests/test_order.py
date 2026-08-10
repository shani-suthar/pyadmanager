from datetime import UTC, datetime

from pyadmanager.services.order import OrderClient

NETWORK_CODE = "123"


class TestListOrders:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(display_name="Q1 Campaign", status="APPROVED")

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

        client.list(order_id=456)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/orders/456"'

    def test_advertiser_id_is_resolved_against_companies_resource(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(advertiser_id=9)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'advertiser = "networks/123/companies/9"'

    def test_agency_id_is_resolved_against_companies_resource(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(agency_id=9)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'agency = "networks/123/companies/9"'

    def test_trafficker_id_is_resolved_against_users_resource(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(trafficker_id=9)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'trafficker = "networks/123/users/9"'

    def test_salesperson_id_is_resolved_against_users_resource(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(salesperson_id=9)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'salesperson = "networks/123/users/9"'

    def test_display_name_and_currency_code_are_quoted(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(display_name="Q1 Campaign", currency_code="USD")

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'displayName = "Q1 Campaign" AND currencyCode = "USD"'

    def test_start_time_is_quoted_rfc3339(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(start_time=(datetime(2025, 1, 1, tzinfo=UTC), "GT_EQ"))

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'startTime >= "2025-01-01T00:00:00+00:00"'

    def test_programmatic_and_archived_are_bare_booleans(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(programmatic=True, archived=False)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == "programmatic = true AND archived = false"

    def test_external_order_id_and_po_number_are_quoted(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(external_order_id="ext-1", po_number="PO-1")

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'externalOrderId = "ext-1" AND poNumber = "PO-1"'

    def test_order_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(order_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(name = "networks/123/orders/1" OR name = "networks/123/orders/2")'
        )

    def test_advertiser_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(advertiser_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(advertiser = "networks/123/companies/1" OR advertiser = "networks/123/companies/2")'
        )

    def test_trafficker_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(trafficker_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(trafficker = "networks/123/users/1" OR trafficker = "networks/123/users/2")'
        )

    def test_all_fields_produce_expected_filter_str_in_order(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(
            order_id=456,
            display_name="Q1 Campaign",
            advertiser_id=1,
            agency_id=2,
            trafficker_id=3,
            salesperson_id=4,
            currency_code="USD",
            start_time=datetime(2025, 1, 1, tzinfo=UTC),
            end_time=datetime(2025, 2, 1, tzinfo=UTC),
            status="APPROVED",
            programmatic=True,
            archived=False,
            external_order_id="ext-1",
            po_number="PO-1",
        )

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'name = "networks/123/orders/456" AND displayName = "Q1 Campaign" '
            'AND advertiser = "networks/123/companies/1" AND agency = "networks/123/companies/2" '
            'AND trafficker = "networks/123/users/3" AND salesperson = "networks/123/users/4" '
            'AND currencyCode = "USD" AND startTime = "2025-01-01T00:00:00+00:00" '
            'AND endTime = "2025-02-01T00:00:00+00:00" AND status = "APPROVED" '
            'AND programmatic = true AND archived = false AND externalOrderId = "ext-1" '
            'AND poNumber = "PO-1"'
        )

    def test_partial_fields_are_joined_in_field_order_skipping_unset(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list(trafficker_id=9, status="APPROVED", archived=False)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'trafficker = "networks/123/users/9" AND status = "APPROVED" AND archived = false'
        )

    def test_no_filters_passes_none(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.list()

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "o1"}]
        client = OrderClient(NETWORK_CODE, fake_http_client)

        assert client.list() == [{"name": "o1"}]


class TestGetOrder:
    def test_fetches_by_id_path(self, fake_http_client):
        client = OrderClient(NETWORK_CODE, fake_http_client)

        client.get(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/orders/456")
