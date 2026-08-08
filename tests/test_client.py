from datetime import UTC, datetime
from unittest.mock import Mock

from google.oauth2 import service_account

from pyadmanager.client import FULL_SCOPE, READONLY_SCOPE, GAMClient
from pyadmanager.services import (
    AdUnitClient,
    CustomTargetingClient,
    LineItemClient,
    NetworkClient,
    OrderClient,
    PlacementClient,
    PrivateAuctionClient,
    PrivateAuctionDealClient,
    ProgrammaticBuyerClient,
    ReportClient,
    RoleClient,
    UserClient,
)


def fake_credentials() -> Mock:
    return Mock(spec=service_account.Credentials)


class TestInit:
    def test_network_code_is_stringified(self):
        client = GAMClient(network_code=123, auth=fake_credentials())
        assert client.network_code == "123"

    def test_network_code_str_is_kept(self):
        client = GAMClient(network_code="123", auth=fake_credentials())
        assert client.network_code == "123"


class TestFromServiceAccountFile:
    def test_defaults_to_full_scope(self, monkeypatch):
        creds = fake_credentials()
        from_file = Mock(return_value=creds)
        monkeypatch.setattr(service_account.Credentials, "from_service_account_file", from_file)

        client = GAMClient.from_service_account_file(123, "creds.json")

        from_file.assert_called_once_with("creds.json", scopes=[FULL_SCOPE])
        assert client.http_client.auth is creds
        assert client.network_code == "123"

    def test_readonly_uses_readonly_scope(self, monkeypatch):
        creds = fake_credentials()
        from_file = Mock(return_value=creds)
        monkeypatch.setattr(service_account.Credentials, "from_service_account_file", from_file)

        GAMClient.from_service_account_file(123, "creds.json", readonly=True)

        from_file.assert_called_once_with("creds.json", scopes=[READONLY_SCOPE])

    def test_explicit_scopes_are_not_overridden(self, monkeypatch):
        creds = fake_credentials()
        from_file = Mock(return_value=creds)
        monkeypatch.setattr(service_account.Credentials, "from_service_account_file", from_file)

        GAMClient.from_service_account_file(123, "creds.json", scopes=["custom-scope"])

        from_file.assert_called_once_with("creds.json", scopes=["custom-scope"])


class TestFromServiceAccountInfo:
    def test_defaults_to_full_scope(self, monkeypatch):
        creds = fake_credentials()
        from_info = Mock(return_value=creds)
        monkeypatch.setattr(service_account.Credentials, "from_service_account_info", from_info)

        client = GAMClient.from_service_account_info(123, {"type": "service_account"})

        from_info.assert_called_once_with({"type": "service_account"}, scopes=[FULL_SCOPE])
        assert client.http_client.auth is creds

    def test_readonly_uses_readonly_scope(self, monkeypatch):
        creds = fake_credentials()
        from_info = Mock(return_value=creds)
        monkeypatch.setattr(service_account.Credentials, "from_service_account_info", from_info)

        GAMClient.from_service_account_info(123, {}, readonly=True)

        from_info.assert_called_once_with({}, scopes=[READONLY_SCOPE])


class TestExpiry:
    def test_returns_credentials_expiry(self):
        creds = fake_credentials()
        creds.expiry = datetime(2025, 1, 1, tzinfo=UTC)
        client = GAMClient(network_code=123, auth=creds)

        assert client.expiry == datetime(2025, 1, 1, tzinfo=UTC)

    def test_none_when_credentials_have_no_expiry(self):
        creds = fake_credentials()
        creds.expiry = None
        client = GAMClient(network_code=123, auth=creds)

        assert client.expiry is None


class TestResourceClients:
    def test_custom_targeting_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        custom_targeting = client.custom_targeting

        assert isinstance(custom_targeting, CustomTargetingClient)
        assert custom_targeting.network_code == "123"
        assert custom_targeting.http_client is client.http_client

    def test_custom_targeting_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.custom_targeting is client.custom_targeting

    def test_line_item_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        line_item = client.line_item

        assert isinstance(line_item, LineItemClient)
        assert line_item.network_code == "123"
        assert line_item.http_client is client.http_client

    def test_line_item_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.line_item is client.line_item

    def test_report_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        report = client.report

        assert isinstance(report, ReportClient)
        assert report.network_code == "123"
        assert report.http_client is client.http_client

    def test_report_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.report is client.report

    def test_network_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        network = client.network

        assert isinstance(network, NetworkClient)
        assert network.network_code == "123"
        assert network.http_client is client.http_client

    def test_network_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.network is client.network

    def test_role_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        role = client.role

        assert isinstance(role, RoleClient)
        assert role.network_code == "123"
        assert role.http_client is client.http_client

    def test_role_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.role is client.role

    def test_user_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        user = client.user

        assert isinstance(user, UserClient)
        assert user.network_code == "123"
        assert user.http_client is client.http_client

    def test_user_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.user is client.user

    def test_placement_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        placement = client.placement

        assert isinstance(placement, PlacementClient)
        assert placement.network_code == "123"
        assert placement.http_client is client.http_client

    def test_placement_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.placement is client.placement

    def test_order_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        order = client.order

        assert isinstance(order, OrderClient)
        assert order.network_code == "123"
        assert order.http_client is client.http_client

    def test_order_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.order is client.order

    def test_ad_unit_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        ad_unit = client.ad_unit

        assert isinstance(ad_unit, AdUnitClient)
        assert ad_unit.network_code == "123"
        assert ad_unit.http_client is client.http_client

    def test_ad_unit_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.ad_unit is client.ad_unit

    def test_private_auction_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        private_auction = client.private_auction

        assert isinstance(private_auction, PrivateAuctionClient)
        assert private_auction.network_code == "123"
        assert private_auction.http_client is client.http_client

    def test_private_auction_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.private_auction is client.private_auction

    def test_private_auction_deal_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        private_auction_deal = client.private_auction_deal

        assert isinstance(private_auction_deal, PrivateAuctionDealClient)
        assert private_auction_deal.network_code == "123"
        assert private_auction_deal.http_client is client.http_client

    def test_private_auction_deal_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.private_auction_deal is client.private_auction_deal

    def test_programmatic_buyer_is_wired_correctly(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        programmatic_buyer = client.programmatic_buyer

        assert isinstance(programmatic_buyer, ProgrammaticBuyerClient)
        assert programmatic_buyer.network_code == "123"
        assert programmatic_buyer.http_client is client.http_client

    def test_programmatic_buyer_is_cached(self):
        client = GAMClient(network_code=123, auth=fake_credentials())

        assert client.programmatic_buyer is client.programmatic_buyer
