# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re

from connect.eaas.core.decorators import router, transformation
from fastapi.responses import JSONResponse

from connect_transformations.split_column.utils import merge_groups, validate_split_column


class SplitColumnTransformationMixin:

    @transformation(
        name='Split Column',
        description=(
            'This transformation function allows you to copy values from Input to Output columns,'
            ' which might be handy if you’d like to change column name in the output data for for'
            ' some other reason create a copy of values in table.'
        ),
        edit_dialog_ui='/static/transformations/split_column.html',
    )
    async def split_column(
        self,
        row,
    ):
        trfn_settings = self.transformation_request['transformation']['settings']
        row_value = row[trfn_settings['from']]
        pattern = trfn_settings['regex']['pattern']
        groups = trfn_settings['regex']['groups']

        result = {}
        match = re.match(pattern, row_value) if row_value else None
        pattern_groups = match.groups() if match else {}

        for key, column_value in groups.items():
            index = int(key) - 1
            value = pattern_groups[index] if len(pattern_groups) > index else None
            result[column_value] = value

        return result


class SplitColumnWebAppMixin:

    @router.post(
        '/validate/split_column',
        summary='Validate split column settings',
    )
    def validate_split_column_settings(
        self,
        data: dict,
    ):
        return validate_split_column(data)

    @router.post(
        '/split_column/extract_groups',
        summary='Get group names for a given regular expression',
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
        if 'groups' in data and not isinstance(data['groups'], dict):
            return JSONResponse(
                status_code=400,
                content={
                    'error': 'The `groups` key must be a valid dict',
                },
            )
        try:
            pattern = re.compile(data['pattern'])
            named_groups = {str(v): k for k, v in dict(pattern.groupindex).items()}
            for n in range(1, pattern.groups + 1):
                n = str(n)
                if n not in named_groups:
                    named_groups[n] = f'group_{n}'
            merge_groups(named_groups, data.get('groups', None))
            return {'groups': named_groups}
        except re.error:
            return JSONResponse(
                status_code=400,
                content={
                    'error': 'Invalid regular expression',
                },
            )
