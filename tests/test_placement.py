from datetime import UTC, datetime

from pyadmanager.services.placement import PlacementClient

NETWORK_CODE = "123"


class TestListPlacements:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        client = PlacementClient(NETWORK_CODE, fake_http_client)

        client.list_placements(display_name="Homepage", status="ACTIVE")

        fake_http_client.fetch_all.assert_called_once_with(
            "networks/123/placements",
            "placements",
            {
                "pageSize": 1000,
                "filter": 'displayName = "Homepage" AND status = "ACTIVE"',
            },
        )

    def test_placement_id_is_resolved_to_full_path(self, fake_http_client):
        client = PlacementClient(NETWORK_CODE, fake_http_client)

        client.list_placements(placement_id=456)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/placements/456"'

    def test_placement_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = PlacementClient(NETWORK_CODE, fake_http_client)

        client.list_placements(placement_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(name = "networks/123/placements/1" OR name = "networks/123/placements/2")'
        )

    def test_placement_code_is_quoted(self, fake_http_client):
        client = PlacementClient(NETWORK_CODE, fake_http_client)

        client.list_placements(placement_code="ABC123")

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'placementCode = "ABC123"'

    def test_update_time_is_quoted_rfc3339(self, fake_http_client):
        client = PlacementClient(NETWORK_CODE, fake_http_client)

        client.list_placements(update_time=(datetime(2025, 1, 1, tzinfo=UTC), "GT_EQ"))

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'updateTime >= "2025-01-01T00:00:00+00:00"'

    def test_all_fields_produce_expected_filter_str_in_order(self, fake_http_client):
        client = PlacementClient(NETWORK_CODE, fake_http_client)

        client.list_placements(
            placement_id=456,
            display_name="Homepage",
            description="Main page placement",
            placement_code="ABC123",
            status="ACTIVE",
            update_time=datetime(2025, 1, 1, tzinfo=UTC),
        )

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'name = "networks/123/placements/456" AND displayName = "Homepage" '
            'AND description = "Main page placement" AND placementCode = "ABC123" '
            'AND status = "ACTIVE" AND updateTime = "2025-01-01T00:00:00+00:00"'
        )

    def test_partial_fields_are_joined_in_field_order_skipping_unset(self, fake_http_client):
        client = PlacementClient(NETWORK_CODE, fake_http_client)

        client.list_placements(description="Main page placement", status="ACTIVE")

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == ('description = "Main page placement" AND status = "ACTIVE"')

    def test_no_filters_passes_none(self, fake_http_client):
        client = PlacementClient(NETWORK_CODE, fake_http_client)

        client.list_placements()

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "p1"}]
        client = PlacementClient(NETWORK_CODE, fake_http_client)

        assert client.list_placements() == [{"name": "p1"}]


class TestGetPlacement:
    def test_fetches_by_id_path(self, fake_http_client):
        client = PlacementClient(NETWORK_CODE, fake_http_client)

        client.get_placement(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/placements/456")
