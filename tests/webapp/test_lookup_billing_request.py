# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.webapp import TransformationsWebApplication


def test_validate_billing_request_lookup(test_client_factory):
    data = {
        'settings': {
            'item': {
                'id': 'id',
                'name': 'Item ID',
            },
            'item_column': 'Request ID',
            'parameter': {
                'id': 'PRM-0001',
                'name': 'param_a',
            },
            'parameter_column': 'Param A',
            'asset_type': None,
            'asset_column': None,
            'output_config': {
                'abc': {
                    'attribute': 'id',
                },
            },
            'action_if_multiple': 'use_most_actual',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 200, response.content
    data = response.json()
    assert data == {
        'overview': (
            'Match by parameter "param_a"\n'
            'If not found = Leave empty\n'
            'If multiple found = Use most actual\n'
            'And populate 1 column'
        ),
    }


def test_validate_billing_request_lookup_with_asset(test_client_factory):
    data = {
        'settings': {
            'item': {
                'id': 'id',
                'name': 'Item ID',
            },
            'item_column': 'Request ID',
            'parameter': {
                'id': 'PRM-0001',
                'name': 'param_a',
            },
            'parameter_column': 'Param A',
            'asset_type': 'id',
            'asset_column': 'Subscription ID',
            'output_config': {
                'abc': {
                    'attribute': 'id',
                },
            },
            'action_if_multiple': 'use_most_actual',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Subscription ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 200, response.content
    data = response.json()
    assert data == {
        'overview': (
            'Match by parameter "param_a"\n'
            'And "CloudBlue Subscription ID"\n'
            'If not found = Leave empty\n'
            'If multiple found = Use most actual\n'
            'And populate 1 column'
        ),
    }


def test_validate_billing_request_lookup_invalid_basic_structure(test_client_factory):
    data = {
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Subscription ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 400, response.content
    data = response.json()
    assert data == {
        'error': 'Invalid input data',
    }


def test_validate_billing_request_lookup_invalid_settings(test_client_factory):
    data = {
        'settings': {
            'item': {
                'id': 'id',
                'name': 'Item ID',
            },
            'item_column': 'Request ID',
            'parameter': {
                'id': 'PRM-0001',
                'name': 'param_a',
            },
            'parameter_column': 'Param A',
            'asset_type': 'id',
            'asset_column': 'Subscription ID',
            'action_if_multiple': 'use_most_actual',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Subscription ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 400, response.content
    data = response.json()
    assert data == {
        'error': (
            'The settings must have `parameter`, `parameter_column`, `item`, `item_column`, '
            '`action_if_not_found` and `action_if_multiple` fields'
        ),
    }


def test_validate_billing_request_lookup_invalid_asset_type(test_client_factory):
    data = {
        'settings': {
            'item': {
                'id': 'id',
                'name': 'Item ID',
            },
            'item_column': 'Request ID',
            'parameter': {
                'id': 'PRM-0001',
                'name': 'param_a',
            },
            'parameter_column': 'Param A',
            'asset_type': 'invalid_type',
            'asset_column': 'Subscription ID',
            'output_config': {
                'abc': {
                    'attribute': 'id',
                },
            },
            'action_if_multiple': 'use_most_actual',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Subscription ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 400, response.content
    data = response.json()
    assert data == {
        'error': 'The settings `asset_type` allowed values external_id, id',
    }


def test_validate_billing_request_lookup_invalid_action_if_not_found(test_client_factory):
    data = {
        'settings': {
            'item': {
                'id': 'id',
                'name': 'Item ID',
            },
            'item_column': 'Request ID',
            'parameter': {
                'id': 'PRM-0001',
                'name': 'param_a',
            },
            'parameter_column': 'Param A',
            'output_config': {
                'abc': {
                    'attribute': 'id',
                },
            },
            'action_if_multiple': 'use_most_actual',
            'action_if_not_found': 'invalid_type',
        },
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Subscription ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 400, response.content
    data = response.json()
    assert data == {
        'error': 'The settings `action_if_not_found` allowed values leave_empty, fail',
    }


def test_validate_billing_request_lookup_invalid_action_if_multiple(test_client_factory):
    data = {
        'settings': {
            'item': {
                'id': 'id',
                'name': 'Item ID',
            },
            'item_column': 'Request ID',
            'parameter': {
                'id': 'PRM-0001',
                'name': 'param_a',
            },
            'parameter_column': 'Param A',
            'output_config': {
                'abc': {
                    'attribute': 'id',
                },
            },
            'action_if_multiple': 'invalid_type',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Subscription ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 400, response.content
    data = response.json()
    assert data == {
        'error': (
            'The settings `action_if_multiple` allowed values leave_empty,'
            ' fail, use_most_actual'
        ),
    }


def test_validate_billing_request_lookup_invalid_parameter(test_client_factory):
    data = {
        'settings': {
            'item': {
                'id': 'id',
                'name': 'Item ID',
            },
            'item_column': 'Request ID',
            'parameter': {
                'name': 'param_a',
            },
            'parameter_column': 'Param A',
            'output_config': {
                'abc': {
                    'attribute': 'id',
                },
            },
            'action_if_multiple': 'leave_empty',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Subscription ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 400, response.content
    data = response.json()
    assert data == {
        'error': 'The settings must have `parameter` with `id` and `name`',
    }


def test_validate_billing_request_lookup_invalid_item(test_client_factory):
    data = {
        'settings': {
            'item': {
                'name': 'Item ID',
            },
            'item_column': 'Request ID',
            'parameter': {
                'id': 'PRM-0001',
                'name': 'param_a',
            },
            'parameter_column': 'Param A',
            'output_config': {
                'abc': {
                    'attribute': 'id',
                },
            },
            'action_if_multiple': 'leave_empty',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Subscription ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 400, response.content
    data = response.json()
    assert data == {
        'error': 'The settings must have `item` with `id` and `name`',
    }


def test_validate_billing_request_lookup_invalid_settings_column(test_client_factory):
    data = {
        'settings': {
            'item': {
                'id': 'id',
                'name': 'Item ID',
            },
            'item_column': 'Request ID',
            'parameter': {
                'id': 'PRM-0001',
                'name': 'param_a',
            },
            'parameter_column': 'Param A',
            'asset_type': 'id',
            'asset_column': 'Invalid column',
            'output_config': {
                'abc': {
                    'attribute': 'id',
                },
            },
            'action_if_multiple': 'leave_empty',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Subscription ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 400, response.content
    data = response.json()
    assert data == {
        'error': (
            'The settings contains an invalid column name Invalid column'
            ' that does not exist on columns.input'
        ),
    }


def test_validate_billing_request_lookup_invalid_output_config(test_client_factory):
    data = {
        'settings': {
            'item': {
                'id': 'id',
                'name': 'Item ID',
            },
            'item_column': 'Request ID',
            'parameter': {
                'id': 'PRM-0001',
                'name': 'param_a',
            },
            'parameter_column': 'Param A',
            'asset_type': 'id',
            'asset_column': 'Subscription ID',
            'output_config': {
                'abcd': {
                    'attribute': 'id',
                },
            },
            'action_if_multiple': 'leave_empty',
            'action_if_not_found': 'leave_empty',
        },
        'columns': {
            'input': [
                {'name': 'Request ID'},
                {'name': 'Subscription ID'},
                {'name': 'Param A'},
            ],
            'output': [
                {'name': 'abc'},
            ],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/lookup_billing_request/validate', json=data)

    assert response.status_code == 400, response.content
    data = response.json()
    assert data == {
        'error': (
            'The settings `output_config` does not contain '
            'settings for the column abc.'
        ),
    }


@pytest.mark.asyncio
async def test_get_billing_parameters(
    test_client_factory,
    async_connect_client,
    async_client_mocker_factory,
):
    client = async_client_mocker_factory(base_url=async_connect_client.endpoint)
    client.products['PRD-123-123'].parameters.all().mock(return_value=[
        {'id': 'P-123', 'name': 'param_a'},
        {'id': 'P-321', 'name': 'param_b'},
    ])

    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/lookup_billing_request/parameters?product_id=PRD-123-123')

    assert response.status_code == 200
    data = response.json()
    assert data == [
        {'id': 'P-123', 'name': 'param_a'},
        {'id': 'P-321', 'name': 'param_b'},
    ]
