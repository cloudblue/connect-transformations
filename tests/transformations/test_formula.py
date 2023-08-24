# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import datetime
from decimal import Decimal

import pytest
from connect.eaas.core.enums import ResultType

from connect_transformations.formula.utils import find_all_columns
from connect_transformations.transformations import StandardTransformationsApplication


@pytest.mark.parametrize('formula,columns', (
    ('.a .b', ['a', 'b']),
    ('."a.b.c" .d', ['a.b.c', 'd']),
    ('."a.b.c" .["qwe"]', ['a.b.c', 'qwe']),
    ('."a.b.c" .["qwe"]', ['a.b.c', 'qwe']),
    ('."as.d"*.qwe', ['as.d', 'qwe']),
    ('$a.b.c + .a', ['a']),

))
def test_find_all_columns(formula, columns):
    assert list(find_all_columns(formula)) == columns


def test_formula(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'stream': {
            'id': 'STR-3920-1626-6382',
            'name': 'Stream',
            'context': {
                'listing': {
                    'id': 'LST-1113-3453-3429',
                },
            },
        },
        'batch': {
            'id': 'BAT-1211-1123-2423-2342',
            'name': 'Batch',
            'context': {
                'period': {
                    'start': datetime.datetime(2023, 1, 1, 0, 0, 0),
                    'end': datetime.datetime(2023, 1, 31, 23, 59, 59),
                },
            },
        },
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Price with Tax',
                        'formula': '.["Price without Tax"] + .Tax + ."Additional fee"',
                        'ignore_errors': True,
                        'type': 'decimal',
                        'precision': 2,
                    },
                    {
                        'to': 'Tax value',
                        'formula': '.Tax / ."Price without Tax"',
                        'ignore_errors': True,
                        'type': 'decimal',
                        'precision': 3,
                    },
                    {
                        'to': 'Copy date',
                        'formula': '.Created',
                        'ignore_errors': True,
                        'type': 'string',
                    },
                    {
                        'to': 'Billing period',
                        'formula': '$context.period.start',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'Price without Tax', 'nullable': False, 'type': 'integer'},
                    {'name': 'Additional fee', 'nullable': False, 'type': 'decimal'},
                    {'name': 'Tax', 'nullable': False, 'type': 'integer'},
                    {'name': 'Created', 'nullable': False, 'type': 'datetime'},
                ],
            },
        },
    }

    date = datetime.datetime.now()
    response = app.formula({
        'Price without Tax': 100,
        'Tax': 20,
        'Additional fee': 0.2,
        'Created': date,
        'Redundant Column': None,
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Price with Tax': Decimal(120.2).quantize(
            Decimal('.01'),
        ),
        'Tax value': Decimal(0.2).quantize(
            Decimal('.001'),
        ),
        'Copy date': str(date),
        'Billing period': '2023-01-01 00:00:00',
    }


def test_formula_using_old_config(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'stream': {
            'id': 'STR-3920-1626-6382',
            'name': 'Stream',
            'context': {
                'listing': {
                    'id': 'LST-1113-3453-3429',
                },
            },
        },
        'batch': {
            'id': 'BAT-1211-1123-2423-2342',
            'name': 'Batch',
            'context': {
                'period': {
                    'start': datetime.datetime(2023, 1, 1, 0, 0, 0),
                    'end': datetime.datetime(2023, 1, 31, 23, 59, 59),
                },
            },
        },
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Price String',
                        'formula': '."Price without Tax"',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'Price without Tax', 'nullable': False, 'type': 'integer'},
                ],
            },
        },
    }

    response = app.formula({
        'Price without Tax': 100,
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Price String': '100',
    }


def test_formula_invalid_operation(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'stream': {},
        'batch': {},
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Tax value',
                        'formula': '.["Tax"] / ."Price without Tax"',
                        'ignore_errors': False,
                        'type': 'decimal',
                        'precision': '2',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'Price without Tax', 'nullable': False},
                    {'name': 'Tax', 'nullable': False},
                ],
            },
        },
    }

    response = app.formula({'Price without Tax': 100, 'Tax': 'twenty'})
    assert response.status == ResultType.FAIL
    assert 'string ("twenty") and number (100) cannot be divided' in response.output


