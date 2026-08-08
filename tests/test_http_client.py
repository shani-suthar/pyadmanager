from unittest.mock import Mock

import google.auth.credentials
import pytest
import requests

from pyadmanager.http_client import HTTPClient


@pytest.fixture
def http_client():
    fake_credentials = Mock(spec=google.auth.credentials.Credentials)
    client = HTTPClient(fake_credentials)
    client.authed_session = Mock()
    return client


def make_response(json_data: dict) -> Mock:
    response = Mock(spec=requests.Response)
    response.json.return_value = json_data
    response.raise_for_status.return_value = None
    return response


class TestFetch:
    def test_returns_parsed_json(self, http_client):
        http_client.authed_session.request.return_value = make_response({"foo": "bar"})

        assert http_client.fetch("networks/1/lineItems") == {"foo": "bar"}

    def test_builds_url_and_defaults_to_get(self, http_client):
        http_client.authed_session.request.return_value = make_response({})

        http_client.fetch("networks/1/lineItems", params={"pageSize": 1000})

        http_client.authed_session.request.assert_called_once_with(
            "GET",
            "https://admanager.googleapis.com/v1/networks/1/lineItems",
            params={"pageSize": 1000},
            cookies={},
        )

    def test_threads_explicit_http_method(self, http_client):
        http_client.authed_session.request.return_value = make_response({})

        http_client.fetch("networks/1/reports/456:run", http_method="POST")

        http_client.authed_session.request.assert_called_once_with(
            "POST",
            "https://admanager.googleapis.com/v1/networks/1/reports/456:run",
            params=None,
            cookies={},
        )

    def test_raises_on_http_error(self, http_client):
        response = make_response({})
        response.raise_for_status.side_effect = requests.HTTPError("boom")
        http_client.authed_session.request.return_value = response

        with pytest.raises(requests.HTTPError):
            http_client.fetch("networks/1/lineItems")


class TestFetchAll:
    def test_collects_gam_obj_type_across_pages(self, http_client):
        http_client.authed_session.request.side_effect = [
            make_response({"lineItems": [1, 2], "nextPageToken": "abc"}),
            make_response({"lineItems": [3], "nextPageToken": None}),
        ]

        results = http_client.fetch_all("networks/1/lineItems", "lineItems")

        assert results == [1, 2, 3]
        assert http_client.authed_session.request.call_count == 2

    def test_follows_next_page_token_in_params(self, http_client):
        http_client.authed_session.request.side_effect = [
            make_response({"lineItems": [1], "nextPageToken": "abc"}),
            make_response({"lineItems": [2]}),
        ]

        http_client.fetch_all("networks/1/lineItems", "lineItems", {"pageSize": 1000})

        second_call_params = http_client.authed_session.request.call_args_list[1].kwargs["params"]
        assert second_call_params["pageToken"] == "abc"

    def test_stops_when_no_next_page_token(self, http_client):
        http_client.authed_session.request.return_value = make_response({"lineItems": [1, 2]})

        results = http_client.fetch_all("networks/1/lineItems", "lineItems")

        assert results == [1, 2]
        assert http_client.authed_session.request.call_count == 1

    def test_missing_gam_obj_type_key_yields_empty_page(self, http_client):
        http_client.authed_session.request.return_value = make_response({})

        results = http_client.fetch_all("networks/1/lineItems", "lineItems")

        assert results == []


class TestFetchReportRows:
    ENDPOINT = "networks/1/reports/1/results/1:fetchRows"

    def test_collects_raw_pages_across_next_page_token(self, http_client):
        http_client.authed_session.request.side_effect = [
            make_response({"rows": [1], "nextPageToken": "abc"}),
            make_response({"rows": [2]}),
        ]

        results = http_client.fetch_report_rows(self.ENDPOINT)

        assert results == [
            {"rows": [1], "nextPageToken": "abc"},
            {"rows": [2]},
        ]
        assert http_client.authed_session.request.call_count == 2

    def test_uses_large_page_size(self, http_client):
        http_client.authed_session.request.return_value = make_response({"rows": []})

        http_client.fetch_report_rows(self.ENDPOINT)

        params = http_client.authed_session.request.call_args.kwargs["params"]
        assert params["pageSize"] == 10_000

    def test_follows_next_page_token_in_params(self, http_client):
        http_client.authed_session.request.side_effect = [
            make_response({"rows": [1], "nextPageToken": "abc"}),
            make_response({"rows": [2]}),
        ]

        http_client.fetch_report_rows(self.ENDPOINT)

        second_call_params = http_client.authed_session.request.call_args_list[1].kwargs["params"]
        assert second_call_params["pageToken"] == "abc"

    def test_stops_when_no_next_page_token(self, http_client):
        http_client.authed_session.request.return_value = make_response({"rows": [1]})

        results = http_client.fetch_report_rows(self.ENDPOINT)

        assert results == [{"rows": [1]}]
        assert http_client.authed_session.request.call_count == 1
