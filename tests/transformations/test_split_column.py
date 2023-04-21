# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from decimal import Decimal

import pytest
from connect.eaas.core.enums import ResultType
from dateutil.parser import parse

from connect_transformations.transformations import StandardTransformationsApplication


@pytest.mark.asyncio
async def test_split_column_string(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': r'(\w+) (?P<first_name>\w+) (?P<last_name>\w+)',
                    'groups': {
                        '1': {'name': 'group_1', 'type': 'string'},
                        '2': {'name': 'First Name', 'type': 'string'},
                        '3': {'name': 'Last Name', 'type': 'string'},
                    },
                },
            },
        },
    }
    response = await app.split_column({
        'column': 'X Name Surname',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'group_1': 'X',
        'First Name': 'Name',
        'Last Name': 'Surname',
    }


@pytest.mark.asyncio
async def test_split_column_integer(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': r'(\w+) (?P<number>\d+)',
                    'groups': {
                        '1': {'name': 'street', 'type': 'string'},
                        '2': {'name': 'number', 'type': 'integer'},
                    },
                },
            },
        },
    }
    response = await app.split_column({
        'column': 'street 22',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'street': 'street',
        'number': 22,
    }


@pytest.mark.asyncio
async def test_split_column_decimal(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': r'(\w+) (?P<number>[\d,.]+) (?P<vat>[\d,.]+)',
                    'groups': {
                        '1': {'name': 'currency', 'type': 'string'},
                        '2': {'name': 'number', 'type': 'decimal', 'precision': 2},
                        '3': {'name': 'vat', 'type': 'decimal', 'precision': 3},
                    },
                },
            },
        },
    }
    response = await app.split_column({
        'column': 'euro 22.44 3,4333',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'currency': 'euro',
        'number': Decimal('22.44').quantize(
            Decimal('.001'),
        ),
        'vat': Decimal('3.4333').quantize(
            Decimal('.0001'),
        ),
    }


@pytest.mark.parametrize(
    ('value', 'result'),
    (
        ('True', True),
        ('TRUE', True),
        ('true', True),
        ('1', True),
        ('False', False),
        ('FALSE', False),
        ('false', False),
        ('0', False),
        ('', None),
        (None, None),
    ),
)
@pytest.mark.asyncio
async def test_split_column_boolean(mocker, value, result):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': r'(\w+)',
                    'groups': {
                        '1': {'name': 'is_right', 'type': 'boolean'},
                    },
                },
            },
        },
    }
    response = await app.split_column({
        'column': value,
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'is_right': result,
    }


@pytest.mark.parametrize(
    'value',
    (
        '2022/03/21 17:21:00 CEST',
        '2022-01-19 12:31:00 UTC',
    ),
)
@pytest.mark.asyncio
async def test_split_column_datetime(mocker, value):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': r'(.*)',
                    'groups': {
                        '1': {'name': 'date', 'type': 'datetime'},
                    },
                },
            },
        },
    }
    response = await app.split_column({
        'column': value,
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'date': parse(value),
    }


@pytest.mark.asyncio
async def test_split_column_not_match_regex(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': '(\\w+) (?P<first_name>\\w+) (?P<last_name>\\w+)',
                    'groups': {
                        '1': {'name': 'group_1', 'type': 'string'},
                        '2': {'name': 'First Name', 'type': 'string'},
                        '3': {'name': 'Last Name', 'type': 'string'},
                    },
                },
            },
        },
    }
    response = await app.split_column({
        'column': 'Name Surname',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'First Name': None,
        'Last Name': None,
        'group_1': None,
    }


@pytest.mark.asyncio
async def test_split_column_match_partially(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': '(?P<first_name>\\w+) (?P<last_name>\\w+)',
                    'groups': {
                        '1': {'name': 'First Name', 'type': 'string'},
                        '2': {'name': 'Last Name', 'type': 'string'},
                    },
                },
            },
        },
    }
    response = await app.split_column({
        'column': 'Name Surname Othername',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'First Name': 'Name',
        'Last Name': 'Surname',
    }


@pytest.mark.asyncio
async def test_split_column_match_optional(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': '(?P<first_name>\\w+) (?:(?P<last_name>\\w+))?',
                    'groups': {
                        '1': {'name': 'First Name', 'type': 'string'},
                        '2': {'name': 'Last Name', 'type': 'string'},
                    },
                },
            },
        },
    }
    response = await app.split_column({
        'column': 'Name ',
    })

    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'First Name': 'Name',
        'Last Name': None,
    }
