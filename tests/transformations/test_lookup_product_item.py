# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest
from connect.eaas.core.enums import ResultType

from connect_transformations.transformations import StandardTransformationsApplication


@pytest.mark.asyncio
async def test_lookup_product_item(mocker, async_connect_client, async_client_mocker_factory):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-000-000-001'].get(return_value={
        'id': 'PRD-000-000-001',
        'name': 'Google Apps',
    })
    client.products['PRD-000-000-001'].items['PRD-000-000-001-0001'].get(return_value={
        'id': 'PRD-000-000-001-0001',
        'name': 'Prd 000 000 001 0001',
        'unit': {"name": "Gb"},
        'period': 'monthly',
        'mpn': 'MPN-A',
    })

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
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
    response = await app.lookup_product_items({
        'ColumnA': 'PRD-000-000-001-0001',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'PREFIX.product.id': 'PRD-000-000-001',
        'PREFIX.product.name': 'Google Apps',
        'PREFIX.item.id': 'PRD-000-000-001-0001',
        'PREFIX.item.name': 'Prd 000 000 001 0001',
        'PREFIX.item.unit': 'Gb',
        'PREFIX.item.period': 'monthly',
        'PREFIX.item.mpn': 'MPN-A',
    }


@pytest.mark.asyncio
async def test_lookup_product_item_cached(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
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
    app._cache['PRD-000-000-001-id-PRD-000-000-001-0001'] = {
        'product': {'id': 'PRD-000-000-001', 'name': 'Google Apps'},
        'id': 'PRD-000-000-001-0001',
        'name': 'Prd 000 000 001 0001',
        'unit': {"name": "Gb"},
        'period': 'monthly',
        'mpn': 'MPN-A',
    }
    app._cache['PRD-000-000-001'] = {
        'id': 'PRD-000-000-001', 'name': 'Google Apps',
    }
    response = await app.lookup_product_items({
        'ColumnA': 'PRD-000-000-001-0001',
    })

    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'PREFIX.product.id': 'PRD-000-000-001',
        'PREFIX.product.name': 'Google Apps',
        'PREFIX.item.id': 'PRD-000-000-001-0001',
        'PREFIX.item.name': 'Prd 000 000 001 0001',
        'PREFIX.item.unit': 'Gb',
        'PREFIX.item.period': 'monthly',
        'PREFIX.item.mpn': 'MPN-A',
    }


@pytest.mark.asyncio
async def test_lookup_product_item_unknown_lookup(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
                'lookup_type': 'unknown',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    app._cache['PRD-000-000-001'] = {
        'id': 'PRD-000-000-001', 'name': 'Google Apps',
    }
    response = await app.lookup_product_items({
        'ColumnA': 'PRD-000-000-001-0001',
    })
    assert response.status == ResultType.FAIL
    assert response.output == 'Unknown lookup type'
    assert response.transformed_row is None


@pytest.mark.asyncio
async def test_lookup_product_item_by_mpn(
        mocker,
        async_connect_client,
        async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-000-000-001'].get(return_value={
        'id': 'PRD-000-000-001',
        'name': 'Google Apps',
    })
    client.products['PRD-000-000-001'].items.filter(
        "eq(mpn,MPN-A)",
    ).count(return_value=1)

    client.products['PRD-000-000-001'].items.filter(
        "eq(mpn,MPN-A)",
    ).first().mock(return_value=[{
        'id': 'PRD-000-000-001-0001',
        'name': 'Prd 000 000 001 0001',
        'unit': {"name": "Gb"},
        'period': 'monthly',
        'mpn': 'MPN-A',
    }])

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
                'lookup_type': 'mpn',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    response = await app.lookup_product_items({
        'ColumnA': 'MPN-A',
    })

    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'PREFIX.product.id': 'PRD-000-000-001',
        'PREFIX.product.name': 'Google Apps',
        'PREFIX.item.id': 'PRD-000-000-001-0001',
        'PREFIX.item.name': 'Prd 000 000 001 0001',
        'PREFIX.item.unit': 'Gb',
        'PREFIX.item.period': 'monthly',
        'PREFIX.item.mpn': 'MPN-A',
    }


@pytest.mark.asyncio
async def test_lookup_product_item_by_mpn_empty(
        mocker,
        async_connect_client,
        async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-000-000-001'].get(return_value={
        'id': 'PRD-000-000-001',
        'name': 'Google Apps',
    })
    client.products['PRD-000-000-001'].items.filter("eq(mpn,MPN-A)").count(return_value=0)

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
                'lookup_type': 'mpn',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    response = await app.lookup_product_items({
        'ColumnA': 'MPN-A',
    })
    assert response.status == ResultType.SKIP
    assert response.transformed_row is None
    assert response.output is None


