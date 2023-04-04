# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from fastapi.responses import JSONResponse


def validate_currency_conversion(data):
    if (
        'settings' not in data
        or not isinstance(data['settings'], dict)
        or 'columns' not in data
        or 'input' not in data['columns']
    ):
        return JSONResponse(status_code=400, content={'error': 'Invalid input data'})

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    if (
        'from' not in data['settings']
        or 'column' not in data['settings']['from']
        or 'currency' not in data['settings']['from']
        or 'to' not in data['settings']
        or 'column' not in data['settings']['to']
        or 'currency' not in data['settings']['to']
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must have `from` with the `column` and the `currency`, and '
                    '`to` with the `column` and `currency` fields'
                ),
            },
        )

    if data['settings']['from']['column'] not in available_input_columns:
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings contains an invalid `from` column name'
                    f' "{data["settings"]["from"]["column"]}" that does not exist on '
                    'columns.input'
                ),
            },
        )

    overview = 'From Currency = ' + data['settings']['from']['currency'] + '\n'
    overview += 'To Currency = ' + data['settings']['to']['currency'] + '\n'

    return {
        'overview': overview,
    }
