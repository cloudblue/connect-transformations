# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect_transformations.utils import (
    build_error_response,
    does_not_contain_required_keys,
    has_invalid_basic_structure,
)


def validate_copy_columns(data):
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data, list):
        return build_error_response('Invalid input data')

    settings = data['settings']
    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    unique_names = [c['name'] for c in input_columns]
    overview = []

    for setting in settings:
        if does_not_contain_required_keys(setting, ['from', 'to']):
            return build_error_response('Invalid settings format')
        if setting['from'] not in available_input_columns:
            return build_error_response(
                f'The input column {setting["from"]} does not exists',
            )
        if setting['to'] in unique_names:
            return build_error_response(
                f'Invalid column name {setting["to"]}. The to field should be unique',
            )

        unique_names.append(setting['to'])
        overview.append(f'{setting["from"]} \u2192 {setting["to"]}')

    overview = ''.join([row + '\n' for row in overview])

    return {
        'overview': overview,
    }
