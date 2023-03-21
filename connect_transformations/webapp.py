# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
from connect.eaas.core.decorators import router, web_app
from connect.eaas.core.extension import WebApplicationBase
from fastapi.responses import JSONResponse

from connect_transformations.constants import SUBSCRIPTION_LOOKUP


@web_app(router)
class TransformationsWebApplication(WebApplicationBase):

    def validate_copy_columns(self, data):
        if (
            'settings' not in data
            or not type(data['settings']) == list
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
            or not type(data['settings']) == dict
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
