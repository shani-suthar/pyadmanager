from unittest.mock import Mock

from pyadmanager.http_client import HTTPClient
from pyadmanager.services.custom_targeting import (
    CustomTargetingClient,
    CustomTargetingKeyFilter,
    CustomTargetingValueFilter,
)

NETWORK_CODE = "123"


def fake_http_client() -> Mock:
    return Mock(spec=HTTPClient)


class TestCustomTargetingKeyFilter:
    def test_name_uses_id_based_filter(self):
        filter_str = CustomTargetingKeyFilter(
            name="networks/123/customTargetingKeys/456"
        ).get_filter_string()

        assert filter_str == 'name = "networks/123/customTargetingKeys/456"'

    def test_text_fields_are_quoted(self):
        filter_str = CustomTargetingKeyFilter(
            display_name="colors", ad_tag_name="tag", status="ACTIVE", key_type="FREEFORM"
        ).get_filter_string()

        assert filter_str == (
            'displayName = "colors" AND adTagName = "tag" '
            'AND status = "ACTIVE" AND type = "FREEFORM"'
        )

    def test_no_fields_returns_none(self):
        assert CustomTargetingKeyFilter().get_filter_string() is None


class TestCustomTargetingValueFilter:
    def test_name_and_key_use_id_based_filter(self):
        filter_str = CustomTargetingValueFilter(
            name="networks/123/customTargetingValues/1",
            custom_targeting_key="networks/123/customTargetingKeys/2",
        ).get_filter_string()

        assert filter_str == (
            'customTargetingKey = "networks/123/customTargetingKeys/2" '
            'AND name = "networks/123/customTargetingValues/1"'
        )

    def test_status_and_match_type_are_quoted(self):
        filter_str = CustomTargetingValueFilter(
            status=["ACTIVE", "INACTIVE"], match_type="EXACT"
        ).get_filter_string()

        assert filter_str == ('(status = "ACTIVE" OR status = "INACTIVE") AND matchType = "EXACT"')


class TestListKeys:
    def test_builds_endpoint_and_filter(self):
        http_client = fake_http_client()
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

    def test_key_id_is_resolved_to_full_path(self):
        http_client = fake_http_client()
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_keys(key_id=456)

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == 'name = "networks/123/customTargetingKeys/456"'

    def test_key_id_list_is_resolved_to_or_clause(self):
        http_client = fake_http_client()
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_keys(key_id=[1, 2])

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] == (
            '(name = "networks/123/customTargetingKeys/1" '
            'OR name = "networks/123/customTargetingKeys/2")'
        )

    def test_no_filters_passes_none(self):
        http_client = fake_http_client()
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.list_keys()

        _, _, params = http_client.fetch_all.call_args[0]
        assert params["filter"] is None

    def test_returns_fetch_all_result(self):
        http_client = fake_http_client()
        http_client.fetch_all.return_value = [{"name": "k1"}]
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        assert client.list_keys() == [{"name": "k1"}]


class TestGetKey:
    def test_fetches_by_id_path(self):
        http_client = fake_http_client()
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.get_key(456)

        http_client.fetch.assert_called_once_with("networks/123/customTargetingKeys/456")


class TestListValues:
    def test_resolves_both_value_and_key_id(self):
        http_client = fake_http_client()
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


class TestGetValue:
    def test_fetches_by_id_path(self):
        http_client = fake_http_client()
        client = CustomTargetingClient(NETWORK_CODE, http_client)

        client.get_value(789)

        http_client.fetch.assert_called_once_with("networks/123/customTargetingValues/789")
