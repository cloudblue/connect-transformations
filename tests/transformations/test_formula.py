# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import datetime

import pytest

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
    assert app.formula({
        'Price without Tax': 100, 'Tax': 20, 'Created': date,
    }) == {
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

    with pytest.raises(ValueError) as e:
        app.formula({'Price without Tax': 100, 'Tax': 'twenty'})

    assert str(e.value) == 'string ("twenty") and number (100) cannot be divided'
