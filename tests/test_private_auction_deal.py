from datetime import UTC, datetime

from pyadmanager.services.private_auction_deal import PrivateAuctionDealClient

NETWORK_CODE = "123"


class TestListPrivateAuctionDeals:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(status="ACTIVE", block_override_enabled=True)

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

        client.list(private_auction_deal_id=456)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/privateAuctionDeals/456"'

    def test_private_auction_id_is_resolved_against_private_auctions_resource(
        self, fake_http_client
    ):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(private_auction_id=1)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'privateAuctionId = "networks/123/privateAuctions/1"'

    def test_buyer_account_id_is_resolved_against_programmatic_buyers_resource(
        self, fake_http_client
    ):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(buyer_account_id=2)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'buyerAccountId = "networks/123/programmaticBuyers/2"'

    def test_external_deal_id_status_and_buyer_permission_type_are_quoted(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(external_deal_id="ext-1", status="ACTIVE", buyer_permission_type="BIDDER")

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'externalDealId = "ext-1" AND status = "ACTIVE" AND buyerPermissionType = "BIDDER"'
        )

    def test_boolean_fields_are_bare(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(auction_priority_enabled=True, block_override_enabled=False)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == "auctionPriorityEnabled = true AND blockOverrideEnabled = false"

    def test_end_time_is_quoted_rfc3339(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(end_time=(datetime(2025, 1, 1, tzinfo=UTC), "LT_EQ"))

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'endTime <= "2025-01-01T00:00:00+00:00"'

    def test_private_auction_deal_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(private_auction_deal_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(name = "networks/123/privateAuctionDeals/1" '
            'OR name = "networks/123/privateAuctionDeals/2")'
        )

    def test_private_auction_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(private_auction_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(privateAuctionId = "networks/123/privateAuctions/1" '
            'OR privateAuctionId = "networks/123/privateAuctions/2")'
        )

    def test_buyer_account_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(buyer_account_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(buyerAccountId = "networks/123/programmaticBuyers/1" '
            'OR buyerAccountId = "networks/123/programmaticBuyers/2")'
        )

    def test_all_fields_produce_expected_filter_str_in_order(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(
            private_auction_deal_id=456,
            private_auction_id=1,
            buyer_account_id=2,
            external_deal_id="ext-1",
            status="ACTIVE",
            buyer_permission_type="BIDDER",
            auction_priority_enabled=True,
            block_override_enabled=False,
            end_time=datetime(2025, 2, 1, tzinfo=UTC),
            create_time=datetime(2024, 12, 1, tzinfo=UTC),
            update_time=datetime(2025, 1, 1, tzinfo=UTC),
        )

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'name = "networks/123/privateAuctionDeals/456" '
            'AND privateAuctionId = "networks/123/privateAuctions/1" '
            'AND buyerAccountId = "networks/123/programmaticBuyers/2" '
            'AND externalDealId = "ext-1" AND status = "ACTIVE" '
            'AND buyerPermissionType = "BIDDER" AND auctionPriorityEnabled = true '
            'AND blockOverrideEnabled = false AND endTime = "2025-02-01T00:00:00+00:00" '
            'AND createTime = "2024-12-01T00:00:00+00:00" '
            'AND updateTime = "2025-01-01T00:00:00+00:00"'
        )

    def test_partial_fields_are_joined_in_field_order_skipping_unset(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list(buyer_permission_type="BIDDER", auction_priority_enabled=True)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'buyerPermissionType = "BIDDER" AND auctionPriorityEnabled = true'
        )

    def test_no_filters_passes_none(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.list()

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "d1"}]
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        assert client.list() == [{"name": "d1"}]


class TestGetPrivateAuctionDeal:
    def test_fetches_by_id_path(self, fake_http_client):
        client = PrivateAuctionDealClient(NETWORK_CODE, fake_http_client)

        client.get(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/privateAuctionDeals/456")
