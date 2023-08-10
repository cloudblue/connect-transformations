# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest
from connect.eaas.core.enums import ResultType

from connect_transformations.transformations import StandardTransformationsApplication


COMMON_FILTERS = {
    'status__in': (
        'active', 'terminating', 'suspended',
        'terminated', 'terminated',
    ),
}


@pytest.mark.asyncio
async def test_lookup_subscription(mocker, async_connect_client, async_client_mocker_factory):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('subscriptions').assets.all().filter(
        **COMMON_FILTERS,
        id='SubscriptionID',
    ).order_by('-events.created.at').mock(return_value=[{
        'product': {'id': 'product.id', 'name': 'product.name'},
        'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
        'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
        'id': 'subscription.id',
        'external_id': 'subscription.external_id',
        'status': 'active',
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
                'action_if_not_found': 'leave_empty',
                'action_if_multiple': 'use_most_actual',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    response = await app.lookup_subscription({
        'ColumnA': 'SubscriptionID',
    })
    assert response.status == ResultType.SUCCESS, response.output
    assert response.transformed_row == {
        'PREFIX.product.id': 'product.id',
        'PREFIX.product.name': 'product.name',
        'PREFIX.marketplace.id': 'marketplace.id',
        'PREFIX.marketplace.name': 'marketplace.name',
        'PREFIX.vendor.id': 'vendor.id',
        'PREFIX.vendor.name': 'vendor.name',
        'PREFIX.subscription.id': 'subscription.id',
        'PREFIX.subscription.external_id': 'subscription.external_id',
        'PREFIX.subscription.status': 'active',
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
                'action_if_not_found': 'leave_empty',
                'action_if_multiple': 'fail',
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
        'status': 'terminated',
    }
    response = await app.lookup_subscription({
        'ColumnA': 'SubscriptionID',
    })

    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'PREFIX.product.id': 'product.id',
        'PREFIX.product.name': 'product.name',
        'PREFIX.marketplace.id': 'marketplace.id',
        'PREFIX.marketplace.name': 'marketplace.name',
        'PREFIX.vendor.id': 'vendor.id',
        'PREFIX.vendor.name': 'vendor.name',
        'PREFIX.subscription.id': 'subscription.id',
        'PREFIX.subscription.external_id': 'subscription.external_id',
        'PREFIX.subscription.status': 'terminated',
    }


@pytest.mark.asyncio
async def test_lookup_subscription_not_found(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('subscriptions').assets.filter(
        **COMMON_FILTERS,
        id='SubscriptionID',
    ).order_by('-events.created.at').mock(return_value=[])

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'id',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'fail',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }

    response = await app.lookup_subscription(
        {
            'ColumnA': 'SubscriptionID',
        },
    )
    assert response.status == ResultType.FAIL
    assert "No result found for the filter {'id': 'SubscriptionID'}" in response.output


@pytest.mark.asyncio
async def test_lookup_subscription_not_found_leave_empty(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('subscriptions').assets.filter(
        **COMMON_FILTERS,
        id='SubscriptionID',
    ).order_by('-events.created.at').mock(return_value=[])

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'id',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    response = await app.lookup_subscription(
        {
            'ColumnA': 'SubscriptionID',
        },
    )
    assert response.status == ResultType.SKIP


@pytest.mark.asyncio
async def test_lookup_subscription_found_multiple_fail(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
):
    params = {'params.name': 'param_a', 'params.value': 'SubscriptionID'}

    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('subscriptions').assets.filter(
        **COMMON_FILTERS,
        **params,
    ).order_by('-events.created.at').mock(return_value=[
        {
            'product': {'id': 'product.id', 'name': 'product.name'},
            'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
            'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
            'id': '1',
            'external_id': '1',
            'status': 'active',
        },
        {
            'product': {'id': 'product.id', 'name': 'product.name'},
            'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
            'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
            'id': '2',
            'external_id': '2',
            'status': 'active',
        },
    ])

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'params__value',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
                'action_if_multiple': 'fail',
                'parameter': {'id': 'PRD-123', 'name': 'param_a'},
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }

    response = await app.lookup_subscription(
        {
            'ColumnA': 'SubscriptionID',
        },
    )
    assert response.status == ResultType.FAIL
    assert f'Many results found for the filter {params}' in response.output


@pytest.mark.asyncio
async def test_lookup_subscription_found_multiple_leave_empty(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
):
    params = {'params.name': 'param_a', 'params.value': 'SubscriptionID'}

    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('subscriptions').assets.filter(
        **COMMON_FILTERS,
        **params,
    ).order_by('-events.created.at').mock(return_value=[
        {
            'product': {'id': 'product.id', 'name': 'product.name'},
            'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
            'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
            'id': '1',
            'external_id': '1',
            'status': 'active',
        },
        {
            'product': {'id': 'product.id', 'name': 'product.name'},
            'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
            'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
            'id': '2',
            'external_id': '2',
            'status': 'active',
        },
    ])

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'params__value',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
                'action_if_multiple': 'leave_empty',
                'parameter': {'id': 'PRD-123', 'name': 'param_a'},
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }

    response = await app.lookup_subscription(
        {
            'ColumnA': 'SubscriptionID',
        },
    )
    assert response.status == ResultType.SKIP


@pytest.mark.asyncio
@pytest.mark.parametrize('sub_status', ('active', 'terminating'))
async def test_lookup_subscription_found_multiple_use_most_actual_active(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
    sub_status,
):
    params = {'params.name': 'param_a', 'params.value': 'SubscriptionID'}

    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('subscriptions').assets.filter(
        **COMMON_FILTERS,
        **params,
    ).order_by('-events.created.at').mock(return_value=[
        {
            'product': {'id': 'product.id', 'name': 'product.name'},
            'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
            'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
            'id': '1',
            'external_id': '1',
            'status': 'terminated',
        },
        {
            'product': {'id': 'product.id', 'name': 'product.name'},
            'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
            'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
            'id': '2',
            'external_id': '2',
            'status': sub_status,
        },
    ])

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'params__value',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
                'action_if_multiple': 'use_most_actual',
                'parameter': {'id': 'PRD-123', 'name': 'param_a'},
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }

    response = await app.lookup_subscription(
        {
            'ColumnA': 'SubscriptionID',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'PREFIX.product.id': 'product.id',
        'PREFIX.product.name': 'product.name',
        'PREFIX.marketplace.id': 'marketplace.id',
        'PREFIX.marketplace.name': 'marketplace.name',
        'PREFIX.vendor.id': 'vendor.id',
        'PREFIX.vendor.name': 'vendor.name',
        'PREFIX.subscription.id': '2',
        'PREFIX.subscription.external_id': '2',
        'PREFIX.subscription.status': sub_status,
    }


@pytest.mark.asyncio
async def test_lookup_subscription_found_multiple_use_most_actual_all_terminated(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
):
    params = {'params.name': 'param_a', 'params.value': 'SubscriptionID'}

    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('subscriptions').assets.filter(
        **COMMON_FILTERS,
        **params,
    ).order_by('-events.created.at').mock(return_value=[
        {
            'product': {'id': 'product.id', 'name': 'product.name'},
            'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
            'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
            'id': '1',
            'external_id': '1',
            'status': 'terminated',
        },
        {
            'product': {'id': 'product.id', 'name': 'product.name'},
            'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
            'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
            'id': '2',
            'external_id': '2',
            'status': 'terminated',
        },
    ])

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'params__value',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
                'action_if_multiple': 'use_most_actual',
                'parameter': {'id': 'PRD-123', 'name': 'param_a'},
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }

    response = await app.lookup_subscription(
        {
            'ColumnA': 'SubscriptionID',
        },
    )
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'PREFIX.product.id': 'product.id',
        'PREFIX.product.name': 'product.name',
        'PREFIX.marketplace.id': 'marketplace.id',
        'PREFIX.marketplace.name': 'marketplace.name',
        'PREFIX.vendor.id': 'vendor.id',
        'PREFIX.vendor.name': 'vendor.name',
        'PREFIX.subscription.id': '1',
        'PREFIX.subscription.external_id': '1',
        'PREFIX.subscription.status': 'terminated',
    }


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
                'action_if_not_found': 'fail',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': True}],
            },
        },
    }
    response = await app.lookup_subscription({
        'ColumnA': None,
    })
    assert response.status == ResultType.SKIP


