# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import httpx
from fastapi.responses import JSONResponse

from connect_transformations.exceptions import AirTableError
from connect_transformations.utils import check_mapping


async def get_airtable_data(api_url, token, params=None):
    async with httpx.AsyncClient(transport=httpx.AsyncHTTPTransport(retries=3)) as client:
        try:
            response = await client.get(
                f'https://api.airtable.com/v0/{api_url}',
                headers={'Authorization': f'Bearer {token}'},
                params=params,
            )
            response.raise_for_status()

            return response.json()

        except httpx.HTTPError:
            raise AirTableError(f'Error calling `{api_url}`')


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
        or not isinstance(data['settings']['mapping'], list)
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must contain `api_key`, `base_id`, `table_id` '
                    'fields, dictionary `map_by` and list `mapping` fields.'
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

    mapping_error = check_mapping(data['settings'], data['columns'])
    if mapping_error:
        return mapping_error

    populate = len(data["settings"]["mapping"])
    overview = f'Match column "{data["settings"]["map_by"]["input_column"]}" with AirTable '
    overview += f'field "{data["settings"]["map_by"]["airtable_column"]}" and populate '
    overview += f'{populate} column{"s" if populate > 1 else ""} with the matching data.'

    return {
        'overview': overview,
    }
