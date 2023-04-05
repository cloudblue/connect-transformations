# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import httpx
import pytest

from connect_transformations.exceptions import CurrencyConversion, SubscriptionLookup
from connect_transformations.transformations import StandardTransformationsApplication


def test_copy_columns(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': [
                {'from': 'ColumnA', 'to': 'NewColC'},
                {'from': 'ColumnB', 'to': 'NewColD'},
            ],
        },
    }
    assert app.copy_columns(
        {
            'ColumnA': 'ContentColumnA',
            'ColumnB': 'ContentColumnB',
        },
    ) == {
        'NewColC': 'ContentColumnA',
        'NewColD': 'ContentColumnB',
    }


@pytest.mark.asyncio
async def test_lookup_subscription(mocker, async_connect_client, async_client_mocker_factory):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('subscriptions').assets.all().filter(id='SubscriptionID').count(return_value=1)
    client('subscriptions').assets.all().filter(id='SubscriptionID').limit(1).mock(return_value=[{
        'product': {'id': 'product.id', 'name': 'product.name'},
        'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
        'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
        'id': 'subscription.id',
        'external_id': 'subscription.external_id',
    }])

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'id',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    assert await app.lookup_subscription({
        'ColumnA': 'SubscriptionID',
    }) == {
        'PREFIX.product.id': 'product.id',
        'PREFIX.product.name': 'product.name',
        'PREFIX.marketplace.id': 'marketplace.id',
        'PREFIX.marketplace.name': 'marketplace.name',
        'PREFIX.vendor.id': 'vendor.id',
        'PREFIX.vendor.name': 'vendor.name',
        'PREFIX.subscription.id': 'subscription.id',
        'PREFIX.subscription.external_id': 'subscription.external_id',
    }


@pytest.mark.asyncio
async def test_lookup_subscription_cached(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'id',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    app._cache['id-SubscriptionID'] = {
        'product': {'id': 'product.id', 'name': 'product.name'},
        'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
        'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
        'id': 'subscription.id',
        'external_id': 'subscription.external_id',
    }
    assert await app.lookup_subscription({
        'ColumnA': 'SubscriptionID',
    }) == {
        'PREFIX.product.id': 'product.id',
        'PREFIX.product.name': 'product.name',
        'PREFIX.marketplace.id': 'marketplace.id',
        'PREFIX.marketplace.name': 'marketplace.name',
        'PREFIX.vendor.id': 'vendor.id',
        'PREFIX.vendor.name': 'vendor.name',
        'PREFIX.subscription.id': 'subscription.id',
        'PREFIX.subscription.external_id': 'subscription.external_id',
    }


@pytest.mark.asyncio
async def test_lookup_subscription_not_found(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('subscriptions').assets.all().filter(id='SubscriptionID').count(return_value=0)

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'id',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    with pytest.raises(SubscriptionLookup) as e:
        await app.lookup_subscription(
            {
                'ColumnA': 'SubscriptionID',
            },
        )
    assert str(e.value) == "No result found for the filter {'id': 'SubscriptionID'}"


@pytest.mark.asyncio
async def test_lookup_subscription_found_too_many(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('subscriptions').assets.all().filter(id='SubscriptionID').count(return_value=3)

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'id',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    with pytest.raises(SubscriptionLookup) as e:
        await app.lookup_subscription(
            {
                'ColumnA': 'SubscriptionID',
            },
        )
    assert str(e.value) == "Many results found for the filter {'id': 'SubscriptionID'}"


@pytest.mark.asyncio
async def test_lookup_subscription_null_value(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'id',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': True}],
            },
        },
    }
    assert await app.lookup_subscription({
        'ColumnA': None,
    }) == {
        'PREFIX.product.id': None,
        'PREFIX.product.name': None,
        'PREFIX.marketplace.id': None,
        'PREFIX.marketplace.name': None,
        'PREFIX.vendor.id': None,
        'PREFIX.vendor.name': None,
        'PREFIX.subscription.id': None,
        'PREFIX.subscription.external_id': None,
    }


@pytest.mark.asyncio
async def test_currency_conversion(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/convert?from=USD&to=EUR&amount=22.5',
        json={
            'success': True,
            'result': 23.5,
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
        'Price(Eur)': 23.5,
    }


@pytest.mark.asyncio
async def test_currency_conversion_http_error(mocker):
    mocker.patch(
        'connect_transformations.transformations.httpx.AsyncClient',
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

    with pytest.raises(CurrencyConversion) as e:
        await app.currency_conversion({'Price': '22.5'})
    assert str(e.value) == (
        'An error occurred while requesting '
        'https://api.exchangerate.host/convert with params'
        " {'from': 'USD', 'to': 'EUR', 'amount': '22.5'}: error"
    )


@pytest.mark.asyncio
async def test_currency_conversion_unexpected_response(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/convert?from=USD&to=EUR&amount=22.5',
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

    with pytest.raises(CurrencyConversion) as e:
        await app.currency_conversion({'Price': '22.5'})
    assert str(e.value) == (
        'Unexpected response calling '
        'https://api.exchangerate.host/convert with params'
        " {'from': 'USD', 'to': 'EUR', 'amount': '22.5'}"
    )


@pytest.mark.asyncio
async def test_currency_conversion_400_response(mocker, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url='https://api.exchangerate.host/convert?from=USD&to=EUR&amount=22.5',
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

    with pytest.raises(CurrencyConversion) as e:
        await app.currency_conversion({'Price': '22.5'})
    assert str(e.value) == (
        'Unexpected response calling '
        'https://api.exchangerate.host/convert with params'
        " {'from': 'USD', 'to': 'EUR', 'amount': '22.5'}"
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

    assert await app.currency_conversion(
        {
            'Price': None,
        },
    ) == {
        'Price(Eur)': None,
    }


@pytest.mark.asyncio
async def test_split_column(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
                    'groups': [
                        {'first_name': 'First Name'},
                        {'last_name': 'Last Name'},
                    ],
                },
            },
        },
    }
    assert await app.split_column({
        'column': 'Name Surname',
    }) == {
        'First Name': 'Name',
        'Last Name': 'Surname',
    }


@pytest.mark.asyncio
async def test_split_column_not_match_regex(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+) (?P<other_name>\\w+)',
                    'groups': [
                        {'first_name': 'First Name'},
                        {'last_name': 'Last Name'},
                        {'other_name': 'Other name'},
                    ],
                },
            },
        },
    }
    assert await app.split_column({
        'column': 'Name Surname',
    }) == {
        'First Name': None,
        'Last Name': None,
        'Other name': None,
    }


