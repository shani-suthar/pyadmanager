from pyadmanager.services.role import RoleClient, RoleFilter

NETWORK_CODE = "123"


class TestRoleFilter:
    def test_name_uses_id_based_filter(self):
        filter_str = RoleFilter(name="networks/123/roles/456").get_filter_string()

        assert filter_str == 'name = "networks/123/roles/456"'

    def test_display_name_is_quoted(self):
        filter_str = RoleFilter(display_name="Admin").get_filter_string()

        assert filter_str == 'displayName = "Admin"'

    def test_status_is_quoted(self):
        filter_str = RoleFilter(status="ACTIVE").get_filter_string()

        assert filter_str == 'status = "ACTIVE"'

    def test_built_in_is_bare_boolean(self):
        filter_str = RoleFilter(built_in=True).get_filter_string()

        assert filter_str == "builtIn = true"

    def test_no_fields_returns_none(self):
        assert RoleFilter().get_filter_string() is None


class TestListRoles:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.list_roles(display_name="Admin", status="ACTIVE")

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

        client.list_roles(role_id=456)

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/roles/456"'

    def test_role_id_list_is_resolved_to_or_clause(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.list_roles(role_id=[1, 2])

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert (
            params["filter"] == '(name = "networks/123/roles/1" OR name = "networks/123/roles/2")'
        )

    def test_no_filters_passes_none(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.list_roles()

        _, _, params = fake_http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        fake_http_client.fetch_all.return_value = [{"name": "r1"}]
        client = RoleClient(NETWORK_CODE, fake_http_client)

        assert client.list_roles() == [{"name": "r1"}]


class TestGetRole:
    def test_fetches_by_id_path(self, fake_http_client):
        client = RoleClient(NETWORK_CODE, fake_http_client)

        client.get_role(456)

        fake_http_client.fetch.assert_called_once_with("networks/123/roles/456")
