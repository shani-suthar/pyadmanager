from pyadmanager.services.role import RoleClient

NETWORK_CODE = "123"


class TestListRoles:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.list(display_name="Admin", status="ACTIVE")

        fake_http_client.fetch_all.assert_called_once_with(
            "networks/123/roles",
            "roles",
            {
                "pageSize": 1000,
                "filter": 'displayName = "Admin" AND status = "ACTIVE"',
            },
        )

    def test_role_id_is_resolved_to_full_path(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.list(role_id=456)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/roles/456"'

    def test_role_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.list(role_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert (
            params["filter"] == '(name = "networks/123/roles/1" OR name = "networks/123/roles/2")'
        )

    def test_built_in_is_bare_boolean(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.list(built_in=True)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == "builtIn = true"

    def test_all_fields_produce_expected_filter_str_in_order(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.list(role_id=456, display_name="Admin", status="ACTIVE", built_in=True)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'name = "networks/123/roles/456" AND displayName = "Admin" '
            'AND status = "ACTIVE" AND builtIn = true'
        )

    def test_partial_fields_are_joined_in_field_order_skipping_unset(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.list(display_name="Admin", built_in=True)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'displayName = "Admin" AND builtIn = true'

    def test_no_filters_passes_none(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.list()

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "r1"}]
        client = RoleClient(NETWORK_CODE, fake_http_client)

        assert client.list() == [{"name": "r1"}]


class TestGetRole:
    def test_fetches_by_id_path(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.get(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/roles/456")
