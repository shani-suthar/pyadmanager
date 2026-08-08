"""Shared fixtures for tests exercising per-resource `*Client`s against a mocked `HTTPClient`."""

from unittest.mock import Mock

import pytest

from pyadmanager.http_client import HTTPClient


@pytest.fixture
def fake_http_client() -> Mock:
    return Mock(spec=HTTPClient)
