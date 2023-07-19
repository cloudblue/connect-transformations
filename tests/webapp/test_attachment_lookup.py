# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.webapp import TransformationsWebApplication


@pytest.mark.asyncio
async def test_get_excel_attachments(
        test_client_factory,
        async_connect_client,
        async_client_mocker_factory,
):
    query = (
        "((ilike(mime_type,*vnd.openxmlformats-officedocument.spreadsheetml.sheet*)"
        "|ilike(mime_type,*vnd.ms-excel*));"
        "ilike(mime_type,*application*))"
    )

    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client('media')('folders').collection(
        'streams_attachments',
    )['stream_id'].files.filter(query).mock(return_value=[
        {
            'id': 'MFL-0001',
            'file': '/some/path/to/file.xlsx',
            'size': 5381,
            'folder': {
                'name': 'STR-001',
                'type': 'streams_attachments',
            },
            'owner': {},
            'name': 'file.xlsx',
            'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'events': {},
            'access': {},
        },
        {
            'id': 'MFL-0002',
            'file': '/another/path/to/file-002.xlsx',
            'size': 5840,
            'folder': {
                'name': 'STR-001',
                'type': 'streams_attachments',
            },
            'owner': {},
            'name': 'file-002.xlsx',
            'mime_type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'events': {},
            'access': {},
        },
    ])

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/attachment_lookup/stream_id')

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {
        'file': '/public/v1/media/folders/streams_attachments/stream_id/files/MFL-0001',
        'id': 'MFL-0001',
        'name': 'file.xlsx',
    } in data, data
    assert {
        'id': 'MFL-0002',
        'file': '/public/v1/media/folders/streams_attachments/stream_id/files/MFL-0002',
        'name': 'file-002.xlsx',
    } in data, data


def test_validate_attachment_lookup_invalid_data(test_client_factory):
    data = {
        'settings': {
            'file': '/path/to/file.xlsx',
            'sheet': 'Data',
            'map_by': {
                'input_column': 'id',
                'attachment_column': 'customer_id',
            },
            'mapping': [
                {
                    'from': 'sub_id',
                    'to': 'Subscription',
                },
                {
                    'from': 'purchase_time',
                    'to': 'Purchase time',
                },
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/attachment_lookup/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == 'Invalid input data'


def test_validate_attachment_lookup_invalid_settings(test_client_factory):
    data = {
        'settings': {
            'sheet': 'Data',
            'map_by': {
                'input_column': 'id',
                'attachment_column': 'customer_id',
            },
            'mapping': [
                {
                    'from': 'sub_id',
                    'to': 'Subscription',
                },
                {
                    'from': 'purchase_time',
                    'to': 'Purchase time',
                },
            ],
        },
        'columns': {
            'input': [{'name': 'id'}],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/attachment_lookup/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == (
        'The settings must contain `file` and optional `sheet` '
        'fields and dictionary `map_by` and list `mapping` fields.'
    )


def test_validate_attachment_lookup_invalid_map_by(test_client_factory):
    data = {
        'settings': {
            'file': '/path/to/file.xlsx',
            'sheet': 'Data',
            'map_by': {
                'from': 'id',
                'to': 'customer_id',
            },
            'mapping': [
                {
                    'from': 'sub_id',
                    'to': 'Subscription',
                },
                {
                    'from': 'purchase_time',
                    'to': 'Purchase time',
                },
            ],
        },
        'columns': {
            'input': [{'name': 'id'}],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/attachment_lookup/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == (
        'The settings field `map_by` must contain '
        '`input_column` and `attachment_column` fields in it.'
    )


def test_validate_attachment_lookup_invalid_mapping(test_client_factory):
    data = {
        'settings': {
            'file': '/path/to/file.xlsx',
            'sheet': 'Data',
            'map_by': {
                'input_column': 'id',
                'attachment_column': 'customer_id',
            },
            'mapping': [
                {
                    'from': 'sub_id',
                    'to': 'Subscription',
                },
                {
                    'input_column': 'purchase_time',
                    'output_column': 'Purchase time',
                },
            ],
        },
        'columns': {
            'input': [{'name': 'id'}],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/attachment_lookup/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == (
        'Each element of the settings `mapping` must contain '
        '`from` and `to` fields in it.'
    )


def test_validate_attachment_lookup_not_existing_column(test_client_factory):
    data = {
        'settings': {
            'file': '/path/to/file.xlsx',
            'sheet': 'Data',
            'map_by': {
                'input_column': 'idd',
                'attachment_column': 'customer_id',
            },
            'mapping': [
                {
                    'from': 'sub_id',
                    'to': 'Subscription',
                },
                {
                    'from': 'purchase_time',
                    'to': 'Purchase time',
                },
            ],
        },
        'columns': {
            'input': [{'name': 'id'}],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/attachment_lookup/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data['error'] == (
        'The settings contains invalid input column that '
        'does not exist on columns.input'
    )


def test_validate_attachment_lookup_ok(test_client_factory):
    data = {
        'settings': {
            'file': '/path/to/file.xlsx',
            'sheet': 'Data',
            'map_by': {
                'input_column': 'id',
                'attachment_column': 'customer_id',
            },
            'mapping': [
                {
                    'from': 'sub_id',
                    'to': 'Subscription',
                },
                {
                    'from': 'purchase_time',
                    'to': 'Purchase time',
                },
            ],
        },
        'columns': {
            'input': [{'name': 'id'}],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/attachment_lookup/validate', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data['overview'] == (
        'Match column "id" with Attachment field "customer_id" and populate '
        '2 columns with the matching data.'
    )
