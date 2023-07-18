# -*- coding: utf-8 -*-
#
# Copyright (c) 2023, CloudBlue LLC
# All rights reserved.
#
import re
from collections import defaultdict

import jq
from fastapi.responses import JSONResponse

from connect_transformations.utils import (
    _cast_mapping,
    build_error_response,
    does_not_contain_required_keys,
    has_invalid_basic_structure,
)


JQ_FIELDS_REGEX = re.compile(r'(\.([a-z_][a-z0-9_]*))|(\."(.+?)")|(\.\["(.+?)"\])', re.I)
DROP_REGEX = re.compile(r'(?<![."])drop_row(?![."])', re.I)
COL_ID_REGEX = re.compile(r'\."([^"]+) \(C\d{3,4}\)"')


def validate_formula(data):  # noqa: CCR001
    data = data.dict(by_alias=True)

    if (
        has_invalid_basic_structure(data)
        or does_not_contain_required_keys(data['columns'], ['output'])
    ):
        print('error')
        return build_error_response('Invalid input data')

    if (
        does_not_contain_required_keys(data['settings'], ['expressions'])
        or not isinstance(data['settings']['expressions'], list)
    ):
        return build_error_response(
            'The settings must have `expressions` field which contains list of formulas.',
        )

    for expression in data['settings']['expressions']:
        if (
            does_not_contain_required_keys(
                expression,
                ['to', 'formula', 'type', 'ignore_errors'],
            ) or not isinstance(expression['to'], str)
            or not isinstance(expression['formula'], str)
            or expression['type'] not in _cast_mapping.keys()
            or not isinstance(expression['ignore_errors'], bool)
        ):
            return build_error_response(
                'Each expression must have not empty `to`, `formula`, `type` '
                'and `ignore_errors` fields.',
            )

    output_columns = []
    column_converter = get_expression_column_converter(data['columns']['input'])

    for expression in data['settings']['expressions']:
        if expression['to'] in output_columns:
            return build_error_response('Each `output column` must be unique.')

        for match in JQ_FIELDS_REGEX.findall(expression['formula']):
            var_name = match[1] or match[3] or match[5]
            var = column_converter(var_name)
            if not var:
                return build_error_response(
                    (
                        f'Settings contains formula `{expression["formula"]}` '
                        f'with column `{var_name}` that does not exist on columns.input.'
                    ),
                )
        try:
            formula = expression['formula']
            if DROP_REGEX.findall(formula):
                formula = f'def drop_row: "#DROP_ROW"; {formula}'
            jq.compile(formula)
        except ValueError as e:
            return build_error_response(
                f'Settings contains invalid formula `{expression["formula"]}: {str(e)}`.',
            )

        output_columns.append(expression['to'])

    overview = ''
    for expression in data['settings']['expressions']:
        overview += f'{expression["to"]} = {expression["formula"]}\n'

    return {'overview': overview}


def extract_input(data):
    if 'expressions' not in data or not isinstance(data['expressions'], list):
        return JSONResponse(
            status_code=400,
            content={
                'error': 'The body does not contain `expressions` list',
            },
        )
    if 'columns' not in data or not isinstance(data['columns'], list):
        return JSONResponse(
            status_code=400,
            content={
                'error': 'The body does not contain `columns` list',
            },
        )

    input_columns = []
    added_columns = {}

    column_converter = get_expression_column_converter(data['columns'])

    for expression in data['expressions']:
        for match in JQ_FIELDS_REGEX.findall(expression['formula']):
            col_value = match[1] or match[3] or match[5]
            col = column_converter(col_value)
            if not col:
                return JSONResponse(
                    status_code=400,
                    content={
                        'error': f'{col_value} not found in input columns',
                    },
                )

            if col['name'] not in added_columns:
                input_columns.append(col)
                added_columns[col['name']] = col['id']

    return input_columns


def get_expression_column_converter(columns):
    cols_by_name = defaultdict(list)
    cols_by_id = {}

    for column in columns:
        id_suffix = column['id'].split('-')[-1]
        cols_by_name[column['name']].append(column)
        cols_by_id[f'(C{id_suffix})'] = column

    def converter(col_name):
        if col_name in cols_by_name:
            return cols_by_name[col_name][-1]

        col_name_parts = col_name.split()
        if (
            len(col_name_parts) > 1
            and col_name_parts[-1] in cols_by_id
            and cols_by_id[col_name_parts[-1]]['name'] == ' '.join(col_name_parts[:-1])
        ):
            return cols_by_id[col_name_parts[-1]]

    return converter


def clear_formula(expression):
    return COL_ID_REGEX.sub(r'."\1"', expression)
