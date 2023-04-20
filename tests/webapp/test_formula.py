# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect_transformations.webapp import TransformationsWebApplication


def test_validate_formula(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.(Price without Tax) + .Tax + ."Additional fee"',
                },
                {
                    'to': 'Tax value',
                    'formula': '.(Tax) / .(Price without Tax)',
                },
            ],
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price without Tax', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
                {'id': 'COL-3', 'name': 'Additional fee', 'nullable': False},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': (
            'Price with Tax = .(Price without Tax) + .Tax + ."Additional fee"\n'
            'Tax value = .(Tax) / .(Price without Tax)\n'
        ),
    }


def test_validate_formula_invalid_input(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.(Price without Tax) + .(Tax)',
                },
            ],
        },
        'columns': {},
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Invalid input data.',
    }


def test_validate_formula_invalid_expression_field(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': {
                'to': 'Price with Tax',
                'formula': '.(Price without Tax) + .(Tax)',
            },
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price without Tax', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The settings must have `expressions` field which contains list of formulas.',
    }


def test_validate_formula_invalid_expression(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {'formula': '.(Price without Tax) + .(Tax)'},
            ],
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price without Tax', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Each expression must have not empty `to` and `formula` fields.',
    }


def test_validate_formula_unique_error(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price',
                    'formula': '.(Price) + .(Tax)',
                },
            ],
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Column `Price` already exists.',
    }


def test_validate_formula_duplicated_input_error(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Pricing',
                    'formula': '.(Price) + .(Tax)',
                },
                {
                    'to': 'Pricing',
                    'formula': '.Price + .Tax + ."Additional fee"',
                },
            ],
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
                {'id': 'COL-3', 'name': 'Additional fee', 'nullable': False},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Each `output column` must be unique.',
    }


def test_validate_formula_edit_formula(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price full',
                    'formula': '.(Price) + .Tax',
                },
            ],
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
                {'id': 'COL-3', 'name': 'Price full', 'nullable': False},
            ],
            'output': [
                {'id': 'COL-3', 'name': 'Price full', 'nullable': False},
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': 'Price full = .(Price) + .Tax\n',
    }


def test_validate_formula_non_existing_column(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.(Price) + .(Tax)',
                },
            ],
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price without Tax', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'Settings contains formula `.(Price) + .(Tax)` '
            'with column that does not exist on columns.input.'
        ),
    }


def test_validate_formula_non_existing_column_another(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.Price + .(Tax)',
                },
            ],
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price without Tax', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'Settings contains formula `.Price + .(Tax)` '
            'with column that does not exist on columns.input.'
        ),
    }


def test_validate_formula_non_existing_column_another_one(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '."Price without Tax" + ."Tax federal"',
                },
            ],
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price without Tax', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'Settings contains formula `."Price without Tax" + ."Tax federal"` '
            'with column that does not exist on columns.input.'
        ),
    }


def test_validate_formula_invalid_formula(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.(Price with Tax + .(Tax)',
                },
            ],
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price without Tax', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
            ],
            'output': [],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Settings contains invalid formula `.(Price with Tax + .(Tax)`.',
    }


def test_extract_formula_input(
    test_client_factory,
):
    data = {
        'expressions': [
            {
                'to': 'Price with Tax',
                'formula': '.(Price without Tax) + .Tax + ."Additional fee"',
            },
        ],
        'columns': [
            {'name': 'Price without Tax', 'nullable': False},
            {'name': 'Tax', 'nullable': False},
            {'name': 'Additional fee', 'nullable': False},
            {'name': 'Created', 'nullable': False},
            {'name': 'Purchase', 'nullable': False},
        ],
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/formula/extract_input', json=data)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 3
    assert {'name': 'Price without Tax', 'nullable': False} in data
    assert {'name': 'Tax', 'nullable': False} in data
    assert {'name': 'Additional fee', 'nullable': False} in data


def test_extract_formula_input_invalid_expressions(
    test_client_factory,
):
    data = {
        'expressions': {
            'to': 'Price with Tax',
            'formula': '.(Price without Tax) + .(Tax)',
        },
        'columns': [
            {'name': 'Price without Tax', 'nullable': False},
            {'name': 'Tax', 'nullable': False},
        ],
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/formula/extract_input', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The body does not contain `expressions` list',
    }


def test_extract_formula_input_missing_columns(
    test_client_factory,
):
    data = {
        'expressions': [
            {
                'to': 'Price with Tax',
                'formula': '.(Price without Tax) + .(Tax)',
            },
        ],
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/formula/extract_input', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'The body does not contain `columns` list',
    }
