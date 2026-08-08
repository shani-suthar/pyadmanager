from pyadmanager.services.network import NetworkClient

NETWORK_CODE = "123"


class TestListNetworks:
    def test_builds_endpoint_with_no_filter(self, fake_http_client):
        client = NetworkClient(NETWORK_CODE, fake_http_client)

        client.list_networks()

        fake_http_client.fetch_all.assert_called_once_with(
            "networks", "networks", {"pageSize": 1000}
        )

    def test_page_size_is_forwarded(self, fake_http_client):
        client = NetworkClient(NETWORK_CODE, fake_http_client)

        client.list_networks(page_size=50)

        fake_http_client.fetch_all.assert_called_once_with("networks", "networks", {"pageSize": 50})

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "networks/123"}]
        client = NetworkClient(NETWORK_CODE, fake_http_client)

        assert client.list_networks() == [{"name": "networks/123"}]


class TestGetNetwork:
    def test_defaults_to_own_network_code(self, fake_http_client):
        client = NetworkClient(NETWORK_CODE, fake_http_client)

        client.get_network()

        fake_http_client.fetch.assert_called_once_with("networks/123")

    def test_explicit_network_code_overrides_default(self, fake_http_client):
        client = NetworkClient(NETWORK_CODE, fake_http_client)

        client.get_network(456)

        fake_http_client.fetch.assert_called_once_with("networks/456")

    def test_returns_fetch_result(self, fake_http_client):
        fake_http_client.fetch.return_value = {"name": "networks/123"}
        client = NetworkClient(NETWORK_CODE, fake_http_client)

        assert client.get_network() == {"name": "networks/123"}
