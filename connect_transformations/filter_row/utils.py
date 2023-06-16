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


def validate_filter_row(data):
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data):
        return build_error_response('Invalid input data')

    settings = data['settings']

    if (
        does_not_contain_required_keys(
            settings,
            ['from', 'value', 'match_condition', 'additional_values'],
        ) or not isinstance(settings['value'], str)
        or not isinstance(settings['match_condition'], bool)
        or not isinstance(settings['additional_values'], list)
    ):
        return build_error_response(
            'The settings must have `from`, `value`, boolean `match_condition` '
            'and list `additional_values` fields',
        )

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    if settings['from'] not in available_input_columns:
        return build_error_response(
            'The settings must have a valid `from` column name',
        )

    for condition in settings['additional_values']:
        if (
            'value' not in condition
            or not condition['value']
            or not isinstance(condition['value'], str)
        ):
            return build_error_response(
                'Each additional value in the settings must have '
                'not empty `value` field and `operation` field '
                'equal to `or` or `and`',
            )

    value = f'"{settings["value"]}"'
    for condition in settings['additional_values']:
        value += f' {"OR" if settings["match_condition"] else "AND"} "{condition["value"]}"'

    return {
        'overview': (
            f'We Keep Row If Value of column "{settings["from"]}" '
            f'{"==" if settings["match_condition"] else "!="} {value}'
        ),
    }
