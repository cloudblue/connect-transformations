# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import asyncio
from decimal import Decimal

import httpx
import pytest

from connect_transformations.exceptions import BaseTransformationException, CurrencyConversionError
from connect_transformations.transformations import StandardTransformationsApplication


@pytest.mark.asyncio
async def test_currency_conversion_first(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/latest?symbols=EUR&base=USD',
        json={
            'success': True,
            'rates': {'EUR': 0.92343},
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': {'column': 'Price', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            },
            'columns': {
                'input': [{'name': 'Price', 'nullable': False}],
            },
        },
    }

    assert await app.currency_conversion(
        {
            'Price': '22.5',
        },
    ) == {
        'Price(Eur)': (
            Decimal('22.5') * Decimal(0.92343)
        ).quantize(
            Decimal('.00001'),
        ),
    }


@pytest.mark.asyncio
async def test_currency_conversion_first_with_multitask(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/latest?symbols=EUR&base=USD',
        json={
            'success': True,
            'rates': {'EUR': 0.92343},
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': {'column': 'Price', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            },
            'columns': {
                'input': [{'name': 'Price', 'nullable': False}],
            },
        },
    }

    tasks = []
    for _ in range(10):
        task = asyncio.create_task(
            app.currency_conversion(
                {
                    'Price': '22.5',
                },
            ),
        )
        tasks.append(task)

    results = await asyncio.gather(*tasks)
    for result in results:
        assert result == {
            'Price(Eur)': (
                Decimal('22.5') * Decimal(0.92343)
            ).quantize(
                Decimal('.00001'),
            ),
        }
    assert len(httpx_mock.get_requests()) == 1


@pytest.mark.asyncio
async def test_currency_conversion(mocker):
    mocked_client = mocker.patch(
        'connect_transformations.currency_conversion.mixins.httpx.Client',
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.current_exchange_rate = Decimal(0.92343)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': {'column': 'Price', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            },
            'columns': {
                'input': [{'name': 'Price', 'nullable': False}],
            },
        },
    }

    assert await app.currency_conversion(
        {
            'Price': '22.5',
        },
    ) == {
        'Price(Eur)': (
            Decimal('22.5') * Decimal(0.92343)
        ).quantize(
            Decimal('.00001'),
        ),
    }
    assert mocked_client.call_count == 0


@pytest.mark.asyncio
async def test_currency_conversion_first_http_error(mocker):
    mocker.patch(
        'connect_transformations.currency_conversion.mixins.httpx.Client',
        side_effect=httpx.RequestError('error'),
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': {'column': 'Price', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            },
            'columns': {
                'input': [{'name': 'Price', 'nullable': False}],
            },
        },
    }

    with pytest.raises(CurrencyConversionError) as e:
        await app.currency_conversion({'Price': '22.5'})
    assert str(e.value) == (
        'An error occurred while requesting '
        'https://api.exchangerate.host/latest with params'
        " {'symbols': 'EUR', 'base': 'USD'}: error"
    )


@pytest.mark.asyncio
async def test_currency_conversion_first_unexpected_response(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/latest?symbols=EUR&base=USD',
        json={
            'success': False,
            'result': None,
        },
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': {'column': 'Price', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            },
            'columns': {
                'input': [{'name': 'Price', 'nullable': False}],
            },
        },
    }

    with pytest.raises(CurrencyConversionError) as e:
        await app.currency_conversion({'Price': '22.5'})
    assert str(e.value) == (
        'Unexpected response calling '
        'https://api.exchangerate.host/latest with params'
        " {'symbols': 'EUR', 'base': 'USD'}"
    )


@pytest.mark.asyncio
async def test_currency_conversion_first_400_response(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/latest?symbols=EUR&base=USD',
        status_code=400,
        json={},
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': {'column': 'Price', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            },
            'columns': {
                'input': [{'name': 'Price', 'nullable': False}],
            },
        },
    }

    with pytest.raises(CurrencyConversionError) as e:
        await app.currency_conversion({'Price': '22.5'})
    assert str(e.value) == (
        'Unexpected response calling '
        'https://api.exchangerate.host/latest with params'
        " {'symbols': 'EUR', 'base': 'USD'}"
    )


@pytest.mark.asyncio
async def test_currency_conversion_null_value(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': {'column': 'Price', 'currency': 'USD'},
                'to': {'column': 'Price(Eur)', 'currency': 'EUR'},
            },
            'columns': {
                'input': [{'name': 'Price', 'nullable': True}],
            },
        },
    }

    assert await app.currency_conversion(
        {
            'Price': None,
        },
    ) == {
        'Price(Eur)': None,
    }


@pytest.mark.asyncio
async def test_currency_conversion_no_input_column_found(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.current_exchange_rate = Decimal(0.92343)
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

    with pytest.raises(BaseTransformationException) as e:
        await app.currency_conversion(
            {
                'Price': None,
            },
        )
        assert str(e.value) == 'The column Price does not exists.'
