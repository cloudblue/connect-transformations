# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.lookup_subscription.utils import SUBSCRIPTION_LOOKUP
from connect_transformations.webapp import TransformationsWebApplication


def test_validate_lookup_subscription(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'action_if_not_found': 'fail',
            'action_if_multiple': 'fail',
            'output_config': {
                'Sub ID': {
                    'attribute': 'id',
                },
                'Param': {
                    'attribute': 'parameter.value',
                    'parameter': 'test',
                },
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [
                {
                    'name': 'Sub ID',
                },
                {
                    'name': 'Param',
                },
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_subscription/validate', json=data)

    assert response.status_code == 200, response.content
    data = response.json()
    assert data == {
        'overview': (
            'Criteria = "CloudBlue Subscription ID"\n'
            'If not found = Fail\n'
            'If multiple found = Fail\n'
        ),
    }


def test_validate_lookup_subscription_external_id(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'external_id',
            'from': 'column',
            'action_if_not_found': 'leave_empty',
            'action_if_multiple': 'use_most_actual',
            'output_config': {
                'A': {
                    'attribute': 'id',
                },
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [
                {
                    'name': 'A',
                },
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_subscription/validate', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': (
            'Criteria = "CloudBlue Subscription External ID"\n'
            'If not found = Leave empty\n'
            'If multiple found = Use most actual\n'
        ),
    }


def test_validate_lookup_subscription_with_params_value(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'params__value',
            'from': 'column',
            'action_if_not_found': 'leave_empty',
            'action_if_multiple': 'leave_empty',
            'parameter': {'id': 'P-123', 'name': 'param_a'},
            'output_config': {
                'A': {
                    'attribute': 'id',
                },
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [
                {
                    'name': 'A',
                },
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_subscription/validate', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': (
            'Criteria = "Parameter Value"\nParameter Name = "param_a"\n'
            'If not found = Leave empty\n'
            'If multiple found = Leave empty\n'
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
    response = client.post('/api/lookup_subscription/validate', json=data)

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
        {'lookup_type': 'x', 'from': 'x', 'output_config': None},
        {'lookup_type': 'x', 'from': 'x', 'output_config': {'A': {}}},
        {'lookup_type': 'x', 'from': 'x', 'output_config': {'A': {}}, 'action_if_not_found': ''},
        {'lookup_type': 'x', 'from': 'x', 'output_config': {'A': {}}, 'action_if_multiple': ''},
    ),
)
def test_validate_lookup_subscription_invalid_format(test_client_factory, settings):
    data = {'settings': settings, 'columns': {'input': [{'name': 'name'}]}}
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_subscription/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings must have `lookup_type`, `from`, `output_config`, `action_if_not_found` '
            'and `action_if_multiple` fields'
        ),
    }


def test_validate_lookup_subscription_invalid_lookup_type(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'invalidtype',
            'from': 'column',
            'action_if_not_found': 'fail',
            'action_if_multiple': 'fail',
            'output_config': {
                'A': {
                    'attribute': 'id',
                },
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [
                {
                    'name': 'A',
                },
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_subscription/validate', json=data)

    assert response.status_code == 400, response.content
    data = response.json()
    values = SUBSCRIPTION_LOOKUP.keys()
    assert data == {
        'error': f'The settings `lookup_type` allowed values {values}',
    }


def test_validate_lookup_subscription_invalid_action_if_not_found(
    test_client_factory,
):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'action_if_not_found': 'invalidtype',
            'action_if_multiple': 'leave_empty',
            'output_config': {
                'A': {
                    'attribute': 'id',
                },
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [
                {
                    'name': 'A',
                },
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_subscription/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    values = ['leave_empty', 'fail']
    assert data == {
        'error': f'The settings `action_if_not_found` allowed values {values}',
    }


def test_validate_lookup_subscription_invalid_action_if_multiple(
    test_client_factory,
):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
            'action_if_not_found': 'fail',
            'action_if_multiple': 'invalid',
            'output_config': {
                'A': {
                    'attribute': 'status',
                },
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [
                {
                    'name': 'A',
                },
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_subscription/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    values = ['leave_empty', 'fail', 'use_most_actual']
    assert data == {
        'error': f'The settings `action_if_multiple` allowed values {values}',
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
            'action_if_not_found': 'leave_empty',
            'action_if_multiple': 'leave_empty',
            'output_config': {
                'A': {
                    'attribute': 'id',
                },
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [
                {
                    'name': 'A',
                },
            ],
        },
    }
    if parameter is not None:
        data['settings']['parameter'] = parameter
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_subscription/validate', json=data)

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
            'action_if_not_found': 'leave_empty',
            'action_if_multiple': 'leave_empty',
            'output_config': {
                'A': {
                    'attribute': 'id',
                },
            },
        },
        'columns': {
            'input': [
                {'name': 'otherColumn'},
            ],
            'output': [
                {
                    'name': 'A',
                },
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_subscription/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings `from` contains an invalid column name column that does not exist'
            ' on columns.input'
        ),
    }


def test_validate_lookup_subscription_no_source(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'id',
            'from': 'column',
            'action_if_not_found': 'leave_empty',
            'action_if_multiple': 'leave_empty',
            'output_config': {
                'A': {
                    'attribute': 'id',
                },
            },
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [
                {
                    'name': 'A',
                },
                {
                    'name': 'B',
                },
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_subscription/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The settings `output_config` does not contain settings for the column B.',
    }


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
        {'id': 'P-123', 'name': 'param_a'},
        {'id': 'P-321', 'name': 'param_b'},
    ]
