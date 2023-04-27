# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest
from connect.eaas.core.enums import ResultType

from connect_transformations.transformations import StandardTransformationsApplication


@pytest.mark.asyncio
async def test_airtable_lookup(mocker, httpx_mock):
    params = 'filterByFormula=customer_id=1&maxRecords=2'
    httpx_mock.add_response(
        method='GET',
        url=f'https://api.airtable.com/v0/base_id/table_id?{params}',
        json={
            'records': [
                {
                    'id': 'some_id',
                    'createdTime': '2023-01-01T00:0:00.000Z',
                    'fields': {
                        'customer_id': '1',
                        'first name': 'First Name',
                        'last name': 'Last Name',
                    },
                },
            ],
        },
    )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'api_key': 'token',
                'base_id': 'base_id',
                'table_id': 'table_id',
                'map_by': {
                    'input_column': 'id',
                    'airtable_column': 'customer_id',
                },
                'mapping': [
                    {
                        'from': 'first name',
                        'to': 'Customer first name',
                    },
                    {
                        'from': 'last name',
                        'to': 'Customer last name',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'id', 'nullable': False},
                ],
            },
        },
    }

    response = await app.airtable_lookup({'id': 1})
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Customer first name': 'First Name',
        'Customer last name': 'Last Name',
    }


@pytest.mark.asyncio
async def test_airtable_lookup_skip_nullable(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'api_key': 'token',
                'base_id': 'base_id',
                'table_id': 'table_id',
                'map_by': {
                    'input_column': 'purchase_id',
                    'airtable_column': 'id',
                },
                'mapping': [
                    {
                        'from': 'created',
                        'to': 'Purchase date',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'purchase_id', 'nullable': True},
                ],
            },
        },
    }

    response = await app.airtable_lookup({'purchase_id': None})
    assert response.status == ResultType.SKIP


@pytest.mark.asyncio
async def test_airtable_lookup_no_matching_query(mocker, httpx_mock):
    params = 'filterByFormula=customer_id=1&maxRecords=2'
    httpx_mock.add_response(
        method='GET',
        url=f'https://api.airtable.com/v0/base_id/table_id?{params}',
        json={
            'records': [],
        },
    )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'api_key': 'token',
                'base_id': 'base_id',
                'table_id': 'table_id',
                'map_by': {
                    'input_column': 'id',
                    'airtable_column': 'customer_id',
                },
                'mapping': [
                    {
                        'from': 'first_name',
                        'to': 'Customer first name',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'id', 'nullable': False},
                ],
            },
        },
    }

    response = await app.airtable_lookup({'id': 1})
    assert response.status == ResultType.SKIP


@pytest.mark.asyncio
async def test_airtable_lookup_airtable_api_error(mocker, httpx_mock):
    params = 'filterByFormula=customer_id=1&maxRecords=2'
    httpx_mock.add_response(
        method='GET',
        url=f'https://api.airtable.com/v0/base_id/table_id?{params}',
        status_code=400,
    )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'api_key': 'token',
                'base_id': 'base_id',
                'table_id': 'table_id',
                'map_by': {
                    'input_column': 'id',
                    'airtable_column': 'customer_id',
                },
                'mapping': [
                    {
                        'from': 'first_name',
                        'to': 'First name',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'id', 'nullable': False},
                ],
            },
        },
    }

    response = await app.airtable_lookup({'id': 1})
    assert response.status == ResultType.FAIL
    assert 'Error calling `base_id/table_id`' in response.output


@pytest.mark.asyncio
async def test_airtable_lookup_corrupted_airtable_row(mocker, httpx_mock):
    params = 'filterByFormula=customer_id=1&maxRecords=2'
    httpx_mock.add_response(
        method='GET',
        url=f'https://api.airtable.com/v0/base_id/table_id?{params}',
        json={
            'records': [
                {
                    'id': 'some_id',
                    'createdTime': '2023-01-01T00:0:00.000Z',
                    'fields': {
                        'customer_id': '1',
                        'first name': 'First Name',
                    },
                },
            ],
        },
    )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'api_key': 'token',
                'base_id': 'base_id',
                'table_id': 'table_id',
                'map_by': {
                    'input_column': 'id',
                    'airtable_column': 'customer_id',
                },
                'mapping': [
                    {
                        'from': 'first_name',
                        'to': 'Customer first name',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'id', 'nullable': False},
                ],
            },
        },
    }

    response = await app.airtable_lookup({'id': 1})
    assert response.status == ResultType.FAIL
    assert "Error extracting data: 'first_name'" in response.output
