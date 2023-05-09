# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from fastapi.responses import JSONResponse


def validate_vat_rate(data):
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
        or 'to' not in data['settings']
        or 'action_if_not_found' not in data['settings']
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must have `from`, `to` and `action_if_not_found` '
                    'fields'
                ),
            },
        )

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

    return {
        'overview': (
            'What to do for non-EU country codes = '
            + data['settings']['action_if_not_found'].replace('_', ' ').title()
            + '\n'
        ),
    }
