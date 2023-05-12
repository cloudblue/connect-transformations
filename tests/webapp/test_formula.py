# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import pytest

from connect_transformations.models import StreamsColumn
from connect_transformations.webapp import TransformationsWebApplication


def test_validate_formula(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '."Price without Tax" + .Tax + ."Additional fee"',
                    'ignore_errors': False,
                    'type': 'decimal',
                    'precision': '2',
                },
                {
                    'to': 'Tax value',
                    'formula': '."Tax" / ."Price without Tax"',
                    'ignore_errors': False,
                    'type': 'decimal',
                    'precision': '2',
                },
                {
                    'to': 'Drop',
                    'formula': 'if .Tax > 10 then drop_row else "OK" end',
                    'ignore_errors': False,
                    'type': 'string',
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
    response = client.post('/api/formula/validate', json=data)
    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': (
            'Price with Tax = ."Price without Tax" + .Tax + ."Additional fee"\n'
            'Tax value = ."Tax" / ."Price without Tax"\n'
            'Drop = if .Tax > 10 then drop_row else "OK" end\n'
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
                    'formula': '."Price without Tax" + ."Tax"',
                },
            ],
        },
        'columns': {},
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/formula/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'Invalid input data',
    }


def test_validate_formula_invalid_expression_field(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': {
                'to': 'Price with Tax',
                'formula': '."Price without Tax" + ."Tax"',
            },
        },
        'columns': {
            'input': [
                {'id': 'COL-1', 'name': 'Price without Tax', 'nullable': False},
                {'id': 'COL-2', 'name': 'Tax', 'nullable': False},
            ],
            'output': [{'name': 'Price with Tax'}],
        },
    }
    client = test_client_factory(TransformationsWebApplication)
    response = client.post('/api/formula/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': 'value is not a valid list (settings.expressions)',
    }


@pytest.mark.parametrize(
    'expression',
    (
        {'formula': '."Price without Tax" + ."Tax"'},
        {'formula': '."PriceWithoutTax" + .Tax', 'to': 'somefield'},
        {'formula': '."PriceWithoutTax" + .Tax', 'to': 'somefield', 'ignore_errors': False},
        {
            'formula': '.PriceWithoutTax + .Tax',
            'to': 'somefield',
            'ignore_errors': False,
            'type': 'invalid',
        },
    ),
)
def test_validate_formula_invalid_expression(
    test_client_factory,
    expression,
):
    data = {
        'settings': {
            'expressions': [
                expression,
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
    response = client.post('/api/formula/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'Each expression must have not empty `to`, `formula`, `type` and `ignore_errors` '
            'fields.'
        ),
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
                    'ignore_errors': False,
                    'type': 'integer',
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
    response = client.post('/api/formula/validate', json=data)

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
                    'formula': '.Price + .Tax',
                    'ignore_errors': False,
                    'type': 'decimal',
                    'precision': '2',
                },
                {
                    'to': 'Pricing',
                    'formula': '.Price + .Tax + ."Additional fee"',
                    'ignore_errors': False,
                    'type': 'decimal',
                    'precision': '2',
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
    response = client.post('/api/formula/validate', json=data)

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
                    'formula': '.Price + .Tax',
                    'ignore_errors': False,
                    'type': 'string',
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
    response = client.post('/api/formula/validate', json=data)

    assert response.status_code == 200
    data = response.json()
    assert data == {
        'overview': 'Price full = .Price + .Tax\n',
    }


def test_validate_formula_non_existing_column_parenthesis(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.Price + .Tax',
                    'ignore_errors': False,
                    'type': 'decimal',
                    'precision': '2',
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
    response = client.post('/api/formula/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'Settings contains formula `.Price + .Tax` '
            'with column that does not exist on columns.input.'
        ),
    }


def test_validate_formula_non_existing_column(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '.Price + .(Tax)',
                    'ignore_errors': False,
                    'type': 'decimal',
                    'precision': '2',
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
    response = client.post('/api/formula/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert data == {
        'error': (
            'Settings contains formula `.Price + .(Tax)` '
            'with column that does not exist on columns.input.'
        ),
    }


def test_validate_formula_non_existing_column_double_quote(
    test_client_factory,
):
    data = {
        'settings': {
            'expressions': [
                {
                    'to': 'Price with Tax',
                    'formula': '."Price without Tax" + ."Tax federal"',
                    'ignore_errors': False,
                    'type': 'decimal',
                    'precision': '2',
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
    response = client.post('/api/formula/validate', json=data)

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
                    'formula': '."Price without Tax"|fill + .(Tax)',
                    'ignore_errors': False,
                    'type': 'decimal',
                    'precision': '2',
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
    response = client.post('/api/formula/validate', json=data)

    assert response.status_code == 400
    data = response.json()
    assert 'jq: error:' in data['error']


def test_extract_formula_input(
    test_client_factory,
):
    data = {
        'expressions': [
            {
                'to': 'Price with Tax',
                'formula': '.["Price without Tax"] + .Tax + ."Additional fee"',
                'type': 'decimal',
                'precision': '2',
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
    assert StreamsColumn(**{'name': 'Price without Tax', 'nullable': False}).dict() in data
    assert StreamsColumn(**{'name': 'Tax', 'nullable': False}).dict() in data
    assert StreamsColumn(**{'name': 'Additional fee', 'nullable': False}).dict() in data


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
                'type': 'decimal',
                'precision': '2',
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