@pytest.mark.asyncio
async def test_lookup_subscription_params_value(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    params = {**COMMON_FILTERS, 'params.name': 'param_a', 'params.value': 'SubscriptionID'}
    client('subscriptions').assets.filter(
        **params,
    ).order_by('-events.created.at').mock(return_value=[{
        'product': {'id': 'product.id', 'name': 'product.name'},
        'marketplace': {'id': 'marketplace.id', 'name': 'marketplace.name'},
        'connection': {'vendor': {'id': 'vendor.id', 'name': 'vendor.name'}},
        'id': 'subscription.id',
        'external_id': 'subscription.external_id',
        'status': 'active',
    }])

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'lookup_type': 'params__value',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
                'parameter': {'id': 'PRD-123', 'name': 'param_a'},
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    response = await app.lookup_subscription({
        'ColumnA': 'SubscriptionID',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'PREFIX.product.id': 'product.id',
        'PREFIX.product.name': 'product.name',
        'PREFIX.marketplace.id': 'marketplace.id',
        'PREFIX.marketplace.name': 'marketplace.name',
        'PREFIX.vendor.id': 'vendor.id',
        'PREFIX.vendor.name': 'vendor.name',
        'PREFIX.subscription.id': 'subscription.id',
        'PREFIX.subscription.external_id': 'subscription.external_id',
        'PREFIX.subscription.status': 'active',
    }
