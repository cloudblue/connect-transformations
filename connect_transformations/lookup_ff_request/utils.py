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


ASSET_LOOKUP = {
    'external_id': 'CloudBlue Subscription External ID',
    'id': 'CloudBlue Subscription ID',
}


NOT_FOUND_CHOICES = ['leave_empty', 'fail']
MULTIPLE_CHOICES = ['leave_empty', 'fail', 'use_most_actual']

FF_REQ_COMMON_FILTERS = {
    'status': 'approved',
}
FF_REQ_SELECT = ['-activation_key', '-template']


def validate_lookup_ff_request(data):  # noqa: CCR001
    data = data.dict(by_alias=True)

    if has_invalid_basic_structure(data):
        return build_error_response('Invalid input data')

    if (
        does_not_contain_required_keys(
            data['settings'],
            [
                'parameter',
                'parameter_column',
                'action_if_not_found',
                'action_if_multiple',
                'output_config',
            ],
        )
    ):
        return build_error_response(
            'The settings must have `parameter`, `parameter_column`, `item`, `item_column`, '
            '`action_if_not_found` and `action_if_multiple` fields',
        )

    values = ASSET_LOOKUP.keys()
    if data['settings'].get('asset_type') and data['settings'].get('asset_type') not in values:
        return build_error_response(
            f'The settings `asset_type` allowed values {", ".join(values)}',
        )

    if data['settings']['action_if_not_found'] not in NOT_FOUND_CHOICES:
        return build_error_response(
            f'The settings `action_if_not_found` allowed values {", ".join(NOT_FOUND_CHOICES)}',
        )

    if data['settings']['action_if_multiple'] not in MULTIPLE_CHOICES:
        return build_error_response(
            f'The settings `action_if_multiple` allowed values {", ".join(MULTIPLE_CHOICES)}',
        )

    if (
        does_not_contain_required_keys(data['settings'], ['parameter'])
        or not isinstance(data['settings']['parameter'], dict)
        or does_not_contain_required_keys(data['settings']['parameter'], ['id', 'name'])
    ):
        return build_error_response('The settings must have `parameter` with `id` and `name`')

    if (
        does_not_contain_required_keys(data['settings'], ['item'])
        or not isinstance(data['settings']['item'], dict)
        or does_not_contain_required_keys(data['settings']['item'], ['id', 'name'])
    ):
        return build_error_response('The settings must have `item` with `id` and `name`')

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    columns_names = [data['settings']['parameter_column'], data['settings']['item_column']]
    if data['settings'].get('asset_column'):
        columns_names.append(data['settings']['asset_column'])
    for column_name in columns_names:
        if column_name not in available_input_columns:
            return build_error_response(
                f'The settings contains an invalid column name {column_name}'
                ' that does not exist on columns.input',
            )

    output_columns = data['columns']['output']
    output_columns_config = data['settings']['output_config']

    for out_column in output_columns:
        column_name = out_column['name']
        column_config = output_columns_config.get(column_name)
        if not column_config:
            return build_error_response(
                'The settings `output_config` does not contain '
                f'settings for the column {column_name}.',
            )

    overview = 'Match by parameter "' + data['settings']['parameter']['name'] + '"\n'
    if data['settings'].get('asset_type'):
        overview += 'And "' + ASSET_LOOKUP[data['settings']['asset_type']] + '"\n'
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

    total = len(data["columns"]["output"])
    overview += f'And populate {total} column{"s" if total > 1 else ""}'

    return {
        'overview': overview,
    }


def filter_requests_with_changes(requests):
    """ FF requests without any changes can be produced during synchronization.
        Exclude them.
    """
    filtered_requests = []
    for request in requests:
        changed = False
        for item_data in request['asset']['items']:
            if item_data['quantity'] != item_data['old_quantity']:
                changed = True
                break
        if changed:
            filtered_requests.append(request)

    if not filtered_requests:
        return requests[0]

    return filtered_requests
