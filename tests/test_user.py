from pyadmanager.services.user import UserClient

NETWORK_CODE = "123"


class TestGetUser:
    def test_fetches_by_id_path(self, fake_http_client):
        client = UserClient(NETWORK_CODE, fake_http_client)

        client.get(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/users/456")

    def test_returns_fetch_result(self, fake_http_client):
        fake_http_client.fetch.return_value = {"name": "networks/123/users/456"}
        client = UserClient(NETWORK_CODE, fake_http_client)

        assert client.get(456) == {"name": "networks/123/users/456"}
