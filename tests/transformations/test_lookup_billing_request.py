# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest
from connect.eaas.core.enums import ResultType

from connect_transformations.transformations import StandardTransformationsApplication


@pytest.mark.asyncio
async def test_lookup_billing_request_full(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)

    client.requests.filter(
        **{
            'status': 'approved',
            'asset.id': 'AS-12311',
            'asset.params.id': 'param_name',
            'asset.params.value': 'ParamValue',
            'updated__lt': '2022-01-31T23:59:59',
        },
    ).select(
        '-activation_key',
        '-template',
    ).order_by('-updated').first().mock(return_value=[
        {
            'id': 'PR-123-123',
            'asset': {
                'id': 'AS-12311',
                'params': [{
                    'name': 'param_name',
                    'value': 'ParamValue',
                }],
                'items': [
                    {'id': 'i1', 'mpn': 'm1', 'quantity': 12, 'old_quantity': 10},
                ],
            },
            'updated': '2022-01-31T23:59:59',
        },
    ])

    client('subscriptions').requests.filter(
        **{
            'asset.id': 'AS-12311',
            'asset.params.id': 'param_name',
            'asset.params.value': 'ParamValue',
            'events.created.at__lt': '2022-01-31T23:59:59',
            'events.created.at__gt': '2022-01-31T23:59:59',
        },
    ).order_by('events.created.at').first().mock(return_value=[
        {
            'id': 'BR-123-123',
            'asset': {
                'id': 'AS-12311',
                'params': [{
                    'name': 'param_name',
                    'value': 'ParamValue',
                }],
            },
            'items': [
                {'id': 'i1', 'mpn': 'm1', 'quantity': 12},
            ],
            'events': {'created': {'at': '2022-01-31T23:59:59'}},
        },
    ])

    client.requests.filter(
        **{
            'status': 'approved',
            'updated__lt': '2022-01-31T23:59:59',
            'updated__gt': '2022-01-31T23:59:59',
        },
    ).count(return_value=1)

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'batch': {
            'context': {
                'period': {
                    'start': '2022-01-01T00:00:00',
                    'end': '2022-01-31T23:59:59',
                },
            },
        },
        'transformation': {
            'settings': {
                "item": {
                    "id": "mpn",
                    "name": "Item MPN",
                },
                "parameter": {
                    "id": "PRM-000-048-001-0003",
                    "name": "param_name",
                },
                "asset_type": "id",
                "asset_column": "AssetID",
                "item_column": "ItemMPN",
                "output_config": {
                    "A": {
                        "attribute": "asset.parameter.value",
                        "parameter_name": "param_name",
                    },
                    "Quantity": {
                        "attribute": "items.quantity",
                    },
                },
                "parameter_column": "ParamName",
                "action_if_multiple": "fail",
                "action_if_not_found": "fail",
            },
            'columns': {
                'input': [
                    {'name': 'AssetID', 'nullable': False},
                    {'name': 'ParamName', 'nullable': False},
                    {'name': 'ItemMPN', 'nullable': False},
                ],
                'output': [
                    {'name': 'A'},
                ],
            },
        },
    }
    response = await app.lookup_billing_request({
        'AssetID': 'AS-12311',
        'ParamName': 'ParamValue',
        'ItemMPN': 'm1',
    })
    assert response.status == ResultType.SUCCESS, response.output
    assert response.transformed_row == {
        'A': 'ParamValue',
        'Quantity': '12',
    }


