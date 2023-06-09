# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest
import responses as request_responses
from connect.client import AsyncConnectClient, ConnectClient


@pytest.fixture
def connect_client():
    return ConnectClient(
        'ApiKey fake_api_key',
        endpoint='https://example.org/public/v1',
    )


@pytest.fixture
def async_connect_client():
    return AsyncConnectClient(
        'ApiKey fake_api_key',
        endpoint='https://example.org/public/v1',
    )


@pytest.fixture
def logger(mocker):
    return mocker.MagicMock()


@pytest.fixture
def non_mocked_hosts() -> list:
    return ['example.org']


@pytest.fixture
def responses():
    with request_responses.RequestsMock() as rsps:
        yield rsps
