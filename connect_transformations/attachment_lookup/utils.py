# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect_transformations.utils import (
    build_error_response,
    check_mapping,
    does_not_contain_required_keys,
    has_invalid_basic_structure,
)


def validate_attachment_lookup(data):
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data):
        return build_error_response('Invalid input data')

    if (
        does_not_contain_required_keys(
            data['settings'],
            ['file', 'map_by', 'mapping'],
        )
        or not isinstance(data['settings']['map_by'], list)
        or not isinstance(data['settings']['mapping'], list)
    ):
        return build_error_response(
            'The settings must contain `file` and optional `sheet` '
            'fields and lists of `map_by` and `mapping` fields.',
        )

    for map in data['settings']['map_by']:
        if does_not_contain_required_keys(
            map,
            ['input_column', 'attachment_column'],
        ):
            return build_error_response(
                'The settings field `map_by` must contain of dicts with '
                '`input_column` and `attachment_column` fields in it.',
            )

    mapping_error = check_mapping(data['settings'], data['columns'], multiple=True)
    if mapping_error:
        return mapping_error

    inp_cols = ', '.join([map_by['input_column'] for map_by in data["settings"]["map_by"]])
    atc_cols = ', '.join([map_by['attachment_column'] for map_by in data["settings"]["map_by"]])
    map_by = len(data["settings"]["map_by"])
    populate = len(data['settings']['mapping'])
    overview = f'Match column{"s" if map_by > 1 else ""} "{inp_cols}" with Attachment '
    overview += f'field{"s" if map_by > 1 else ""} "{atc_cols}" and populate '
    overview += f'{populate} column{"s" if populate > 1 else ""} with the matching data.'

    return {
        'overview': overview,
    }
