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
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must have `from` and `value` fields'
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

    value = settings['value']
    return {
        'overview': f'We Keep Row If Value == "{value}"',
    }
