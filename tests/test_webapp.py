# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.webapp import TransformationsWebApplication


def test_validate_transform_1_copy_row(test_client_factory):
    data = {
        'settings': [
            {
                'from': 'columnInput1',
                'to': 'newColumn1',
            },
            {
                'from': 'columnInput2',
                'to': 'newColumn2',
            },
        ],
        'columns': {
            'input': [
                {'name': 'columnInput1'},
                {'name': 'columnInput2'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/transform_1_copy_row', json=data)
    print(response.json())
    assert response.status_code == 200

    data = response.json()
    assert data == {
        'overview': 'columnInput1  -->  newColumn1\ncolumnInput2  -->  newColumn2\n',
    }


@pytest.mark.parametrize(
    'data',
    (
        {},
        {'settings': {}},
        {'settings': []},
        {'settings': [], 'columns': {}},
    ),
)
def test_validate_transform_1_copy_row_missing_settings_or_invalid(test_client_factory, data):

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/transform_1_copy_row', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid input data'}


def test_validate_transform_1_copy_row_invalid_settings(test_client_factory):
    data = {'settings': [{'x': 'y'}], 'columns': {'input': []}}

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/transform_1_copy_row', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid settings format'}


def test_validate_transform_1_copy_row_invalid_from(test_client_factory):
    data = {'settings': [{'from': 'Hola', 'to': 'Hola2'}], 'columns': {'input': [{'name': 'Gola'}]}}

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/transform_1_copy_row', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': 'The input column Hola does not exists'}


@pytest.mark.parametrize(
    'data',
    (
        {
            'settings': [
                {'from': 'A', 'to': 'C'},
                {'from': 'B', 'to': 'C'},
            ],
            'columns': {
                'input': [
                    {'name': 'A'},
                    {'name': 'B'},
                ],
            },
        },
        {
            'settings': [
                {'from': 'A', 'to': 'C'},
            ],
            'columns': {
                'input': [
                    {'name': 'A'},
                    {'name': 'C'},
                ],
            },
        },
    ),
)
def test_validate_transform_1_copy_row_not_unique_name(test_client_factory, data):
    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/transform_1_copy_row', json=data)
    assert response.status_code == 400
    assert response.json() == {
        'error': 'Invalid column name C. The to field should be unique',
    }
