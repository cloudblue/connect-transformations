# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.webapp import TransformationsWebApplication


def test_validate_currency_conversion(test_client_factory):
    data = {
        'settings': [
            {
                'from': {'column': 'COL-123', 'currency': 'USD'},
                'to': {'column': 'col1_eur', 'currency': 'EUR'},
            },
            {
                'from': {'column': 'COL-234', 'currency': 'USD'},
                'to': {'column': 'col2_eur', 'currency': 'EUR'},
            },
        ],
        'columns': {
            'input': [
                {'id': 'COL-123', 'name': 'col1'},
                {'id': 'COL-234', 'name': 'col2'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/currency_conversion/validate', json=data)

    assert response.status_code == 200, response.content
    data = response.json()

    assert data == {
        'overview': (
            'From: col1 (USD)\n'
            'To: col1_eur (EUR)\n'
            '\n'
            'From: col2 (USD)\n'
            'To: col2_eur (EUR)\n'
        ),
    }, data


@pytest.mark.parametrize(
    'data',
    (
        {},
        {'settings': []},
        {'settings': [{}]},
        {'settings': [{}], 'columns': {}},
    ),
)
def test_validate_currency_conversion_settings_or_invalid(test_client_factory, data):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/currency_conversion/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Invalid input data',
    }


@pytest.mark.parametrize(
    'settings',
    (
        [{'from': {'column': 'x'}}],
        [{'from': {'column': 'x', 'currency': ''}}],
        [{'from': {'column': 'x', 'currency': ''}, 'to': {'column': 'y'}}],
        [{'from': {'column': 'x', 'currency': ''}, 'to': {'currency': 'y'}}],
    ),
)
def test_validate_currency_conversion_invalid_format(test_client_factory, settings):
    data = {'settings': settings, 'columns': {'input': []}}
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/currency_conversion/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings must have `from` with the `column` and the `currency`, and '
            '`to` with the `column` and `currency` fields'
        ),
    }


def test_validate_currency_conversion_equal_currencies(test_client_factory):
    data = {
        'settings': [{
            'from': {'column': 'columnA', 'currency': 'USD'},
            'to': {'column': 'columnB', 'currency': 'USD'},
        }],
        'columns': {
            'input': [
                {'name': 'columnA'},
            ],
            'output': [
                {'name': 'columnB'},
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/currency_conversion/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings must have different currencies for `from` and `to`'
        ),
    }


def test_validate_currency_conversion_invalid_column(test_client_factory):
    data = {
        'settings': [{
            'from': {'column': 'column', 'currency': 'USD'},
            'to': {'column': 'columnB', 'currency': 'EUR'},
        }],
        'columns': {
            'input': [
                {'name': 'otherColumn'},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/currency_conversion/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings contains an invalid `from` column name "column" that does not exist on'
            ' columns.input'
        ),
    }


def test_get_available_rates(
    test_client_factory,
    httpx_mock,
):
    httpx_mock.add_response(
        method='GET',
        url='https://api.apilayer.com/exchangerates_data/symbols',
        json={
            'symbols': {
                'EUR': 'Euro',
                'USD': 'United States Dollar',
            },
            'success': True,
        },
    )
    client = test_client_factory(TransformationsWebApplication)
    response = client.get(
        '/api/currency_conversion/currencies',
        config={'EXCHANGE_API_KEY': 'API Key'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {
            'code': 'EUR',
            'description': 'Euro',
        },
        {
            'code': 'USD',
            'description': 'United States Dollar',
        },
    ]


def test_get_available_rates_invalid_response(
    test_client_factory,
    httpx_mock,
):
    httpx_mock.add_response(
        method='GET',
        url='https://api.apilayer.com/exchangerates_data/symbols',
        json={
            'symbols': {},
            'success': False,
        },
    )
    client = test_client_factory(TransformationsWebApplication)
    response = client.get(
        '/api/currency_conversion/currencies',
        config={'EXCHANGE_API_KEY': 'API Key'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_available_rates_invalid_status_code(
    test_client_factory,
    httpx_mock,
):
    httpx_mock.add_response(
        method='GET',
        url='https://api.apilayer.com/exchangerates_data/symbols',
        status_code=400,
    )
    client = test_client_factory(TransformationsWebApplication)
    response = client.get(
        '/api/currency_conversion/currencies',
        config={'EXCHANGE_API_KEY': 'API Key'},
    )

    assert response.status_code == 200
    data = response.json()
    assert data == []


def test_get_available_rates_code_exception(
    test_client_factory,
    mocker,
):
    mocker.patch(
        'connect_transformations.currency_conversion.mixins.httpx.AsyncClient',
        side_effect=Exception(),
    )

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/currency_conversion/currencies')

    assert response.status_code == 200
    data = response.json()
    assert data == []