@pytest.mark.asyncio
async def test_lookup_billing_request_wo_asset(
    mocker,
    async_connect_client,
    async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)

    client.requests.filter(
        **{
            'status': 'approved',
            'asset.params.id': 'param_name',
            'asset.params.value': 'ParamValue',
            'updated__lt': '2022-01-31T23:59:59',
        },
    ).select(
        '-activation_key',
        '-template',
    ).order_by('-updated').first().mock(return_value=[
        {
            'id': 'PR-123-123',
            'asset': {
                'id': 'AS-12311',
                'params': [{
                    'name': 'param_name',
                    'value': 'ParamValue',
                }],
                'items': [
                    {'id': 'i1', 'mpn': 'm1', 'quantity': 11, 'old_quantity': 10},
                    {'id': 'i2', 'mpn': 'm2', 'quantity': 0, 'old_quantity': 0},
                    {'id': 'i3', 'mpn': 'm3', 'quantity': 12, 'old_quantity': 5},
                ],
            },
            'updated': '2022-01-31T23:59:59',
        },
    ])

    client('subscriptions').requests.filter(
        **{
            'asset.params.id': 'param_name',
            'asset.params.value': 'ParamValue',
            'events.created.at__lt': '2022-01-31T23:59:59',
            'events.created.at__gt': '2022-01-31T23:59:59',
        },
    ).order_by('events.created.at').first().mock(return_value=[
        {
            'id': 'BR-123-123',
            'asset': {
                'id': 'AS-12311',
                'params': [{
                    'name': 'param_name',
                    'value': 'ParamValue',
                }],
            },
            'items': [
                {'id': 'i1', 'mpn': 'm1', 'quantity': 11},
                {'id': 'i2', 'mpn': 'm2', 'quantity': 0},
                {'id': 'i3', 'mpn': 'm3', 'quantity': 12},
            ],
            'events': {'created': {'at': '2022-01-31T23:59:59'}},
        },
    ])

    client.requests.filter(
        status='approved',
        updated__lt='2022-01-31T23:59:59',
        updated__gt='2022-01-31T23:59:59',
    ).count(return_value=1)

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'batch': {
            'context': {
                'period': {
                    'start': '2022-01-01T00:00:00',
                    'end': '2022-01-31T23:59:59',
                },
            },
        },
        'transformation': {
            'settings': {
                "item": {
                    "id": "mpn",
                    "name": "Item MPN",
                },
                "parameter": {
                    "id": "PRM-000-048-001-0003",
                    "name": "param_name",
                },
                "asset_type": None,
                "asset_column": None,
                "item_column": "ItemMPN",
                "output_config": {
                    "A": {
                        "attribute": "asset.parameter.value",
                        "parameter_name": "param_name",
                    },
                    "Quantity": {
                        "attribute": "items.quantity",
                    },
                    "Old Quantity": {
                        "attribute": "items.old_quantity",
                    },
                },
                "parameter_column": "ParamName",
                "action_if_multiple": "fail",
                "action_if_not_found": "fail",
            },
            'columns': {
                'input': [
                    {'name': 'ParamName', 'nullable': False},
                    {'name': 'ItemMPN', 'nullable': False},
                ],
                'output': [
                    {'name': 'A'},
                ],
            },
        },
    }
    response = await app.lookup_billing_request({
        'ParamName': 'ParamValue',
        'ItemMPN': 'm3',
    })
    assert response.status == ResultType.SUCCESS, response.output
    assert response.transformed_row == {
        'A': 'ParamValue',
        'Quantity': '12',
        'Old Quantity': '5',
    }


@pytest.mark.asyncio
async def test_lookup_billing_request_null_value(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'parameter': {
                    'id': 'PRM-ID',
                    'name': 'param_a',
                },
                'parameter_column': 'Param A',
                'item': {
                    'id': 'all',
                    'name': 'All',
                },
                'item_column': None,
                'asset_type': None,
                'asset_column': None,
                'output_config': {
                    'billing_id': {'attribute': 'id'},
                },
                'action_if_multiple': 'use_most_actual',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'Param A', 'nullable': True}],
                'output': [{'name': 'billing_id'}],
            },
        },
    }
    response = await app.lookup_billing_request({
        'Param A': None,
    })
    assert response.status == ResultType.SKIP


@pytest.mark.asyncio
async def test_lookup_billing_request_not_found(
    mocker, async_connect_client, async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.requests.filter(
        **{
            'status': 'approved',
            'asset.params.id': 'param_a',
            'asset.params.value': 'PAR-111',
        },
    ).select(
        '-activation_key',
        '-template',
    ).order_by('-updated').first().mock(return_value=[])

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'batch': {'context': {}},
        'transformation': {
            'settings': {
                'parameter': {
                    'id': 'PAR-ID',
                    'name': 'param_a',
                },
                'parameter_column': 'Param A',
                'item': {
                    'id': 'all',
                    'name': 'All',
                },
                'item_column': None,
                'asset_type': None,
                'asset_column': None,
                'output_config': {
                    'billing_id': {'attribute': 'id'},
                },
                'action_if_multiple': 'use_most_actual',
                'action_if_not_found': 'fail',
            },
            'columns': {
                'input': [
                    {'name': 'Param A', 'nullable': False},
                ],
                'output': [
                    {'name': 'billing_id'},
                ],
            },
        },
    }
    response = await app.lookup_billing_request({
        'Param A': 'PAR-111',
    })
    assert response.status == ResultType.FAIL
    assert "No result found for the filter" in response.output