@pytest.mark.asyncio
async def test_lookup_product_item_by_mpn_empty_forced(
        mocker,
        async_connect_client,
        async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-000-000-001'].get(return_value={
        'id': 'PRD-000-000-001',
        'name': 'Google Apps',
    })
    client.products['PRD-000-000-001'].items.filter("eq(mpn,MPN-A)").count(return_value=0)

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
                'lookup_type': 'mpn',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'fail',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    response = await app.lookup_product_items({
        'ColumnA': 'MPN-A',
    })
    assert response.status == ResultType.FAIL
    assert response.transformed_row is None
    assert response.output == 'Product not found'


@pytest.mark.asyncio
async def test_lookup_product_item_by_mpn_too_much(
        mocker,
        async_connect_client,
        async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-000-000-001'].get(return_value={
        'id': 'PRD-000-000-001',
        'name': 'Google Apps',
    })
    client.products['PRD-000-000-001'].items.filter("eq(mpn,MPN-A)").count(return_value=2)

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
                'lookup_type': 'mpn',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'fail',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    response = await app.lookup_product_items({
        'ColumnA': 'MPN-A',
    })
    assert response.status == ResultType.FAIL
    assert response.transformed_row is None
    assert response.output == 'Multiple results found for the filter: MPN-A'


@pytest.mark.asyncio
async def test_lookup_product_item_skip_on_nullable(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
                'lookup_type': 'id',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': True}],
            },
        },
    }
    response = await app.lookup_product_items({
        'ColumnA': None,
    })
    assert response.status == ResultType.SKIP
    assert response.transformed_row is None


@pytest.mark.asyncio
async def test_lookup_product_item_no_product_and_skip(
        mocker,
        async_connect_client,
        async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-000-000-001'].get(status_code=404)

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
                'lookup_type': 'mpn',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'leave_empty',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    response = await app.lookup_product_items({
        'ColumnA': 'MPN-A',
    })
    assert response.status == ResultType.SKIP
    assert response.transformed_row is None
    assert response.output is None


@pytest.mark.asyncio
async def test_lookup_product_item_no_product_and_no_skip(
        mocker,
        async_connect_client,
        async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-000-000-001'].get(status_code=404)

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
                'lookup_type': 'mpn',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'fail',
            },
            'columns': {
                'input': [{'name': 'ColumnA', 'nullable': False}],
            },
        },
    }
    response = await app.lookup_product_items({
        'ColumnA': 'MPN-A',
    })
    assert response.status == ResultType.FAIL
    assert response.transformed_row is None
    assert response.output == 'Product not found'


@pytest.mark.asyncio
async def test_lookup_product_item_no_product_and_no_skip_search_by_id(
        mocker,
        async_connect_client,
        async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-000-000-001'].get(return_value={
        'id': 'PRD-000-000-001',
        'name': 'Google Apps',
    })
    client.products['PRD-000-000-001'].items['PRD-000-000-001-0001'].get(
        status_code=404,
    )
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': 'PRD-000-000-001',
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
    response = await app.lookup_product_items({
        'ColumnA': 'PRD-000-000-001-0001',
    })
    assert response.status == ResultType.FAIL
    assert response.transformed_row is None
    assert response.output == 'Product not found'


@pytest.mark.asyncio
async def test_lookup_product_item_product_column(
        mocker,
        async_connect_client,
        async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-000-000-001'].get(return_value={
        'id': 'PRD-000-000-001',
        'name': 'Google Apps',
    })
    client.products['PRD-000-000-001'].items['PRD-000-000-001-0001'].get(return_value={
        'id': 'PRD-000-000-001-0001',
        'name': 'Prd 000 000 001 0001',
        'unit': {"name": "Gb"},
        'period': 'monthly',
        'mpn': 'MPN-A',
    })
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'product_id': '',
                'product_column': 'Product ID',
                'lookup_type': 'id',
                'from': 'ColumnA',
                'prefix': 'PREFIX',
                'action_if_not_found': 'fail',
                'product_lookup_mode': 'column',
            },
            'columns': {
                'input': [
                    {'name': 'ColumnA', 'nullable': False},
                    {'name': 'Product ID', 'nullable': False},
                ],
            },
        },
    }
    response = await app.lookup_product_items({
        'ColumnA': 'PRD-000-000-001-0001',
        'Product ID': 'PRD-000-000-001',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'PREFIX.product.id': 'PRD-000-000-001',
        'PREFIX.product.name': 'Google Apps',
        'PREFIX.item.id': 'PRD-000-000-001-0001',
        'PREFIX.item.name': 'Prd 000 000 001 0001',
        'PREFIX.item.unit': 'Gb',
        'PREFIX.item.period': 'monthly',
        'PREFIX.item.mpn': 'MPN-A',
    }
    assert response.output is None
