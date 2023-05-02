# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect_transformations.constants import PRODUCT_ITEM_LOOKUP
from connect_transformations.webapp import TransformationsWebApplication


def test_validate_lookup_product_item(test_client_factory):
    data = {
        'settings': {
            'product_id': 'PRD-000-000-001',
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
            'action_if_not_found': 'fail',
            'product_lookup_mode': 'id',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_product_item', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': (
            'Criteria = "CloudBlue Item ID"\nIn product = '
            '\"PRD-000-000-001\"\nPrefix = "PREFIX"\nIf not found = Fail\n'
        ),
    }


def test_validate_lookup_product_item_no_product(test_client_factory):
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
    response = client.post('/api/validate/lookup_product_item', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'No product associated with this data stream. Please either enter a Product ID, '
            'which will be applied to all product item lookups, or select a Product column '
            'containing the row-specific product IDs.'
        ),
    }


def test_validate_lookup_product_item_no_product_no_column(test_client_factory):
    data = {
        'settings': {
            'lookup_type': 'id',
            'product_id': '',
            'product_column': '',
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
    response = client.post('/api/validate/lookup_product_item', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'No product associated with this data stream. Please either enter a Product ID, '
            'which will be applied to all product item lookups, or select a Product column '
            'containing the row-specific product IDs.'
        ),
    }


def test_validate_lookup_product_item_no_settings(test_client_factory):
    data = {
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_product_item', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'Invalid input data'
        ),
    }


def test_validate_lookup_product_item_unknown_mode(test_client_factory):
    data = {
        'settings': {
            'product_id': 'PRD-000-000-001',
            'lookup_type': 'unknown',
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
    response = client.post('/api/validate/lookup_product_item', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings `lookup_type` allowed values [\'mpn\', \'id\']'
        ),
    }


def test_validate_lookup_product_item_unknown_action(test_client_factory):
    data = {
        'settings': {
            'product_id': 'PRD-000-000-001',
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
            'action_if_not_found': 'unknown',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_product_item', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings `action_if_not_found` allowed values [\'leave_empty\', \'fail\']'
        ),
    }


def test_validate_lookup_product_item_unavailable_column(test_client_factory):
    data = {
        'settings': {
            'product_id': 'PRD-000-000-001',
            'lookup_type': 'id',
            'from': 'unavailable_column',
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
    response = client.post('/api/validate/lookup_product_item', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings `from` contains an invalid column name unavailable_column '
            'that does not exist on columns.input'
        ),
    }


def test_validate_lookup_product_item_long_prefix(test_client_factory):
    data = {
        'settings': {
            'product_id': 'PRD-000-000-001',
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX_THAT_EXCEED_MAX_VALUE',
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
    response = client.post('/api/validate/lookup_product_item', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'The settings `prefix` max length is 10'
        ),
    }


def test_get_product_item_criteria(test_client_factory):
    client = test_client_factory(TransformationsWebApplication)
    response = client.get('/api/lookup_product_item/criteria')

    assert response.status_code == 200
    data = response.json()
    assert data == PRODUCT_ITEM_LOOKUP


def test_validate_lookup_product_item_with_column(test_client_factory):
    data = {
        'settings': {
            'product_id': '',
            'product_column': 'Product ID column',
            'lookup_type': 'id',
            'from': 'column',
            'prefix': 'PREFIX',
            'action_if_not_found': 'fail',
            'product_lookup_mode': 'column',
        },
        'columns': {
            'input': [
                {'name': 'column'},
            ],
            'output': [],
        },
    }

    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/lookup_product_item', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': (
            'Criteria = "CloudBlue Item ID"\nWith row-specific product IDs '
            '\nPrefix = "PREFIX"\nIf not found = Fail\n'
        ),
    }


def test_validate_lookup_product_item_no_required_column(test_client_factory):
    data = {
        'settings': {
            'product_id': '',
            'product_column': 'Product ID column',
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
    response = client.post('/api/validate/lookup_product_item', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {'error': (
        'The settings must have `lookup_type`, `from`, `prefix` and '
        '`action_if_not_found` fields'
    )}
