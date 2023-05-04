# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.webapp import TransformationsWebApplication


def test_validate_filter_row(test_client_factory):
    data = {
        'settings': {
            'from': 'columnInput1',
            'value': 'somevalue',
            'match_condition': True,
            'additional_values': [
                {
                    'operation': 'or',
                    'value': 'another_value',
                },
            ],
        },
        'columns': {
            'input': [
                {'name': 'columnInput1'},
            ],
            'output': [
                {'name': 'somevalue_INSTRUCTIONS'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/filter_row', json=data)
    assert response.status_code == 200

    data = response.json()
    assert data == {
        'overview': (
            'We Keep Row If Value of column "columnInput1" == "somevalue" OR "another_value"'
        ),
    }


@pytest.mark.parametrize(
    'data',
    (
        {},
        {'settings': []},
        {'settings': [], 'columns': {}},
    ),
)
def test_validate_filter_row_invalid_input(test_client_factory, data):

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/filter_row', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': 'Invalid input data'}


@pytest.mark.parametrize(
    'settings',
    (
        {},
        {'settings': {'from': None}},
        {'settings': {'from': ''}},
        {'settings': {'from': 'Hola'}},
        {'settings': {'from': 'Hola', 'value': None}},
        {'settings': {'from': 'Hola', 'value': 22}},
        {'settings': {'from': 'Hola', 'value': 2.2}},
        {'settings': {'from': 'Hola', 'value': 2.2, 'match_condition': '1'}},
        {'settings': {'from': 'Hola', 'value': 2.2, 'match_condition': False}},
        {'settings': {
            'from': 'Hola',
            'value': 2.2,
            'match_condition': True,
            'additional_value': {},
        }},
    ),
)
def test_validate_filter_row_invalid_format(test_client_factory, settings):
    data = {
        'settings': settings,
        'columns': {
            'input': [
                {'name': 'Hola'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/filter_row', json=data)
    assert response.status_code == 400
    assert response.json() == {'error': (
        'The settings must have `from`, `value`, boolean `match_condition` '
        'and list `additional_values` fields'
    )}


def test_validate_filter_row_invalid_column(test_client_factory):
    data = {
        'settings': {
            'from': 'columnInput1',
            'value': 'somevalue',
            'match_condition': True,
            'additional_values': [],
        },
        'columns': {
            'input': [
                {'name': 'otherColumn'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/filter_row', json=data)
    assert response.status_code == 400
    assert response.json() == {
        'error': 'The settings must have a valid `from` column name',
    }


def test_validate_filter_row_invalid_additional_value(test_client_factory):
    data = {
        'settings': {
            'from': 'columnInput1',
            'value': 'somevalue',
            'match_condition': True,
            'additional_values': [
                {'operation': 'xor', 'value': '123'},
            ],
        },
        'columns': {
            'input': [
                {'name': 'otherColumn'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)

    response = client.post('/api/validate/filter_row', json=data)
    assert response.status_code == 400
    assert response.json() == {
        'error': 'The settings must have a valid `from` column name',
    }
