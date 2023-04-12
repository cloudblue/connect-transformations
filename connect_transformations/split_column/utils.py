# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re

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
