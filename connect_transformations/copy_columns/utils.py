# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from fastapi.responses import JSONResponse


def validate_copy_columns(data):
    if (
        'settings' not in data
        or not isinstance(data['settings'], list)
        or 'columns' not in data
        or 'input' not in data['columns']
    ):
        return JSONResponse(status_code=400, content={'error': 'Invalid input data'})

    settings = data['settings']
    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    unique_names = [c['name'] for c in input_columns]
    overview = []

    for s in settings:
        if 'from' not in s or 'to' not in s:
            return JSONResponse(
                status_code=400,
                content={'error': 'Invalid settings format'},
            )
        if s['from'] not in available_input_columns:
            return JSONResponse(
                status_code=400,
                content={'error': f'The input column {s["from"]} does not exists'},
            )
        if s['to'] in unique_names:
            return JSONResponse(
                status_code=400,
                content={
                    'error': f'Invalid column name {s["to"]}. The to field should be unique',
                },
            )
        unique_names.append(s['to'])
        overview.append(f'{s["from"]} \u2192 {s["to"]}')

    overview = ''.join([row + '\n' for row in overview])

    return {
        'overview': overview,
    }
