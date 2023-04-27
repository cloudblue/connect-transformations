# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import datetime
from decimal import Decimal

from connect.eaas.core.enums import ResultType

from connect_transformations.transformations import StandardTransformationsApplication


def test_formula(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Price with Tax',
                        'formula': '.(Price without Tax) + .(Tax) + ."Additional fee"',
                        'type': 'decimal',
                        'precision': 2,
                    },
                    {
                        'to': 'Tax value',
                        'formula': '.(Tax) / .(Price without Tax)',
                        'type': 'decimal',
                        'precision': 3,
                    },
                    {
                        'to': 'Copy date',
                        'formula': '.Created',
                        'type': 'string',
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
        'Price without Tax': 100, 'Tax': 20, 'Additional fee': 0.2, 'Created': date,
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
    }


def test_formula_using_old_config(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Price String',
                        'formula': '.(Price without Tax)',
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


def test_formula_invalid_row(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'expressions': [
                    {
                        'to': 'Tax value',
                        'formula': '.(Tax) / .(Price without Tax)',
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
