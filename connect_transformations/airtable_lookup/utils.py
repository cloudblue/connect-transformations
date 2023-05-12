# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import httpx

from connect_transformations.airtable_lookup.exceptions import AirTableError
from connect_transformations.utils import (
    build_error_response,
    check_mapping,
    does_not_contain_required_keys,
    has_invalid_basic_structure,
)


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

        except httpx.HTTPError as e:
            raise AirTableError(f'Error calling `{api_url}`: {str(e)}')


def validate_airtable_lookup(data):
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data):
        return build_error_response('Invalid input data')

    if (
        does_not_contain_required_keys(
            data['settings'],
            ['api_key', 'base_id', 'table_id', 'map_by', 'mapping'],
        ) or not isinstance(data['settings']['map_by'], dict)
        or not isinstance(data['settings']['mapping'], list)
    ):
        return build_error_response(
            'The settings must contain `api_key`, `base_id`, `table_id` '
            'fields, dictionary `map_by` and list `mapping` fields.',
        )

    if (
        does_not_contain_required_keys(
            data['settings']['map_by'],
            ['input_column', 'airtable_column'],
        )
    ):
        return build_error_response(
            'The settings field `map_by` must contain '
            '`input_column` and `airtable_column` fields in it.',
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
