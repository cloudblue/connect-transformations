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


PREFIX_MAX_LENGTH = 12

SUBSCRIPTION_LOOKUP = {
    'external_id': 'CloudBlue Subscription External ID',
    'id': 'CloudBlue Subscription ID',
    'params__value': 'Parameter Value',
}


NOT_FOUND_CHOICES = ['leave_empty', 'fail']
MULTIPLE_CHOICES = ['leave_empty', 'fail', 'use_most_actual']


def validate_lookup_subscription(data):
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data):
        return build_error_response('Invalid input data')

    if (
        does_not_contain_required_keys(
            data['settings'],
            ['lookup_type', 'from', 'prefix', 'action_if_not_found', 'action_if_multiple'],
        ) or not isinstance(data['settings']['prefix'], str)
        or data['settings']['prefix'] == ''
    ):
        return build_error_response(
            'The settings must have `lookup_type`, `from`, `prefix`, '
            '`action_if_not_found` and `action_if_multiple` fields',
        )

    values = SUBSCRIPTION_LOOKUP.keys()
    if data['settings']['lookup_type'] not in values:
        return build_error_response(
            f'The settings `lookup_type` allowed values {values}',
        )

    if data['settings']['action_if_not_found'] not in NOT_FOUND_CHOICES:
        return build_error_response(
            f'The settings `action_if_not_found` allowed values {NOT_FOUND_CHOICES}',
        )

    if data['settings']['action_if_multiple'] not in MULTIPLE_CHOICES:
        return build_error_response(
            f'The settings `action_if_multiple` allowed values {MULTIPLE_CHOICES}',
        )

    if (
        data['settings']['lookup_type'] == 'params__value' and (
            does_not_contain_required_keys(data['settings'], ['parameter'])
            or not isinstance(data['settings']['parameter'], dict)
            or does_not_contain_required_keys(data['settings']['parameter'], ['id', 'name'])
        )
    ):
        return build_error_response(
            'The settings must have `parameter` with `id` and `name` if `lookup_type`'
            ' is params__value',
        )

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    column_name = data['settings']['from']
    if column_name not in available_input_columns:
        return build_error_response(
            f'The settings `from` contains an invalid column name {column_name}'
            ' that does not exist on columns.input',
        )

    if len(data['settings']['prefix']) > PREFIX_MAX_LENGTH:
        return build_error_response(
            f'The settings `prefix` max length is {PREFIX_MAX_LENGTH}',
        )

    overview = 'Criteria = "' + SUBSCRIPTION_LOOKUP[data['settings']['lookup_type']] + '"\n'
    if data['settings']['lookup_type'] == 'params__value':
        overview += 'Parameter Name = "' + data['settings']['parameter']['name'] + '"\n'
    overview += 'Prefix = "' + data['settings']['prefix'] + '"\n'
    overview += (
        'If not found = '
        + data['settings']['action_if_not_found'].replace('_', ' ').capitalize()
        + '\n'
    )
    overview += (
        'If multiple found = '
        + data['settings']['action_if_multiple'].replace('_', ' ').capitalize()
        + '\n'
    )

    return {
        'overview': overview,
    }
