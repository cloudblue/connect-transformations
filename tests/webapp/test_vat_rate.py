# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.webapp import TransformationsWebApplication


def test_validate_vat_rate(test_client_factory):
    data = {
        'settings': {
            'from': 'column',
            'to': 'result',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [
                {'name': 'result'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/vat_rate', json=data)

    assert response.status_code == 200
    data = response.json()

    assert data == {
        'overview': (
            'What to do for non-EU country codes = Leave Empty' + '\n'
        ),
    }


@pytest.mark.parametrize(
    'data',
    (
        {},
        {'settings': []},
        {'settings': {}},
        {'settings': {}, 'columns': {}},
    ),
)
def test_validate_vat_rate_settings_or_invalid(test_client_factory, data):
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/vat_rate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Invalid input data',
    }


@pytest.mark.parametrize(
    'settings',
    (
        {},
        {'from': {}},
        {'from': {}, 'to': {}},
    ),
)
def test_validate_vat_rate_invalid_format(test_client_factory, settings):
    data = {'settings': settings, 'columns': {'input': []}}
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/vat_rate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings must have `from`, `to` and `action_if_not_found` '
            'fields'
        ),
    }


def test_validate_vat_rate_invalid_column(test_client_factory):
    data = {
        'settings': {
            'from': 'column',
            'to': 'columnB',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'otherColumn'},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/vat_rate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings contains an invalid `from` column name "column" that does not exist on'
            ' columns.input'
        ),
    }
