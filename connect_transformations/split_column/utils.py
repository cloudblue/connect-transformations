# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re
from decimal import Decimal

from dateutil.parser import parse as _to_datetime
from fastapi.responses import JSONResponse


def validate_split_column(data):
    if (
        'settings' not in data
        or not isinstance(data['settings'], dict)
        or 'columns' not in data
        or 'input' not in data['columns']
    ):
        return JSONResponse(status_code=400, content={'error': 'Invalid input data'})

    if (
        'from' not in data['settings']
        or 'regex' not in data['settings']
        or 'pattern' not in data['settings']['regex']
        or not isinstance(data['settings']['regex']['pattern'], str)
        or 'groups' not in data['settings']['regex']
        or not isinstance(data['settings']['regex']['groups'], dict)
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must have `from` and `regex` with `pattern` and `groups` '
                    'fields'
                ),
            },
        )

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    if data['settings']['from'] not in available_input_columns:
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings contains an invalid `from` column name'
                    f' "{data["settings"]["from"]}" that does not exist on '
                    'columns.input'
                ),
            },
        )

    pattern = None
    try:
        pattern = re.compile(data['settings']['regex']['pattern'])
    except re.error:
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings contains an invalid `regex` regular expression '
                    f"{data['settings']['regex']['pattern']}"
                ),
            },
        )

    if pattern.groups != len(data['settings']['regex']['groups']):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings `groups` contains a different number of elements that are'
                    ' defined in the regular expression '
                    f"{data['settings']['regex']['pattern']}"
                ),
            },
        )

    return {
        'overview': "Regexp = '" + data['settings']['regex']['pattern'] + "'",
    }


def merge_groups(new_groups: dict, past_groups: dict):
    if not past_groups:
        return {'groups': new_groups}
    for key in new_groups.keys():
        if key in past_groups:
            new_groups[key] = past_groups[key]


def _to_decimal(value, precision=2):
    p = ''.join(['0' for _ in range(int(precision))])
    return Decimal(
        value.replace(',', '.'),
    ).quantize(
        Decimal(f'.{p}1'),
    )


def _to_boolean(value):
    if value in ['true', 'True', 'TRUE', '1', 'y', 'yes']:
        return True
    elif value in ['false', 'False', 'FALSE', '0', 'n', 'no']:
        return False


_cast_mapping = {
    'string': str,
    'integer': int,
    'decimal': _to_decimal,
    'boolean': _to_boolean,
    'datetime': _to_datetime,
}


def cast_value_to_type(value, type, additional_parameters=None):
    if additional_parameters is None:
        additional_parameters = {}
    cast_fn = _cast_mapping[type]
    return cast_fn(value, **additional_parameters) if value else None
