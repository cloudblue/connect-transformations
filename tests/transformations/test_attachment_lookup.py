# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest
from connect.eaas.core.enums import ResultType

from connect_transformations.transformations import StandardTransformationsApplication


@pytest.mark.asyncio
async def test_attachment_lookup(mocker, async_connect_client, httpx_mock):
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        httpx_mock.add_response(
            method='GET',
            url=f'{async_connect_client.endpoint}/path/to/input.xlsx',
            content=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/input.xlsx',
                'sheet': 'Data',
                'map_by': {
                    'input_column': 'id',
                    'attachment_column': 'id',
                },
                'mapping': [
                    {
                        'from': 'price',
                        'to': 'Subscription price',
                    },
                    {
                        'from': 'sub_id',
                        'to': 'Subscription ID',
                    },
                ],
            },
            'columns': {
                'input': [{'name': 'id', 'nullable': False}],
            },
        },
    }

    response = await app.attachment_lookup({'id': 3})
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Subscription price': 102.14,
        'Subscription ID': 'SUB-123-123-125',
    }


@pytest.mark.asyncio
async def test_attachment_lookup_no_sheet(mocker, async_connect_client, httpx_mock):
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        httpx_mock.add_response(
            method='GET',
            url=f'{async_connect_client.endpoint}/path/to/input.xlsx',
            content=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/input.xlsx',
                'map_by': {
                    'input_column': 'id',
                    'attachment_column': 'id',
                },
                'mapping': [
                    {
                        'from': 'price',
                        'to': 'Subscription price',
                    },
                    {
                        'from': 'sub_id',
                        'to': 'Subscription ID',
                    },
                ],
            },
            'columns': {
                'input': [{'name': 'id', 'nullable': False}],
            },
        },
    }

    response = await app.attachment_lookup({'id': 3})
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Subscription price': 102.14,
        'Subscription ID': 'SUB-123-123-125',
    }

    response = await app.attachment_lookup({'id': 4})
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Subscription price': 103.14,
        'Subscription ID': 'SUB-123-123-126',
    }


@pytest.mark.asyncio
async def test_attachment_lookup_api_error(mocker, async_connect_client, httpx_mock):
    httpx_mock.add_response(
        method='GET',
        url=f'{async_connect_client.endpoint}/path/to/input.xlsx',
        status_code=400,
    )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/input.xlsx',
                'sheet': 'Data',
                'map_by': {
                    'input_column': 'id',
                    'attachment_column': 'id',
                },
                'mapping': [
                    {
                        'from': 'price',
                        'to': 'Subscription price',
                    },
                    {
                        'from': 'sub_id',
                        'to': 'Subscription ID',
                    },
                ],
            },
            'columns': {
                'input': [{'name': 'id', 'nullable': False}],
            },
        },
    }

    response = await app.attachment_lookup({'id': 3})
    assert response.status == ResultType.FAIL
    assert response.output == 'Error during downloading attachment: 400 Bad Request'


@pytest.mark.asyncio
async def test_attachment_lookup_invalid_sheet(mocker, async_connect_client, httpx_mock):
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        httpx_mock.add_response(
            method='GET',
            url=f'{async_connect_client.endpoint}/path/to/input.xlsx',
            content=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/input.xlsx',
                'sheet': 'Daaaata',
                'map_by': {
                    'input_column': 'id',
                    'attachment_column': 'id',
                },
                'mapping': [
                    {
                        'from': 'price',
                        'to': 'Subscription price',
                    },
                    {
                        'from': 'sub_id',
                        'to': 'Subscription ID',
                    },
                ],
            },
            'columns': {
                'input': [{'name': 'id', 'nullable': False}],
            },
        },
    }

    response = await app.attachment_lookup({'id': 3})
    assert response.status == ResultType.FAIL
    assert 'Worksheet Daaaata does not exist' in response.output


@pytest.mark.asyncio
async def test_attachment_lookup_empty(mocker, async_connect_client, httpx_mock):
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        httpx_mock.add_response(
            method='GET',
            url=f'{async_connect_client.endpoint}/path/to/input.xlsx',
            content=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/input.xlsx',
                'sheet': 'Data',
                'map_by': {
                    'input_column': 'id',
                    'attachment_column': 'id',
                },
                'mapping': [
                    {
                        'from': 'price',
                        'to': 'Subscription price',
                    },
                    {
                        'from': 'sub_id',
                        'to': 'Subscription ID',
                    },
                ],
            },
            'columns': {
                'input': [{'name': 'id', 'nullable': True}],
            },
        },
    }

    response = await app.attachment_lookup({'id': None})
    assert response.status == ResultType.SKIP


@pytest.mark.asyncio
async def test_attachment_lookup_map_not_found(mocker, async_connect_client, httpx_mock):
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        httpx_mock.add_response(
            method='GET',
            url=f'{async_connect_client.endpoint}/path/to/input.xlsx',
            content=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/input.xlsx',
                'sheet': 'Data',
                'map_by': {
                    'input_column': 'id',
                    'attachment_column': 'id',
                },
                'mapping': [
                    {
                        'from': 'price',
                        'to': 'Subscription price',
                    },
                    {
                        'from': 'sub_id',
                        'to': 'Subscription ID',
                    },
                ],
            },
            'columns': {
                'input': [{'name': 'id', 'nullable': True}],
            },
        },
    }

    response = await app.attachment_lookup({'id': 177})
    assert response.status == ResultType.SKIP


@pytest.mark.asyncio
async def test_attachment_lookup_map_invalid_attachment_colums(
    mocker,
    async_connect_client,
    httpx_mock,
):
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        httpx_mock.add_response(
            method='GET',
            url=f'{async_connect_client.endpoint}/path/to/input.xlsx',
            content=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = async_connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/input.xlsx',
                'sheet': 'Data',
                'map_by': {
                    'input_column': 'id',
                    'attachment_column': 'id',
                },
                'mapping': [
                    {
                        'from': 'price',
                        'to': 'Subscription price',
                    },
                    {
                        'from': 'sub_idd',
                        'to': 'Subscription ID',
                    },
                ],
            },
            'columns': {
                'input': [{'name': 'id', 'nullable': True}],
            },
        },
    }

    response = await app.attachment_lookup({'id': 1})
    assert response.status == ResultType.FAIL
    assert response.output == "Invalid column: 'sub_idd'"
