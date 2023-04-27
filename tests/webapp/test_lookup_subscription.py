# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.constants import SUBSCRIPTION_LOOKUP
from connect_transformations.webapp import TransformationsWebApplication


def test_validate_lookup_subscription(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
            'action_if_not_found': 'fail',
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
        'overview': (

            'Criteria = "CloudBlue Subscription ID"\nPrefix = "PREFIX"\nIf not found = Fail\n'
        ),
    }


def test_validate_lookup_subscription_external_id(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'external_id',
            'from': 'column',
            'prefix': 'PREFIX',
            'action_if_not_found': 'leave_empty',
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
        'overview': (
            'Criteria = "CloudBlue Subscription External ID"\nPrefix = "PREFIX"\n'
            'If not found = Leave Empty\n'
        ),
    }


def test_validate_lookup_subscription_with_params_value(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'params__value',
            'from': 'column',
            'prefix': 'PREFIX',
            'action_if_not_found': 'leave_empty',
            'parameter': {'id': 'P-123', 'name': 'param_a'},
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
        'overview': (
            'Criteria = "Parameter Value"\nParameter Name = "param_a"\nPrefix = "PREFIX"\n'
            'If not found = Leave Empty\n'
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
        {'lookup_type': 'x'},
        {'lookup_type': 'x', 'from': 'x'},
        {'lookup_type': 'x', 'from': 'x', 'prefix': None},
        {'lookup_type': 'x', 'from': 'x', 'prefix': 3.33},
        {'lookup_type': 'x', 'from': 'x', 'prefix': 333},
        {'lookup_type': 'x', 'from': 'x', 'prefix': []},
        {'lookup_type': 'x', 'from': 'x', 'prefix': {}},
        {'lookup_type': 'x', 'from': 'x', 'prefix': ''},
        {'lookup_type': 'x', 'from': 'x', 'prefix': 'pref'},
    ),
)
def test_validate_lookup_subscription_invalid_format(test_client_factory, settings):
    data = {'settings': settings, 'columns': {'input': []}}
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings must have `lookup_type`, `from`, `prefix` and `action_if_not_found` '
            'fields'
        ),
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
            'action_if_not_found': 'fail',
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
    'action_if_not_found',
    (
        'invalidtype',
        '',
    ),
)
def test_validate_lookup_subscription_invalid_action_if_not_found(
    test_client_factory,
    action_if_not_found,
):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
            'action_if_not_found': action_if_not_found,
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
    values = ['leave_empty', 'fail']
    assert data == {
        'error': f'The settings `action_if_not_found` allowed values {values}',
    }


@pytest.mark.parametrize(
    'parameter',
    (
        None,
        {},
        {'id': 'id'},
        {'name': 'name'},
    ),
)
def test_validate_lookup_subscription_invalid_parameter(test_client_factory, parameter):
    data = {
        'settings': {
            'lookup_type': 'params__value',
            'from': 'column',
            'prefix': 'PREFIX',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }
    if parameter is not None:
        data['settings']['parameter'] = parameter
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_subscription', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings must have `parameter` with `id` and `name` if `lookup_type` is '
            'params__value'
        ),
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
            'action_if_not_found': 'leave_empty',
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
            'action_if_not_found': 'leave_empty',
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


@pytest.mark.asyncio
async def test_get_subscription_parameters(
    test_client_factory,
    async_connect_client,
    async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-123-123'].parameters.all().mock(return_value=[
        {'id': 'P-123', 'name': 'param_a'},
        {'id': 'P-321', 'name': 'param_b'},
    ])
    data = {
        'settings': {
            'lookup_type': 'params__value',
            'parameter': 'P-123',
            'from': 'column',
            'prefix': 'PREFIX',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/lookup_subscription/parameters?product_id=PRD-123-123')

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {'P-123': 'param_a'},
        {'P-321': 'param_b'},
    ]
