from unittest.mock import Mock

import pytest
import requests

from pyadmanager.retry import retry


def make_http_error(status_code: int | None) -> requests.HTTPError:
    if status_code is None:
        return requests.HTTPError("boom")

    response = Mock(spec=requests.Response)
    response.status_code = status_code
    return requests.HTTPError("boom", response=response)


@pytest.fixture(autouse=True)
def no_sleep(monkeypatch):
    monkeypatch.setattr("pyadmanager.retry.time.sleep", lambda _: None)


def test_returns_result_on_first_success():
    func = Mock(return_value="ok")
    wrapped = retry()(func)

    assert wrapped() == "ok"
    assert func.call_count == 1


def test_retries_retryable_status_then_succeeds():
    func = Mock(side_effect=[make_http_error(503), make_http_error(429), "ok"])
    wrapped = retry(max_retries=3)(func)

    assert wrapped() == "ok"
    assert func.call_count == 3


def test_raises_immediately_on_non_retryable_status():
    func = Mock(side_effect=make_http_error(404))
    wrapped = retry(max_retries=3)(func)

    with pytest.raises(requests.HTTPError):
        wrapped()
    assert func.call_count == 1


def test_raises_immediately_when_response_is_none():
    func = Mock(side_effect=make_http_error(None))
    wrapped = retry(max_retries=3)(func)

    with pytest.raises(requests.HTTPError):
        wrapped()
    assert func.call_count == 1


def test_raises_after_exhausting_retries():
    func = Mock(side_effect=make_http_error(503))
    wrapped = retry(max_retries=2)(func)

    with pytest.raises(requests.HTTPError):
        wrapped()
    assert func.call_count == 3


def test_retries_on_connection_error_then_succeeds():
    func = Mock(side_effect=[requests.ConnectionError("no route"), "ok"])
    wrapped = retry(max_retries=3)(func)

    assert wrapped() == "ok"
    assert func.call_count == 2


def test_raises_after_exhausting_retries_on_connection_error():
    func = Mock(side_effect=requests.ConnectionError("no route"))
    wrapped = retry(max_retries=2)(func)

    with pytest.raises(requests.ConnectionError):
        wrapped()
    assert func.call_count == 3
