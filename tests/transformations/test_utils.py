from datetime import datetime, timezone
from decimal import Decimal

import pytest

from connect_transformations.utils import cast_value_to_type


@pytest.mark.parametrize(
    ('value', 'expected'),
    (
        ('1', '1'),
        (1, '1'),
        ('hello', 'hello'),
        (None, None),
    ),
)
def test_cast_to_string(value, expected):
    assert cast_value_to_type(value, 'string') == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    (
        ('1', 1),
        (1, 1),
        (2.2, 2),
        (None, None),
    ),
)
def test_cast_to_integer(value, expected):
    assert cast_value_to_type(value, 'integer') == expected


@pytest.mark.parametrize(
    ('value', 'precision', 'expected'),
    (
        ('1.11', 2, Decimal(1.11).quantize(Decimal('.001'))),
        ('1.123', 8, Decimal(1.123).quantize(Decimal('.000000001'))),
        (1.11, 2, Decimal(1.11).quantize(Decimal('.001'))),
        (None, 2, None),
    ),
)
def test_cast_to_decimal(value, precision, expected):
    assert cast_value_to_type(value, 'decimal', {'precision': precision}) == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    (
        ('1', True),
        (True, True),
        (False, False),
        (2.2, None),
        (None, None),
    ),
)
def test_cast_to_bool(value, expected):
    assert cast_value_to_type(value, 'boolean') == expected


@pytest.mark.parametrize(
    ('value', 'expected'),
    (
        ('2/10/2022', datetime(2022, 2, 10)),
        ('2/10/2022 10:23:54', datetime(2022, 2, 10, 10, 23, 54)),
        ('2/10/2022 10:23:54 UTC', datetime(2022, 2, 10, 10, 23, 54, tzinfo=timezone.utc)),
        (None, None),
    ),
)
def test_cast_to_datetime(value, expected):
    assert cast_value_to_type(value, 'datetime') == expected
