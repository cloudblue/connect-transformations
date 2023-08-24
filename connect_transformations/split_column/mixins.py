# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re
from functools import cached_property
from typing import Dict

from connect.eaas.core.decorators import router, transformation
from connect.eaas.core.responses import RowTransformationResponse
from fastapi.responses import JSONResponse

from connect_transformations.models import Error, ValidationResult
from connect_transformations.split_column.models import (
    CapturingGroup,
    CapturingGroups,
    Configuration,
)
from connect_transformations.split_column.utils import merge_groups, validate_split_column
from connect_transformations.utils import cast_value_to_type


class SplitColumnTransformationMixin:

    @transformation(
        name='Split columns',
        description=(
            'This transformation function allows you to divide values'
            ' of one column into separate columns, using regular expressions.'
        ),
        edit_dialog_ui='/static/transformations/split_columns.html',
    )
    def split_column(
        self,
        row,
    ):
        trfn_settings = self.transformation_request['transformation']['settings']
        row_value = row[trfn_settings['from']]
        pattern = trfn_settings['regex']['pattern']
        groups = trfn_settings['regex']['groups']

        result = {}
        match = re.match(pattern, str(row_value)) if row_value else None
        pattern_groups = match.groups() if match else {}

        for key, group in groups.items():
            index = int(key) - 1
            column_name = group['name']
            column = self.output_columns[column_name]

            column_type = column.get('type', 'string')
            value = pattern_groups[index] if len(pattern_groups) > index else None
            parameters = {'value': value, 'type': column_type}
            precision = column.get('constraints', {}).get('precision')
            if precision:
                parameters['additional_parameters'] = {'precision': precision}
            cast_value = cast_value_to_type(**parameters)
            result[column_name] = cast_value

        return RowTransformationResponse.done(result)

    @cached_property
    def output_columns(self):
        out_columns = self.transformation_request['transformation']['columns']['output']
        return {c['name']: c for c in out_columns}


class SplitColumnWebAppMixin:

    @router.post(
        '/split_column/validate',
        summary='Validate split column settings',
        response_model=ValidationResult,
        responses={
            400: {'model': Error},
        },
    )
    def validate_split_column_settings(
        self,
        data: Configuration,
    ):
        return validate_split_column(data)

    @router.post(
        '/split_column/extract_groups',
        summary='Get group names for a given regular expression',
        response_model=CapturingGroups,
        responses={
            400: {'model': Error},
        },
    )
    def get_split_column_groups(self, data: Dict):
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
            named_groups = {
                str(v): CapturingGroup(**{'name': k, 'type': 'string'})
                for k, v in dict(pattern.groupindex).items()
            }
            for n in range(1, pattern.groups + 1):
                n = str(n)
                if n not in named_groups:
                    named_groups[n] = CapturingGroup(**{'name': f'group_{n}', 'type': 'string'})
            merge_groups(named_groups, data.get('groups', None))
            return CapturingGroups(**{'groups': named_groups})
        except re.error:
            return JSONResponse(
                status_code=400,
                content={
                    'error': 'Invalid regular expression',
                },
            )
