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
        or not isinstance(data['settings']['map_by'], dict)
        or not isinstance(data['settings']['mapping'], list)
    ):
        return build_error_response(
            'The settings must contain `file` and optional `sheet` '
            'fields and dictionary `map_by` and list `mapping` fields.',
        )

    if does_not_contain_required_keys(
        data['settings']['map_by'],
        ['input_column', 'attachment_column'],
    ):
        return build_error_response(
            'The settings field `map_by` must contain '
            '`input_column` and `attachment_column` fields in it.',
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
