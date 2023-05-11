# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from fastapi.responses import JSONResponse


def validate_filter_row(data):
    if (
        'settings' not in data
        or not isinstance(data['settings'], dict)
        or 'columns' not in data
        or 'input' not in data['columns']
    ):
        return JSONResponse(status_code=400, content={'error': 'Invalid input data'})

    settings = data['settings']

    if (
        'from' not in settings
        or settings['from'] is None
        or settings['from'] == ''
        or 'value' not in settings
        or not isinstance(settings['value'], str)
        or 'match_condition' not in settings
        or not isinstance(settings['match_condition'], bool)
        or 'additional_values' not in settings
        or not isinstance(settings['additional_values'], list)
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must have `from`, `value`, boolean `match_condition` '
                    'and list `additional_values` fields'
                ),
            },
        )

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    if settings['from'] not in available_input_columns:
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must have a valid `from` column name'
                ),
            },
        )

    for condition in settings['additional_values']:
        if (
            'value' not in condition
            or not condition['value']
            or not isinstance(condition['value'], str)
        ):
            return JSONResponse(
                status_code=400,
                content={
                    'error': (
                        'Each additional value in the settings must have '
                        'not empty `value` field and `operation` field '
                        'equal to `or` or `and`'
                    ),
                },
            )

    value = f'"{settings["value"]}"'
    for condition in settings['additional_values']:
        value += f' {"OR" if settings["match_condition"] else "AND"} "{condition["value"]}"'

    return {
        'overview': (
            f'We Keep Row If Value of column "{settings["from"]}" '
            f'{"==" if settings["match_condition"] else "!="} {value}'
        ),
    }
