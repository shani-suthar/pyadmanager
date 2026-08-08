from datetime import UTC, datetime

from pyadmanager.services.ad_unit import AdUnitClient

NETWORK_CODE = "123"


class TestListAdUnits:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units(display_name="Homepage", status="ACTIVE")

        fake_http_client.fetch_all.assert_called_once_with(
            "networks/123/adUnits",
            "adUnits",
            {
                "pageSize": 1000,
                "filter": 'displayName = "Homepage" AND status = "ACTIVE"',
            },
        )

    def test_ad_unit_id_is_resolved_to_full_path(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units(ad_unit_id=456)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/adUnits/456"'

    def test_parent_ad_unit_id_is_resolved_against_ad_units_resource(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units(parent_ad_unit_id=1)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'parentAdUnit = "networks/123/adUnits/1"'

    def test_display_name_and_ad_unit_code_are_quoted(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units(display_name="Homepage", ad_unit_code="HP1")

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'displayName = "Homepage" AND adUnitCode = "HP1"'

    def test_explicitly_targeted_and_has_children_are_bare_booleans(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units(explicitly_targeted=True, has_children=False)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == "explicitlyTargeted = true AND hasChildren = false"

    def test_update_time_is_quoted_rfc3339(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units(update_time=(datetime(2025, 1, 1, tzinfo=UTC), "GT_EQ"))

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'updateTime >= "2025-01-01T00:00:00+00:00"'

    def test_ad_unit_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units(ad_unit_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(name = "networks/123/adUnits/1" OR name = "networks/123/adUnits/2")'
        )

    def test_parent_ad_unit_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units(parent_ad_unit_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(parentAdUnit = "networks/123/adUnits/1" OR parentAdUnit = "networks/123/adUnits/2")'
        )

    def test_all_fields_produce_expected_filter_str_in_order(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units(
            ad_unit_id=456,
            display_name="Homepage",
            parent_ad_unit_id=1,
            ad_unit_code="HP1",
            status="ACTIVE",
            explicitly_targeted=True,
            has_children=False,
            update_time=datetime(2025, 1, 1, tzinfo=UTC),
        )

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'name = "networks/123/adUnits/456" AND displayName = "Homepage" '
            'AND parentAdUnit = "networks/123/adUnits/1" AND adUnitCode = "HP1" '
            'AND status = "ACTIVE" AND explicitlyTargeted = true AND hasChildren = false '
            'AND updateTime = "2025-01-01T00:00:00+00:00"'
        )

    def test_partial_fields_are_joined_in_field_order_skipping_unset(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units(parent_ad_unit_id=1, status="ACTIVE", has_children=True)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'parentAdUnit = "networks/123/adUnits/1" AND status = "ACTIVE" AND hasChildren = true'
        )

    def test_no_filters_passes_none(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.list_ad_units()

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "a1"}]
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        assert client.list_ad_units() == [{"name": "a1"}]


class TestGetAdUnit:
    def test_fetches_by_id_path(self, fake_http_client):
        client = AdUnitClient(NETWORK_CODE, fake_http_client)

        client.get_ad_unit(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/adUnits/456")
