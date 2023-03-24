# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re

import httpx
from connect.eaas.core.decorators import router, web_app
from connect.eaas.core.extension import WebApplicationBase
from fastapi.responses import JSONResponse

from connect_transformations.constants import SUBSCRIPTION_LOOKUP


@web_app(router)
class TransformationsWebApplication(WebApplicationBase):

    def validate_copy_columns(self, data):
        if (
            'settings' not in data
            or not isinstance(data['settings'], list)
            or 'columns' not in data
            or 'input' not in data['columns']
        ):
            return JSONResponse(status_code=400, content={'error': 'Invalid input data'})

        settings = data['settings']
        input_columns = data['columns']['input']
        available_input_columns = [c['name'] for c in input_columns]
        unique_names = [c['name'] for c in input_columns]
        overview = []

        for s in settings:
            if 'from' not in s or 'to' not in s:
                return JSONResponse(
                    status_code=400,
                    content={'error': 'Invalid settings format'},
                )
            if s['from'] not in available_input_columns:
                return JSONResponse(
                    status_code=400,
                    content={'error': f'The input column {s["from"]} does not exists'},
                )
            if s['to'] in unique_names:
                return JSONResponse(
                    status_code=400,
                    content={
                        'error': f'Invalid column name {s["to"]}. The to field should be unique',
                    },
                )
            unique_names.append(s['to'])
            overview.append(f'{s["from"]}  -->  {s["to"]}')

        overview = ''.join([row + '\n' for row in overview])

        return {
            'overview': overview,
        }

    def validate_lookup_subscription(self, data):
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

    def validate_currency_conversion(self, data):
        if (
            'settings' not in data
            or not isinstance(data['settings'], dict)
            or 'columns' not in data
            or 'input' not in data['columns']
        ):
            return JSONResponse(status_code=400, content={'error': 'Invalid input data'})

        input_columns = data['columns']['input']
        available_input_columns = [c['name'] for c in input_columns]
        if (
            'from' not in data['settings']
            or 'column' not in data['settings']['from']
            or 'currency' not in data['settings']['from']
            or 'to' not in data['settings']
            or 'column' not in data['settings']['to']
            or 'currency' not in data['settings']['to']
        ):
            return JSONResponse(
                status_code=400,
                content={
                    'error': (
                        'The settings must have `from` with the `column` and the `currency`, and '
                        '`to` with the `column` and `currency` fields'
                    ),
                },
            )

        if data['settings']['from']['column'] not in available_input_columns:
            return JSONResponse(
                status_code=400,
                content={
                    'error': (
                        'The settings contains an invalid `from` column name'
                        f' "{data["settings"]["from"]["column"]}" that does not exist on '
                        'columns.input'
                    ),
                },
            )

        overview = 'From Currency = ' + data['settings']['from']['currency'] + '\n'
        overview += 'To Currency = ' + data['settings']['to']['currency'] + '\n'

        return {
            'overview': overview,
        }

    def validate_split_column(self, data):
        if (
            'settings' not in data
            or not isinstance(data['settings'], dict)
            or 'columns' not in data
            or 'input' not in data['columns']
        ):
            return JSONResponse(status_code=400, content={'error': 'Invalid input data'})

        if (
            'from' not in data['settings']
            or 'regex' not in data['settings']
            or 'pattern' not in data['settings']['regex']
            or not isinstance(data['settings']['regex']['pattern'], str)
            or 'groups' not in data['settings']['regex']
            or not isinstance(data['settings']['regex']['groups'], dict)
            or 'order' not in data['settings']['regex']
            or not isinstance(data['settings']['regex']['order'], list)
        ):
            return JSONResponse(
                status_code=400,
                content={
                    'error': (
                        'The settings must have `from` and `regex` with `pattern`, `groups` and '
                        '`order` fields'
                    ),
                },
            )

        input_columns = data['columns']['input']
        available_input_columns = [c['name'] for c in input_columns]
        if data['settings']['from'] not in available_input_columns:
            return JSONResponse(
                status_code=400,
                content={
                    'error': (
                        'The settings contains an invalid `from` column name'
                        f' "{data["settings"]["from"]}" that does not exist on '
                        'columns.input'
                    ),
                },
            )

        pattern = None
        try:
            pattern = re.compile(data['settings']['regex']['pattern'])
        except re.error:
            return JSONResponse(
                status_code=400,
                content={
                    'error': (
                        'The settings contains an invalid `regex` regular expression '
                        f"{data['settings']['regex']['pattern']}"
                    ),
                },
            )

        extracted_groups = dict(pattern.groupindex).keys()
        for key in data['settings']['regex']['groups'].keys():
            if key not in extracted_groups:
                return JSONResponse(
                    status_code=400,
                    content={
                        'error': (
                            f'The settings `groups` contains a group name <{key}> that does not '
                            'exists on `pattern` regular expression '
                            f"{data['settings']['regex']['pattern']}"
                        ),
                    },
                )

        return {
            'overview': "Regexp = '" + data['settings']['regex']['pattern'] + "'",
        }

    @router.post(
        '/validate/{transformation_function}',
        summary='Validate settings',
    )
    def validate_tfn_settings(
        self,
        transformation_function: str,
        data: dict,
    ):
        try:
            method = getattr(self, f'validate_{transformation_function}')
            return method(data)
        except AttributeError:
            return JSONResponse(
                status_code=400,
                content={
                    'error': f'The validation method {transformation_function} does not exist',
                },
            )

    @router.get(
        '/lookup_subscription/criteria',
        summary='Return the subscription criteria options.',
    )
    def get_subscription_criteria(
        self,
    ):
        return SUBSCRIPTION_LOOKUP

    @router.get(
        '/currency_conversion/currencies',
        summary='List available exchange rates',
        response_model=dict,
    )
    async def get_available_rates(self):
        try:
            url = 'https://api.exchangerate.host/symbols'
            async with httpx.AsyncClient(
                transport=httpx.AsyncHTTPTransport(retries=3),
            ) as client:
                response = await client.get(url)
            data = response.json()
            if response.status_code != 200 or not data['success']:
                return {}
            currencies = {}
            for key in data['symbols'].keys():
                element = data['symbols'][key]
                currencies[element['code']] = element['description']
            return currencies
        except Exception:
            return {}

    def _merge_groups(self, new_groups, new_order, past_groups):
        if not past_groups:
            return {'groups': new_groups, 'order': new_order}
        groups = {}
        for key in new_order:
            groups[key] = past_groups.get(key, new_groups[key])
        return {'groups': groups, 'order': new_order}

    @router.post(
        '/split_column/extract_groups',
        summary='Get group names and order for a given regular expression',
        response_model=dict,
    )
    async def get_groups(self, data: dict):
        if 'pattern' not in data:
            return JSONResponse(
                status_code=400,
                content={
                    'error': 'The body does not contain `pattern` key',
                },
            )
        if 'groups' in data and type(data['groups']) != dict:
            return JSONResponse(
                status_code=400,
                content={
                    'error': 'The `groups` key must be a valid dict',
                },
            )
        try:
            pattern = re.compile(data['pattern'])
            new_order = list(dict(pattern.groupindex).keys())
            new_groups = {key: key for key in dict(pattern.groupindex).keys()}
            return self._merge_groups(new_groups, new_order, data.get('groups', None))
        except re.error:
            return JSONResponse(
                status_code=400,
                content={
                    'error': 'Invalid regular expression',
                },
            )
