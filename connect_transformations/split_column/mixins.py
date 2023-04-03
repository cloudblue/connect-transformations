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
            'This transformation function allows you to split "compoud" values stored in a certain '
            'column into individual columns using regular expressions.'
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
        match = re.match(pattern, row_value)

        for element in groups:
            key = list(element.keys())[0]
            value = element[key]
            result[value] = match.group(key) if match else None

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
        if 'groups' in data and not isinstance(data['groups'], list):
            return JSONResponse(
                status_code=400,
                content={
                    'error': 'The `groups` key must be a valid list',
                },
            )
        try:
            pattern = re.compile(data['pattern'])
            new_groups = [{key: key} for key in dict(pattern.groupindex).keys()]
            merge_groups(new_groups, data.get('groups', None))
            return {'groups': new_groups}
        except re.error:
            return JSONResponse(
                status_code=400,
                content={
                    'error': 'Invalid regular expression',
                },
            )
