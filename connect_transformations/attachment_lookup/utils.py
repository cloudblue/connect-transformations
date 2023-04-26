# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from fastapi.responses import JSONResponse

from connect_transformations.utils import check_mapping


def validate_attachment_lookup(data):
    if (
        'settings' not in data
        or not isinstance(data['settings'], dict)
        or 'columns' not in data
        or 'input' not in data['columns']
    ):
        return JSONResponse(status_code=400, content={'error': 'Invalid input data'})

    if (
        'file' not in data['settings']
        or 'map_by' not in data['settings']
        or not isinstance(data['settings']['map_by'], dict)
        or 'mapping' not in data['settings']
        or not isinstance(data['settings']['mapping'], list)
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must contain `file` and optional `sheet` '
                    'fields and dictionary `map_by` and list `mapping` fields.'
                ),
            },
        )

    if (
        'input_column' not in data['settings']['map_by']
        or 'attachment_column' not in data['settings']['map_by']
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings field `map_by` must contain '
                    '`input_column` and `attachment_column` fields in it.'
                ),
            },
        )

    mapping_error = check_mapping(data['settings'], data['columns'])
    if mapping_error:
        return mapping_error

    populate = len(data['settings']['mapping'])
    overview = f'Match column "{data["settings"]["map_by"]["input_column"]}" with Attachment '
    overview += f'field "{data["settings"]["map_by"]["attachment_column"]}" and populate '
    overview += f'{populate} column{"s" if populate > 1 else ""} with the matching data.'

    return {
        'overview': overview,
    }
