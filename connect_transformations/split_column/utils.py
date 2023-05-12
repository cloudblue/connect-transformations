# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re

from connect_transformations.utils import (
    build_error_response,
    does_not_contain_required_keys,
    has_invalid_basic_structure,
)


def validate_split_column(data):
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data):
        return build_error_response('Invalid input data')

    if (
        does_not_contain_required_keys(
            data['settings'],
            ['from', 'regex'],
        ) or does_not_contain_required_keys(
            data['settings']['regex'],
            ['pattern', 'groups'],
        ) or not isinstance(data['settings']['regex']['pattern'], str)
        or not isinstance(data['settings']['regex']['groups'], dict)
    ):
        return build_error_response(
            'The settings must have `from` and `regex` with `pattern` and `groups` '
            'fields',
        )

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    if data['settings']['from'] not in available_input_columns:
        return build_error_response(
            'The settings contains an invalid `from` column name'
            f' "{data["settings"]["from"]}" that does not exist on '
            'columns.input',
        )

    pattern = None
    try:
        pattern = re.compile(data['settings']['regex']['pattern'])
    except re.error:
        return build_error_response(
            'The settings contains an invalid `regex` regular expression '
            f"{data['settings']['regex']['pattern']}",
        )

    if pattern.groups != len(data['settings']['regex']['groups']):
        return build_error_response(
            'The settings `groups` contains a different number of elements that are'
            ' defined in the regular expression '
            f"{data['settings']['regex']['pattern']}",
        )

    return {
        'overview': "Regexp = '" + data['settings']['regex']['pattern'] + "'",
    }


def merge_groups(new_groups: dict, past_groups: dict):
    if not past_groups:
        return {'groups': new_groups}
    for key in new_groups.keys():
        if key in past_groups:
            new_groups[key] = past_groups[key]
