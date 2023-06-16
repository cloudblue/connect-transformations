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


def validate_currency_conversion(data):
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data):
        return build_error_response('Invalid input data')

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    if (
        does_not_contain_required_keys(
            data['settings'],
            ['from', 'to'],
        ) or does_not_contain_required_keys(
            data['settings']['from'],
            ['column', 'currency'],
        ) or does_not_contain_required_keys(
            data['settings']['to'],
            ['column', 'currency'],
        )
    ):
        return build_error_response(
            'The settings must have `from` with the `column` and the `currency`, and '
            '`to` with the `column` and `currency` fields',
        )

    if data['settings']['from']['currency'] == data['settings']['to']['currency']:
        return build_error_response(
            'The settings must have different currencies for `from` and `to`',
        )

    if data['settings']['from']['column'] not in available_input_columns:
        return build_error_response(
            'The settings contains an invalid `from` column name'
            f' "{data["settings"]["from"]["column"]}" that does not exist on '
            'columns.input',
        )

    overview = 'From Currency = ' + data['settings']['from']['currency'] + '\n'
    overview += 'To Currency = ' + data['settings']['to']['currency'] + '\n'

    return {
        'overview': overview,
    }
