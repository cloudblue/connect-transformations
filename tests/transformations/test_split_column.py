# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from datetime import datetime
from decimal import Decimal

import pytest
from connect.eaas.core.enums import ResultType
from dateutil.parser import parse

from connect_transformations.transformations import StandardTransformationsApplication


def test_split_column_string(mocker):
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
    response = app.split_column({
        'column': 'X Name Surname',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'group_1': 'X',
        'First Name': 'Name',
        'Last Name': 'Surname',
    }


def test_split_column_integer(mocker):
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
    response = app.split_column({
        'column': 'street 22',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'street': 'street',
        'number': 22,
    }


def test_split_column_input_float(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': r'(\w+).(\d+)',
                    'groups': {
                        '1': {'name': 'whole', 'type': 'integer'},
                        '2': {'name': 'fract', 'type': 'integer'},
                    },
                },
            },
        },
    }
    response = app.split_column({
        'column': 100.12,
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'whole': 100,
        'fract': 12,
    }


def test_split_column_input_datetime(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': r'(\d{4})-(\d{2})-(\d{2}).*',
                    'groups': {
                        '1': {'name': 'year', 'type': 'integer'},
                        '2': {'name': 'month', 'type': 'integer'},
                        '3': {'name': 'day', 'type': 'integer'},
                    },
                },
            },
        },
    }
    response = app.split_column({
        'column': datetime(2022, 1, 2, 12, 11),
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'year': 2022,
        'month': 1,
        'day': 2,
    }


def test_split_column_decimal(mocker):
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
    response = app.split_column({
        'column': 'euro 22.44 3,4333',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'currency': 'euro',
        'number': Decimal('22.44').quantize(
            Decimal('.01'),
        ),
        'vat': Decimal('3.4333').quantize(
            Decimal('.001'),
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
def test_split_column_boolean(mocker, value, result):
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
    response = app.split_column({
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
def test_split_column_datetime(mocker, value):
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
    response = app.split_column({
        'column': value,
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'date': parse(value),
    }


def test_split_column_not_match_regex(mocker):
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
    response = app.split_column({
        'column': 'Name Surname',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'First Name': None,
        'Last Name': None,
        'group_1': None,
    }


def test_split_column_match_partially(mocker):
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
    response = app.split_column({
        'column': 'Name Surname Othername',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'First Name': 'Name',
        'Last Name': 'Surname',
    }


def test_split_column_match_optional(mocker):
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
    response = app.split_column({
        'column': 'Name ',
    })

    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'First Name': 'Name',
        'Last Name': None,
    }


def test_split_column_old_config(mocker):
    m = mocker.MagicMock()
    app = StandardTransformationsApplication(m, m, m)
    app.transformation_request = {
        'transformation': {
            'settings': {
                'from': 'column',
                'regex': {
                    'pattern': r'(\w+) (?P<first_name>\w+) (?P<last_name>\w+)',
                    'groups': {
                        '1': {'name': 'group_1'},
                        '2': {'name': 'First Name'},
                        '3': {'name': 'Last Name'},
                    },
                },
            },
        },
    }
    response = app.split_column({
        'column': 'X Name Surname',
    })
    assert response.status == ResultType.SUCCESS
    assert response.transformed_row == {
        'group_1': 'X',
        'First Name': 'Name',
        'Last Name': 'Surname',
    }
