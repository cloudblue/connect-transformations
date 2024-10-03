# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from decimal import Decimal

import pytest
from connect.eaas.core.enums import ResultType
from responses import matchers

from connect_transformations.transformations import StandardTransformationsApplication


def test_currency_conversion_first(mocker, responses):
    params = {
        'symbols': 'EUR',
        'base': 'USD',
        'app_id': '1a2b3c4d5e6f',
    }
    responses.add(
        'GET',
        'https://openexchangerates.org/api/latest.json',
        match=[matchers.query_param_matcher(params)],
        json={
            'rates': {'EUR': 0.92343},
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, config={'EXCHANGE_API_KEY': '1a2b3c4d5e6f'})
    app.transformation_request = {
        'transformation': {
            'settings': [{
                'from': {'column': 'C123', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            }],
            'columns': {
                'input': [{'id': 'C123', 'name': 'Price', 'nullable': False}],
            },
        },
    }

    response = app.currency_conversion(
        {
            'Price': '22.5',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Price(Eur)': (
            Decimal('22.5') * Decimal(0.92343)
        ).quantize(
            Decimal('.00001'),
        ),
    }


def test_currency_conversion_single_backward_compt(mocker, responses):
    params = {
        'symbols': 'EUR',
        'base': 'USD',
        'app_id': '1a2b3c4d5e6f',
    }
    responses.add(
        'GET',
        'https://openexchangerates.org/api/latest.json',
        match=[matchers.query_param_matcher(params)],
        json={
            'rates': {'EUR': 0.92343},
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, {'EXCHANGE_API_KEY': '1a2b3c4d5e6f'})
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': {'column': 'C123', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            },
            'columns': {
                'input': [{'id': 'C123', 'name': 'Price', 'nullable': False}],
            },
        },
    }

    response = app.currency_conversion(
        {
            'Price': '22.5',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Price(Eur)': (
            Decimal('22.5') * Decimal(0.92343)
        ).quantize(
            Decimal('.00001'),
        ),
    }


def test_currency_conversion(mocker, responses):
    params = {
        'symbols': 'EUR',
        'base': 'USD',
        'app_id': '1a2b3c4d5e6f',
    }
    responses.add(
        'GET',
        'https://openexchangerates.org/api/latest.json',
        match=[matchers.query_param_matcher(params)],
        json={
            'success': True,
            'rates': {'EUR': 0.92343},
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, {'EXCHANGE_API_KEY': '1a2b3c4d5e6f'})
    app.transformation_request = {
        'transformation': {
            'settings': [{
                'from': {'column': 'COL123', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            }],
            'columns': {
                'input': [{'id': 'COL123', 'name': 'Price', 'nullable': False}],
            },
        },
    }

    response = app.currency_conversion(
        {
            'Price': '22.5',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Price(Eur)': (
            Decimal('22.5') * Decimal(0.92343)
        ).quantize(
            Decimal('.00001'),
        ),
    }


def test_currency_conversion_first_http_error(mocker, responses):
    params = {
        'symbols': 'EUR',
        'base': 'USD',
        'app_id': '1a2b3c4d5e6f',
    }
    responses.add(
        'GET',
        'https://openexchangerates.org/api/latest.json',
        match=[matchers.query_param_matcher(params)],
        status=500,
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, {'EXCHANGE_API_KEY': '1a2b3c4d5e6f'})
    app.transformation_request = {
        'transformation': {
            'settings': [{
                'from': {'column': 'COL123', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            }],
            'columns': {
                'input': [{'id': 'COL123', 'name': 'Price', 'nullable': False}],
            },
        },
    }

    response = app.currency_conversion({'Price': '22.5'})
    assert response.status == ResultType.FAIL
    assert (
        'An error occurred while requesting '
        'https://openexchangerates.org/api/latest.json with params'
        " {'symbols': 'EUR', 'base': 'USD'}"
    ) in response.output, response.output
    assert 'app_id' not in response.output


def test_currency_conversion_null_value(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.currency_conversion_rates = {'a': 'b'}
    app.transformation_request = {
        'transformation': {
            'settings': [{
                'from': {'column': 'COL1', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            }],
            'columns': {
                'input': [{'id': 'COL1', 'name': 'Price', 'nullable': True}],
            },
        },
    }

    response = app.currency_conversion(
        {
            'Price': None,
        },
    )
    assert response.status == ResultType.SKIP


def test_currency_conversion_no_input_column_found(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.currency_conversion_rates = {'EUR': Decimal(0.92343)}
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': {'column': 'Price', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            },
            'columns': {
                'input': [{'name': 'other'}],
            },
        },
    }

    with pytest.raises(Exception) as e:
        app.currency_conversion(
            {
                'Price': None,
            },
        )
        assert str(e.value) == 'The column Price does not exists.'