@pytest.mark.asyncio
async def test_split_column_match_partially(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
                    'groups': [
                        {'first_name': 'First Name'},
                        {'last_name': 'Last Name'},
                    ],
                },
            },
        },
    }
    assert await app.split_column({
        'column': 'Name Surname Othername',
    }) == {
        'First Name': 'Name',
        'Last Name': 'Surname',
    }


@pytest.mark.asyncio
async def test_split_column_match_optional(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': '(?P<first_name>\\w+) (?:(?P<last_name>\\w+))?',
                    'groups': [
                        {'first_name': 'First Name'},
                        {'last_name': 'Last Name'},
                    ],
                },
            },
        },
    }
    assert await app.split_column({
        'column': 'Name ',
    }) == {
        'First Name': 'Name',
        'Last Name': None,
    }


def test_formula(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Price with Tax',
                        'formula': '.(Price without Tax) + .(Tax)',
                    },
                    {
                        'to': 'Tax value',
                        'formula': '.(Tax) / .(Price without Tax)',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'Price without Tax', 'nullable': False},
                    {'name': 'Tax', 'nullable': False},
                ],
            },
        },
    }
    assert app.formula({
        'Price without Tax': 100, 'Tax': 20,
    }) == {
        'Price with Tax': 120,
        'Tax value': 0.2,
    }


def test_formula_invalid_row(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Tax value',
                        'formula': '.(Tax) / .(Price without Tax)',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'Price without Tax', 'nullable': False},
                    {'name': 'Tax', 'nullable': False},
                ],
            },
        },
    }

    with pytest.raises(ValueError) as e:
        app.formula({'Price without Tax': 100, 'Tax': 'twenty'})

    assert str(e.value) == 'string ("twenty") and number (100) cannot be divided'
