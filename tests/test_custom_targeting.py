from pyadmanager.services.custom_targeting import CustomTargetingClient

NETWORK_CODE = "123"


class TestListKeys:
    def test_builds_endpoint_and_filter(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_keys(display_name="colors", status="ACTIVE")

        http_client.fetch_all.assert_called_once_with(
            "networks/123/customTargetingKeys",
            "customTargetingKeys",
            {
                "pageSize": 1000,
                "filter": 'displayName = "colors" AND status = "ACTIVE"',
            },
        )

    def test_key_id_is_resolved_to_full_path(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_keys(key_id=456)

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/customTargetingKeys/456"'

    def test_key_id_list_is_resolved_to_or_clause(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_keys(key_id=[1, 2])

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(name = "networks/123/customTargetingKeys/1" '
            'OR name = "networks/123/customTargetingKeys/2")'
        )

    def test_text_fields_are_quoted(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_keys(
            display_name="colors", ad_tag_name="tag", status="ACTIVE", key_type="FREEFORM"
        )

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'displayName = "colors" AND adTagName = "tag" '
            'AND status = "ACTIVE" AND type = "FREEFORM"'
        )

    def test_all_fields_produce_expected_filter_str_in_order(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_keys(
            key_id=456,
            display_name="colors",
            ad_tag_name="tag",
            reportable_type="ON",
            status="ACTIVE",
            key_type="FREEFORM",
        )

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'name = "networks/123/customTargetingKeys/456" AND displayName = "colors" '
            'AND adTagName = "tag" AND reportableType = "ON" AND status = "ACTIVE" '
            'AND type = "FREEFORM"'
        )

    def test_partial_fields_are_joined_in_field_order_skipping_unset(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_keys(ad_tag_name="tag", key_type="FREEFORM")

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'adTagName = "tag" AND type = "FREEFORM"'

    def test_no_filters_passes_none(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_keys()

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self, fake_http_client):
        http_client = fake_http_client
        http_client.fetch_all.return_value = [{"name": "k1"}]
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        assert client.list_keys() == [{"name": "k1"}]


class TestGetKey:
    def test_fetches_by_id_path(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.get_key(456)

        http_client.fetch.assert_called_once_with("networks/123/customTargetingKeys/456")


class TestListValues:
    def test_resolves_both_value_and_key_id(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_values(value_id=1, custom_targeting_key_id=2)

        http_client.fetch_all.assert_called_once_with(
            "networks/123/customTargetingValues",
            "customTargetingValues",
            {
                "pageSize": 1000,
                "filter": (
                    'customTargetingKey = "networks/123/customTargetingKeys/2" '
                    'AND name = "networks/123/customTargetingValues/1"'
                ),
            },
        )

    def test_status_list_and_match_type_are_quoted(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_values(status=["ACTIVE", "INACTIVE"], match_type="EXACT")

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(status = "ACTIVE" OR status = "INACTIVE") AND matchType = "EXACT"'
        )

    def test_value_id_list_is_resolved_to_or_clause(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_values(value_id=[1, 2])

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(name = "networks/123/customTargetingValues/1" '
            'OR name = "networks/123/customTargetingValues/2")'
        )

    def test_custom_targeting_key_id_list_is_resolved_to_or_clause(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_values(custom_targeting_key_id=[1, 2])

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(customTargetingKey = "networks/123/customTargetingKeys/1" '
            'OR customTargetingKey = "networks/123/customTargetingKeys/2")'
        )

    def test_all_fields_produce_expected_filter_str_in_order(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_values(
            value_id=1,
            custom_targeting_key_id=2,
            display_name="Red",
            ad_tag_name="tag",
            status="ACTIVE",
            match_type="EXACT",
        )

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            'customTargetingKey = "networks/123/customTargetingKeys/2" '
            'AND name = "networks/123/customTargetingValues/1" AND displayName = "Red" '
            'AND adTagName = "tag" AND status = "ACTIVE" AND matchType = "EXACT"'
        )

    def test_partial_fields_are_joined_in_field_order_skipping_unset(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_values(display_name="Red", match_type="EXACT")

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'displayName = "Red" AND matchType = "EXACT"'

    def test_no_filters_passes_none(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_values()

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] is None


class TestGetValue:
    def test_fetches_by_id_path(self, fake_http_client):
        http_client = fake_http_client
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.get_value(789)

        http_client.fetch.assert_called_once_with("networks/123/customTargetingValues/789")
