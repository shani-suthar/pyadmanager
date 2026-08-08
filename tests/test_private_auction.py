from datetime import UTC, datetime

from pyadmanager.services.private_auction import PrivateAuctionClient, PrivateAuctionFilter

NETWORK_CODE = "123"


class TestPrivateAuctionFilter:
    def test_name_uses_id_based_filter(self):
        filter_str = PrivateAuctionFilter(
            name="networks/123/privateAuctions/456"
        ).get_filter_string()

        assert filter_str == 'name = "networks/123/privateAuctions/456"'

    def test_display_name_and_description_are_quoted(self):
        filter_str = PrivateAuctionFilter(
            display_name="Q1 Auction", description="Quarterly deal"
        ).get_filter_string()

        assert filter_str == 'displayName = "Q1 Auction" AND description = "Quarterly deal"'

    def test_archived_is_bare_boolean(self):
        filter_str = PrivateAuctionFilter(archived=True).get_filter_string()

        assert filter_str == "archived = true"

    def test_create_time_and_update_time_are_quoted_rfc3339(self):
        dt = datetime(2025, 1, 1, tzinfo=UTC)
        filter_str = PrivateAuctionFilter(
            create_time=dt, update_time=(dt, "GT_EQ")
        ).get_filter_string()

        assert filter_str == (
            'createTime = "2025-01-01T00:00:00+00:00" AND updateTime >= "2025-01-01T00:00:00+00:00"'
        )

    def test_no_fields_returns_none(self):
        assert PrivateAuctionFilter().get_filter_string() is None


class TestListPrivateAuctions:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        client = PrivateAuctionClient(NETWORK_CODE, fake_http_client)

        client.list_private_auctions(display_name="Q1 Auction", archived=False)

        fake_http_client.fetch_all.assert_called_once_with(
            "networks/123/privateAuctions",
            "privateAuctions",
            {
                "pageSize": 1000,
                "filter": 'displayName = "Q1 Auction" AND archived = false',
            },
        )

    def test_private_auction_id_is_resolved_to_full_path(self, fake_http_client):
        client = PrivateAuctionClient(NETWORK_CODE, fake_http_client)

        client.list_private_auctions(private_auction_id=456)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/privateAuctions/456"'

    def test_no_filters_passes_none(self, fake_http_client):
        client = PrivateAuctionClient(NETWORK_CODE, fake_http_client)

        client.list_private_auctions()

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "pa1"}]
        client = PrivateAuctionClient(NETWORK_CODE, fake_http_client)

        assert client.list_private_auctions() == [{"name": "pa1"}]


class TestGetPrivateAuction:
    def test_fetches_by_id_path(self, fake_http_client):
        client = PrivateAuctionClient(NETWORK_CODE, fake_http_client)

        client.get_private_auction(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/privateAuctions/456")
