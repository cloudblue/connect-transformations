# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.enums import ResultType

from connect_transformations.transformations import StandardTransformationsApplication


def test_attachment_lookup(mocker, connect_client, responses):
    connect_client.endpoint = 'https://cnct.example.org/public/v1'
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        responses.add(
            'GET',
            f'{connect_client.endpoint}/path/to/MFL-123-123',
            body=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/MFL-123-123',
                'sheet': 'Data',
                'map_by': [
                    {
                        'input_column': 'id',
                        'attachment_column': 'id',
                    },
                ],
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

    response = app.attachment_lookup({'id': 3})
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Subscription price': 102.14,
        'Subscription ID': 'SUB-123-123-125',
    }


def test_attachment_lookup_no_sheet(mocker, connect_client, responses):
    connect_client.endpoint = 'https://cnct.example.org/public/v1'
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        responses.add(
            'GET',
            f'{connect_client.endpoint}/path/to/MFL-123-123',
            body=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/MFL-123-123',
                'map_by': [
                    {
                        'input_column': 'id',
                        'attachment_column': 'id',
                    },
                ],
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

    response = app.attachment_lookup({'id': 3})
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Subscription price': 102.14,
        'Subscription ID': 'SUB-123-123-125',
    }

    response = app.attachment_lookup({'id': 4})
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Subscription price': 103.14,
        'Subscription ID': 'SUB-123-123-126',
    }


def test_attachment_lookup_api_error(mocker, connect_client, responses):
    connect_client.endpoint = 'https://cnct.example.org/public/v1'
    responses.add(
        'GET',
        f'{connect_client.endpoint}/path/to/MFL-123-123',
        status=400,
    )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/MFL-123-123',
                'sheet': 'Data',
                'map_by': [
                    {
                        'input_column': 'id',
                        'attachment_column': 'id',
                    },
                ],
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

    response = app.attachment_lookup({'id': 3})
    assert response.status == ResultType.FAIL
    assert response.output == 'Error during downloading attachment: 400 Bad Request'


def test_attachment_lookup_invalid_sheet(mocker, connect_client, responses):
    connect_client.endpoint = 'https://cnct.example.org/public/v1'
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        responses.add(
            'GET',
            f'{connect_client.endpoint}/path/to/MFL-123-123',
            body=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/MFL-123-123',
                'sheet': 'Daaaata',
                'map_by': [
                    {
                        'input_column': 'id',
                        'attachment_column': 'id',
                    },
                ],
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

    response = app.attachment_lookup({'id': 3})
    assert response.status == ResultType.FAIL
    assert 'Worksheet Daaaata does not exist' in response.output


def test_attachment_lookup_empty(mocker, connect_client, responses):
    connect_client.endpoint = 'https://cnct.example.org/public/v1'
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        responses.add(
            'GET',
            f'{connect_client.endpoint}/path/to/MFL-123-123',
            body=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/MFL-123-123',
                'sheet': 'Data',
                'map_by': [
                    {
                        'input_column': 'id',
                        'attachment_column': 'id',
                    },
                ],
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

    response = app.attachment_lookup({'id': None})
    assert response.status == ResultType.SKIP


def test_attachment_lookup_map_not_found(mocker, connect_client, responses):
    connect_client.endpoint = 'https://cnct.example.org/public/v1'
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        responses.add(
            'GET',
            f'{connect_client.endpoint}/path/to/MFL-123-123',
            body=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/MFL-123-123',
                'sheet': 'Data',
                'map_by': [
                    {
                        'input_column': 'id',
                        'attachment_column': 'id',
                    },
                ],
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

    response = app.attachment_lookup({'id': 177})
    assert response.status == ResultType.SKIP


def test_attachment_lookup_map_invalid_attachment_columns(
    mocker,
    connect_client,
    responses,
):
    connect_client.endpoint = 'https://cnct.example.org/public/v1'
    with open('tests/test_data/input_file_example.xlsx', 'rb') as input_file:
        responses.add(
            'GET',
            f'{connect_client.endpoint}/path/to/MFL-123-123',
            body=input_file.read(),
        )

    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.installation_client = connect_client
    app.transformation_request = {
        'transformation': {
            'settings': {
                'file': '/path/to/MFL-123-123',
                'sheet': 'Data',
                'map_by': [
                    {
                        'input_column': 'id',
                        'attachment_column': 'id',
                    },
                ],
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

    response = app.attachment_lookup({'id': 1})
    assert response.status == ResultType.FAIL
    assert response.output == "Invalid column: 'sub_idd'"
