# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.constants import SUBSCRIPTION_LOOKUP
from connect_transformations.webapp import TransformationsWebApplication


def test_validate_copy_columns(test_client_factory):
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

    response = client.post('/api/validate/copy_columns', json=data)
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
def test_validate_copy_columns_missing_settings_or_invalid(test_client_factory, data):

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/copy_columns', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid input data'}


def test_validate_copy_columns_invalid_settings(test_client_factory):
    data = {'settings': [{'x': 'y'}], 'columns': {'input': []}}

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/copy_columns', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid settings format'}


def test_validate_copy_columns_invalid_from(test_client_factory):
    data = {'settings': [{'from': 'Hola', 'to': 'Hola2'}], 'columns': {'input': [{'name': 'Gola'}]}}

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/copy_columns', json=data)
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
def test_validate_copy_columns_not_unique_name(test_client_factory, data):
    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/copy_columns', json=data)
    assert response.status_code == 400
    assert response.json() == {
        'error': 'Invalid column name C. The to field should be unique',
    }


def test_validate_invalid_transformation(test_client_factory):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/invalid_transformation_function', json={})
    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The validation method invalid_transformation_function does not exist',
    }


def test_validate_lookup_subscription(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': 'Criteria = "id"\nInput Column = "column"\nPrefix = "PREFIX"\n',
    }


@pytest.mark.parametrize(
    'data',
    (
        {},
        {'settings': []},
        {'settings': [], 'columns': {}},
    ),
)
def test_validate_lookup_subscription_settings_or_invalid(test_client_factory, data):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Invalid input data',
    }


@pytest.mark.parametrize(
    'settings',
    (
        {},
        {'from': 'x'},
        {'from': 'x', 'prefix': ''},
        {'lookup_type': 'x', 'prefix': ''},
    ),
)
def test_validate_lookup_subscription_invalid_format(test_client_factory, settings):
    data = {'settings': settings, 'columns': {'input': []}}
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The settings must have `lookup_type`, `from` and `prefix` fields',
    }


@pytest.mark.parametrize(
    'lookup_type',
    (
        'invalidtype',
        '',
    ),
)
def test_validate_lookup_subscription_invalid_lookup_type(test_client_factory, lookup_type):
    data = {
        'settings': {
            'lookup_type': lookup_type,
            'from': 'column',
            'prefix': 'PREFIX',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    values = SUBSCRIPTION_LOOKUP.keys()
    assert data == {
        'error': f'The settings `lookup_type` allowed values {values}',
    }


@pytest.mark.parametrize(
    'lookup_type',
    (
        'invalidtype',
        '',
    ),
)
def test_validate_lookup_subscription_invalid_column(test_client_factory, lookup_type):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
        },
        'columns': {
            'input': [
                {'name': 'otherColumn'},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings `from` contains an invalid column name column that does not exist'
            ' on columns.input'
        ),
    }


def test_validate_lookup_subscription_invalid_prefix(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': '12345678901',
        },
        'columns': {
            'input': [{'name': 'column'}],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The settings `prefix` max length is 10',
    }


def test_get_subscription_criteria(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/lookup_subscription/criteria')

    assert response.status_code == 200
    data = response.json()
    assert data == SUBSCRIPTION_LOOKUP
