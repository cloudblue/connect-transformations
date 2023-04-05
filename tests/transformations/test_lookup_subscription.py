# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.exceptions import SubscriptionLookupError
from connect_transformations.transformations import StandardTransformationsApplication


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
    with pytest.raises(SubscriptionLookupError) as e:
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
    with pytest.raises(SubscriptionLookupError) as e:
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
