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
                    'formula': '.(Price without Tax) + .Tax',
                },
                {
                    'to': 'Tax value',
                    'formula': '.(Tax) / .(Price without Tax)',
                },
            ],
        },
        'columns': {
            'input': [
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    print(response.status_code)
    print(response.json())
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': (
            "Price with Tax = .(Price without Tax) + .Tax\n"
            "Tax value = .(Tax) / .(Price without Tax)\n"
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
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
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
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
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
                {'name': 'Price', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/validate/formula', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Each `output column` must be unique.',
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
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
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
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
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
                {'name': 'Price without Tax', 'nullable': False},
                {'name': 'Tax', 'nullable': False},
            ],
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
                'formula': '.(Price without Tax) + .Tax',
            },
        ],
        'columns': [
            {'name': 'Price without Tax', 'nullable': False},
            {'name': 'Tax', 'nullable': False},
            {'name': 'Created', 'nullable': False},
            {'name': 'Purchase', 'nullable': False},
        ],
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/formula/extract_input', json=data)

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert {'name': 'Price without Tax', 'nullable': False} in data
    assert {'name': 'Tax', 'nullable': False} in data


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
