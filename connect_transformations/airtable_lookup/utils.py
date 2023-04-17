# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import httpx
from fastapi.responses import JSONResponse

from connect_transformations.exceptions import AirTableError


def get_airtable_data(api_url, token, params=None):
    try:
        with httpx.Client(transport=httpx.HTTPTransport(retries=3)) as client:
            response = client.get(
                f'https://api.airtable.com/v0/{api_url}',
                headers={'Authorization': f'Bearer {token}'},
                params=params,
            )

            if response.status_code != 200:
                raise AirTableError(f'Unexpected response calling {api_url}')

            return response.json()

    except httpx.RequestError as e:
        raise AirTableError(f'Error calling {api_url}: {e}')


def validate_airtable_lookup(data):
    if (
        'settings' not in data
        or not isinstance(data['settings'], dict)
        or 'columns' not in data
        or 'input' not in data['columns']
    ):
        return JSONResponse(status_code=400, content={'error': 'Invalid input data'})

    if (
        'api_key' not in data['settings']
        or 'base_id' not in data['settings']
        or 'table_id' not in data['settings']
        or 'map_by' not in data['settings']
        or not isinstance(data['settings']['map_by'], dict)
        or 'mapping' not in data['settings']
        or not isinstance(data['settings']['mapping'], dict)
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must contain `api_key`, `base_id`, `table_id` '
                    'fields and dictionary `map_by` and `mapping` fields.'
                ),
            },
        )

    if (
        'input_column' not in data['settings']['map_by']
        or 'airtable_column' not in data['settings']['map_by']
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings field `map_by` must contain '
                    '`input_column` and `airtable_column` fields in it.'
                ),
            },
        )

    available_columns = [c['name'] for c in data['settings']['input']['columns']]
    if data['settings']['map_by']['input_column'] not in available_columns:
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings contains invalid input column that '
                    'does not exist on columns.input'
                ),
            },
        )

    for mapping in data['settings']['mapping']:
        if (
            not isinstance(mapping, dict)
            or 'from' not in mapping
            or 'to' not in mapping
        ):
            return JSONResponse(
                status_code=400,
                content={
                    'error': (
                        'Each element of the settings `mapping` must contain '
                        '`from` and `to` fields in it.'
                    ),
                },
            )

    populate = len(data["settings"]["mapping"])

    overview = f'Match column "{data["settings"]["map_by"]["input_column"]}" with AirTable '
    overview += f'field "{data["settings"]["map_by"]["airtable_column"]}" and populate '
    overview += f'{populate} column{"s" if populate > 1 else ""} with the matching data.'

    return {
        'overview': overview,
    }