def test_formula_invalid_variable(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'stream': {},
        'batch': {},
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Tax value',
                        'formula': '$a / ."Price without Tax"',
                        'ignore_errors': False,
                        'type': 'decimal',
                        'precision': '2',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'Price without Tax', 'nullable': False},
                ],
            },
        },
    }

    response = app.formula({'Price without Tax': 100, 'Tax': 'twenty'})
    assert response.status == ResultType.FAIL
    assert 'jq: error: $a is not defined at <top-level>, line 1:' in response.output


def test_formula_invalid_row_ignore_errors(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'stream': {},
        'batch': {},
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Tax value',
                        'formula': '.Tax / ."Price without Tax"',
                        'ignore_errors': True,
                        'type': 'decimal',
                        'precision': '2',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'Price without Tax', 'nullable': False},
                    {'name': 'Tax', 'nullable': False},
                ],
            },
        },
    }

    response = app.formula({'Price without Tax': 100, 'Tax': 'twenty'})
    assert response.status == ResultType.SUCCESS


def test_formula_no_output(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'stream': {},
        'batch': {},
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Tax value',
                        'formula': 'select(.Tax == "one") | "Drop Column"',
                        'ignore_errors': True,
                        'type': 'string',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'Price without Tax', 'nullable': False},
                    {'name': 'Tax', 'nullable': False},
                ],
            },
        },
    }

    response = app.formula({'Price without Tax': 100, 'Tax': 'twenty'})
    assert response.status == ResultType.SUCCESS
    assert response.output is None


def test_formula_drop_row(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'stream': {},
        'batch': {},
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Tax rate',
                        'formula': 'if .Tax > 10 then drop_row else "OK" end',
                        'ignore_errors': True,
                        'type': 'string',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'Price without Tax', 'nullable': False},
                    {'name': 'Tax', 'nullable': False},
                ],
            },
        },
    }

    response = app.formula({'Price without Tax': 100, 'Tax': 20})
    print(response.output)
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Tax rate': '#INSTRUCTION/DELETE_ROW',
    }

    response = app.formula({'Price without Tax': 100, 'Tax': 8})
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Tax rate': 'OK',
    }


@pytest.mark.parametrize('formula,expected', (
    ('tonumber(.c)', 2.23),
    ('.c | tonumber', 2.23),
    ('.a | round', 10),
    ('.a | round(1)', 10.1),
    ('.b | round(1)', 19.5),
    ('round(.b; 2)', 19.47),
    ('round(.b; -2.5)', 0),
))
def test_formula_functions_common(mocker, formula, expected):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'stream': {},
        'batch': {},
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'd',
                        'formula': formula,
                        'ignore_errors': False,
                        'type': 'decimal',
                        'constraints': {
                            'precision': 2,
                        },
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'a', 'nullable': False},
                    {'name': 'b', 'nullable': False},
                ],
            },
        },
    }
    response = app.formula({'a': 10.123, 'b': 19.466, 'c': "2.23"})

    assert response.transformed_row == {'d': expected}


@pytest.mark.parametrize('formula,expected', (
    ('gross_profit(.a; .b) | round(2)', 5.23),
    ('margin(.a; .b) | round(2)', 4.54),
    ('markup(.a; .b) | round(2)', 4.75),
))
def test_formula_functions_pricing(mocker, formula, expected):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'stream': {},
        'batch': {},
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'c',
                        'formula': formula,
                        'ignore_errors': False,
                        'type': 'decimal',
                        'constraints': {
                            'precision': 2,
                        },
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'a', 'nullable': False, 'type': 'decimal'},
                    {'name': 'b', 'nullable': False, 'type': 'decimal'},
                ],
            },
        },
    }
    response = app.formula({'a': 115.23, 'b': 110})

    assert response.transformed_row == {'c': expected}
