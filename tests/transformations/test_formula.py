# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import datetime

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
                        'formula': '.(Price without Tax) + .(Tax)',
                    },
                    {
                        'to': 'Tax value',
                        'formula': '.(Tax) / .(Price without Tax)',
                    },
                    {
                        'to': 'Copy date',
                        'formula': '.Created',
                    },
                ],
            },
            'columns': {
                'input': [
                    {'name': 'Price without Tax', 'nullable': False},
                    {'name': 'Tax', 'nullable': False},
                    {'name': 'Created', 'nullable': False, 'type': 'datetime'},
                ],
            },
        },
    }

    date = datetime.datetime.now()
    response = app.formula({
        'Price without Tax': 100, 'Tax': 20, 'Created': date,
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'Price with Tax': 120,
        'Tax value': 0.2,
        'Copy date': str(date),
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
