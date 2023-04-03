# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from fastapi.responses import JSONResponse

from connect_transformations.constants import SUBSCRIPTION_LOOKUP
from connect_transformations.exceptions import SubscriptionLookup


async def retrieve_subscription(client, cache, cache_lock, key, value):
    result = None

    k = f'{key}-{value}'
    try:
        result = cache[k]
    except KeyError:
        pass

    if not result:
        query = {key: value}
        results = await client('subscriptions').assets.filter(**query).count()
        if results == 0:
            raise SubscriptionLookup(f'No result found for the filter {query}')
        elif results > 1:
            raise SubscriptionLookup(f'Many results found for the filter {query}')
        else:
            result = await client(
                'subscriptions',
            ).assets.filter(
                **query,
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
    ):
        return JSONResponse(
            status_code=400,
            content={
                'error': 'The settings must have `lookup_type`, `from` and `prefix` fields',
            },
        )

    values = SUBSCRIPTION_LOOKUP.keys()
    if data['settings']['lookup_type'] not in values:
        return JSONResponse(
            status_code=400,
            content={'error': f'The settings `lookup_type` allowed values {values}'},
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

    overview = 'Criteria = "' + data['settings']['lookup_type'] + '"\n'
    overview += 'Input Column = "' + data['settings']['from'] + '"\n'
    overview += 'Prefix = "' + data['settings']['prefix'] + '"\n'

    return {
        'overview': overview,
    }
