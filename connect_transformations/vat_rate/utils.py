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


def validate_vat_rate(data):
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data):
        return build_error_response('Invalid input data')

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    if does_not_contain_required_keys(
        data['settings'],
        ['from', 'to', 'action_if_not_found'],
    ):
        return build_error_response(
            'The settings must have `from`, `to` and `action_if_not_found` '
            'fields',
        )

    if data['settings']['from'] not in available_input_columns:
        return build_error_response(
            'The settings contains an invalid `from` column name'
            f' "{data["settings"]["from"]}" that does not exist on '
            'columns.input',
        )

    return {
        'overview': (
            'What to do for non-EU country codes = '
            + data['settings']['action_if_not_found'].replace('_', ' ').title()
            + '\n'
        ),
    }
