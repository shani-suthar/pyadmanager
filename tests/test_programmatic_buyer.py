from pyadmanager.services.programmatic_buyer import (
    ProgrammaticBuyerClient,
    ProgrammaticBuyerFilter,
)

NETWORK_CODE = "123"


class TestProgrammaticBuyerFilter:
    def test_name_uses_id_based_filter(self):
        filter_str = ProgrammaticBuyerFilter(
            name="networks/123/programmaticBuyers/456"
        ).get_filter_string()

        assert filter_str == 'name = "networks/123/programmaticBuyers/456"'

    def test_parent_account_id_uses_id_based_filter(self):
        filter_str = ProgrammaticBuyerFilter(
            parent_account_id="networks/123/programmaticBuyers/1"
        ).get_filter_string()

        assert filter_str == 'parentAccountId = "networks/123/programmaticBuyers/1"'

    def test_display_name_and_partner_client_id_are_quoted(self):
        filter_str = ProgrammaticBuyerFilter(
            display_name="Acme DSP", partner_client_id="partner-1"
        ).get_filter_string()

        assert filter_str == 'displayName = "Acme DSP" AND partnerClientId = "partner-1"'

    def test_boolean_fields_are_bare(self):
        filter_str = ProgrammaticBuyerFilter(
            agency=True,
            preferred_deals_enabled=False,
            programmatic_guaranteed_enabled=True,
        ).get_filter_string()

        assert filter_str == (
            "agency = true AND preferredDealsEnabled = false "
            "AND programmaticGuaranteedEnabled = true"
        )

    def test_no_fields_returns_none(self):
        assert ProgrammaticBuyerFilter().get_filter_string() is None


class TestListProgrammaticBuyers:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        client = ProgrammaticBuyerClient(NETWORK_CODE, fake_http_client)

        client.list_programmatic_buyers(display_name="Acme DSP", agency=True)

        fake_http_client.fetch_all.assert_called_once_with(
            "networks/123/programmaticBuyers",
            "programmaticBuyers",
            {
                "pageSize": 1000,
                "filter": 'displayName = "Acme DSP" AND agency = true',
            },
        )

    def test_buyer_account_id_is_resolved_to_full_path(self, fake_http_client):
        client = ProgrammaticBuyerClient(NETWORK_CODE, fake_http_client)

        client.list_programmatic_buyers(buyer_account_id=456)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/programmaticBuyers/456"'

    def test_parent_account_id_is_resolved_against_own_resource_type(self, fake_http_client):
        client = ProgrammaticBuyerClient(NETWORK_CODE, fake_http_client)

        client.list_programmatic_buyers(parent_account_id=1)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'parentAccountId = "networks/123/programmaticBuyers/1"'

    def test_no_filters_passes_none(self, fake_http_client):
        client = ProgrammaticBuyerClient(NETWORK_CODE, fake_http_client)

        client.list_programmatic_buyers()

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "b1"}]
        client = ProgrammaticBuyerClient(NETWORK_CODE, fake_http_client)

        assert client.list_programmatic_buyers() == [{"name": "b1"}]


class TestGetProgrammaticBuyer:
    def test_fetches_by_id_path(self, fake_http_client):
        client = ProgrammaticBuyerClient(NETWORK_CODE, fake_http_client)

        client.get_programmatic_buyer(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/programmaticBuyers/456")
