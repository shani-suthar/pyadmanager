from datetime import UTC, datetime

from pyadmanager.services.private_auction_deal import (
    PrivateAuctionDealClient,
    PrivateAuctionDealFilter,
)

NETWORK_CODE = "123"


class TestPrivateAuctionDealFilter:
    def test_name_uses_id_based_filter(self):
        filter_str = PrivateAuctionDealFilter(
            name="networks/123/privateAuctionDeals/456"
        ).get_filter_string()

        assert filter_str == 'name = "networks/123/privateAuctionDeals/456"'

    def test_private_auction_and_buyer_account_use_id_based_filter(self):
        filter_str = PrivateAuctionDealFilter(
            private_auction="networks/123/privateAuctions/1",
            buyer_account="networks/123/programmaticBuyers/2",
        ).get_filter_string()

        assert filter_str == (
            'privateAuctionId = "networks/123/privateAuctions/1" '
            'AND buyerAccountId = "networks/123/programmaticBuyers/2"'
        )

    def test_external_deal_id_status_and_buyer_permission_type_are_quoted(self):
        filter_str = PrivateAuctionDealFilter(
            external_deal_id="ext-1", status="ACTIVE", buyer_permission_type="BIDDER"
        ).get_filter_string()

        assert filter_str == (
            'externalDealId = "ext-1" AND status = "ACTIVE" AND buyerPermissionType = "BIDDER"'
        )

    def test_boolean_fields_are_bare(self):
        filter_str = PrivateAuctionDealFilter(
            auction_priority_enabled=True, block_override_enabled=False
        ).get_filter_string()

        assert filter_str == "auctionPriorityEnabled = true AND blockOverrideEnabled = false"

    def test_end_time_is_quoted_rfc3339(self):
        filter_str = PrivateAuctionDealFilter(
            end_time=(datetime(2025, 1, 1, tzinfo=UTC), "LT_EQ")
        ).get_filter_string()

        assert filter_str == 'endTime <= "2025-01-01T00:00:00+00:00"'

    def test_no_fields_returns_none(self):
        assert PrivateAuctionDealFilter().get_filter_string() is None


class TestListPrivateAuctionDeals:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list_private_auction_deals(status="ACTIVE", block_override_enabled=True)

        fake_http_client.fetch_all.assert_called_once_with(
            "networks/123/privateAuctionDeals",
            "privateAuctionDeals",
            {
                "pageSize": 1000,
                "filter": 'status = "ACTIVE" AND blockOverrideEnabled = true',
            },
        )

    def test_private_auction_deal_id_is_resolved_to_full_path(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list_private_auction_deals(private_auction_deal_id=456)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/privateAuctionDeals/456"'

    def test_private_auction_id_is_resolved_against_private_auctions_resource(
        self, fake_http_client
    ):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list_private_auction_deals(private_auction_id=1)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'privateAuctionId = "networks/123/privateAuctions/1"'

    def test_buyer_account_id_is_resolved_against_programmatic_buyers_resource(
        self, fake_http_client
    ):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list_private_auction_deals(buyer_account_id=2)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'buyerAccountId = "networks/123/programmaticBuyers/2"'

    def test_no_filters_passes_none(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list_private_auction_deals()

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "d1"}]
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        assert client.list_private_auction_deals() == [{"name": "d1"}]


class TestGetPrivateAuctionDeal:
    def test_fetches_by_id_path(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.get_private_auction_deal(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/privateAuctionDeals/456")
