from datetime import UTC, datetime

from pyadmanager.services.placement import PlacementClient, PlacementFilter

NETWORK_CODE = "123"


class TestPlacementFilter:
    def test_name_uses_id_based_filter(self):
        filter_str = PlacementFilter(name="networks/123/placements/456").get_filter_string()

        assert filter_str == 'name = "networks/123/placements/456"'

    def test_display_name_is_quoted(self):
        filter_str = PlacementFilter(display_name="Homepage").get_filter_string()

        assert filter_str == 'displayName = "Homepage"'

    def test_placement_code_is_quoted(self):
        filter_str = PlacementFilter(placement_code="ABC123").get_filter_string()

        assert filter_str == 'placementCode = "ABC123"'

    def test_status_is_quoted(self):
        filter_str = PlacementFilter(status="ACTIVE").get_filter_string()

        assert filter_str == 'status = "ACTIVE"'

    def test_update_time_is_quoted_rfc3339(self):
        filter_str = PlacementFilter(
            update_time=(datetime(2025, 1, 1, tzinfo=UTC), "GT_EQ")
        ).get_filter_string()

        assert filter_str == 'updateTime >= "2025-01-01T00:00:00+00:00"'

    def test_no_fields_returns_none(self):
        assert PlacementFilter().get_filter_string() is None


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
