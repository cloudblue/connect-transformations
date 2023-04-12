# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from fastapi.responses import JSONResponse

from connect_transformations.constants import SUBSCRIPTION_LOOKUP
from connect_transformations.exceptions import SubscriptionLookupError


async def retrieve_subscription(client, cache, cache_lock, lookup, leave_empty):
    result = None

    k = ''
    for key, value in lookup.items():
        k = k + f'{key}-{value}'
    try:
        result = cache[k]
    except KeyError:
        pass

    if not result:
        results = await client('subscriptions').assets.filter(**lookup).count()
        if results == 0:
            if leave_empty:
                return result
            raise SubscriptionLookupError(f'No result found for the filter {lookup}')
        elif results > 1:
            raise SubscriptionLookupError(f'Many results found for the filter {lookup}')
        else:
            result = await client(
                'subscriptions',
            ).assets.filter(
                **lookup,
            ).first()
            async with cache_lock:
                cache[k] = result

    return result


def validate_lookup_subscription(data):
    if (
        'settings' not in data
        or not isinstance(data['settings'], dict)
        or 'columns' not in data
        or 'input' not in data['columns']
    ):
        return JSONResponse(status_code=400, content={'error': 'Invalid input data'})

    if (
        'lookup_type' not in data['settings']
        or 'from' not in data['settings']
        or 'prefix' not in data['settings']
        or not isinstance(data['settings']['prefix'], str)
        or data['settings']['prefix'] == ''
        or 'action_if_not_found' not in data['settings']
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must have `lookup_type`, `from`, `prefix` and '
                    '`action_if_not_found` fields'
                ),
            },
        )

    values = SUBSCRIPTION_LOOKUP.keys()
    if data['settings']['lookup_type'] not in values:
        return JSONResponse(
            status_code=400,
            content={'error': f'The settings `lookup_type` allowed values {values}'},
        )

    values = ['leave_empty', 'fail']
    if data['settings']['action_if_not_found'] not in values:
        return JSONResponse(
            status_code=400,
            content={
                'error': f'The settings `action_if_not_found` allowed values {values}',
            },
        )

    if (
        data['settings']['lookup_type'] == 'params__value' and (
            'parameter' not in data['settings']
            or not isinstance(data['settings']['parameter'], dict)
            or 'id' not in data['settings']['parameter']
            or 'name' not in data['settings']['parameter']
        )
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings must have `parameter` with `id` and `name` if `lookup_type`'
                    ' is params__value'
                ),
            },
        )

    input_columns = data['columns']['input']
    available_input_columns = [c['name'] for c in input_columns]
    column_name = data['settings']['from']
    if column_name not in available_input_columns:
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    f'The settings `from` contains an invalid column name {column_name}'
                    ' that does not exist on columns.input'
                ),
            },
        )

    if len(data['settings']['prefix']) > 10:
        return JSONResponse(
            status_code=400,
            content={
                'error': (
                    'The settings `prefix` max length is 10'
                ),
            },
        )

    overview = 'Criteria = "' + SUBSCRIPTION_LOOKUP[data['settings']['lookup_type']] + '"\n'
    if data['settings']['lookup_type'] == 'params__value':
        overview += 'Parameter Name = "' + data['settings']['parameter']['name'] + '"\n'
    overview += 'Prefix = "' + data['settings']['prefix'] + '"\n'
    overview += (
        'If not found = '
        + data['settings']['action_if_not_found'].replace('_', ' ').title()
        + '\n'
    )

    return {
        'overview': overview,
    }
